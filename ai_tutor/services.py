"""
AI Tutor xizmati.
TZ 4-bo'lim: "LLM: Llama 3.1 (yoki Mistral) - self-hosted asosiy, Groq / TogetherAI
hybrid fallback bilan". Bu yerda soddalik va barqarorlik uchun har qanday
OpenAI-mos API (OpenAI, Groq, Together AI, self-hosted vLLM) bitta interfeys orqali
ishlatiladi - faqat OPENAI_BASE_URL ni almashtirish kifoya.

Barcha tarmoq xatolari (tarmoq yo'q, API kaliti noto'g'ri, timeout, rate limit)
ushlanadi va foydalanuvchiga tushunarli xabar bilan qaytariladi - view hech qachon
500 Internal Server Error bilan qulamaydi.
"""
import json
import logging

from django.conf import settings
from openai import OpenAI, APIError, APIConnectionError, AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """AI xizmati bilan bog'liq har qanday nosozlik uchun umumiy xato turi."""


# Har bir fan uchun tutor "shaxsiyati". Interfeys tili doim o'zbekcha tushuntirish beradi.
SUBJECT_PERSONAS = {
    "english": (
        "Siz professional ingliz tili o'qituvchisisiz. Foydalanuvchi bilan ingliz tilida "
        "suhbatlashing, lekin xatolarini muloyimlik bilan o'zbek tilida tushuntiring. "
        "Foydalanuvchi darajasiga mos so'z boyligi va grammatika ishlating."
    ),
    "russian": (
        "Siz professional rus tili o'qituvchisisiz. Foydalanuvchi bilan rus tilida "
        "suhbatlashing, xatolarini o'zbek tilida tushuntiring."
    ),
    "german": (
        "Siz professional nemis tili o'qituvchisisiz. Foydalanuvchi bilan nemis tilida "
        "suhbatlashing, xatolarini o'zbek tilida tushuntiring."
    ),
    "turkish": (
        "Siz professional turk tili o'qituvchisisiz. Foydalanuvchi bilan turk tilida "
        "suhbatlashing, xatolarini o'zbek tilida tushuntiring."
    ),
    "math": (
        "Siz sabrli matematika o'qituvchisisiz. Masalalarni bosqichma-bosqich, "
        "o'zbek tilida, oddiy va tushunarli qilib tushuntiring. Har doim yakuniy "
        "javobni aniq ko'rsating."
    ),
}

DEFAULT_PERSONA = (
    "Siz do'stona va sabrli AI o'qituvchisiz. Foydalanuvchiga o'zbek tilida yordam bering."
)


def _get_client() -> OpenAI:
    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key:
        raise AIServiceError(
            "AI xizmati sozlanmagan: OPENAI_API_KEY muhit o'zgaruvchisi topilmadi. "
            "Administrator .env faylga API kalitni qo'shishi kerak."
        )
    base_url = getattr(settings, "OPENAI_BASE_URL", None) or None
    return OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)


def _chat_completion(messages, *, json_mode=False):
    """OpenAI-mos API ga so'rov yuborish, barcha xatolarni AIServiceError ga aylantiradi."""
    client = _get_client()
    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 700,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
    except AuthenticationError as exc:
        logger.error("AI auth xatosi: %s", exc)
        raise AIServiceError("AI xizmati kaliti noto'g'ri yoki muddati o'tgan.") from exc
    except RateLimitError as exc:
        logger.warning("AI rate-limit: %s", exc)
        raise AIServiceError("AI xizmati vaqtincha band, birozdan so'ng qayta urinib ko'ring.") from exc
    except APIConnectionError as exc:
        logger.error("AI ulanish xatosi: %s", exc)
        raise AIServiceError("AI xizmatiga ulanib bo'lmadi. Internet aloqasini tekshiring.") from exc
    except APIError as exc:
        logger.error("AI API xatosi: %s", exc)
        raise AIServiceError("AI xizmatida kutilmagan xatolik yuz berdi.") from exc
    except Exception as exc:  # noqa: BLE001 - qolgan barcha kutilmagan holatlar ham ushlanadi
        logger.exception("AI kutilmagan xato")
        raise AIServiceError("Kutilmagan xatolik yuz berdi, qayta urinib ko'ring.") from exc

    choice = response.choices[0] if response.choices else None
    if choice is None or not choice.message or not choice.message.content:
        raise AIServiceError("AI bo'sh javob qaytardi.")
    return choice.message.content


def _build_system_prompt(conversation) -> str:
    persona = SUBJECT_PERSONAS.get(conversation.subject.code, DEFAULT_PERSONA)
    level_hint = (
        f" Foydalanuvchining joriy darajasi: {conversation.target_level}."
        if conversation.target_level else
        " Foydalanuvchining darajasini suhbat davomida aniqlang."
    )
    return persona + level_hint + " Javoblaringiz qisqa va tabiiy bo'lsin (2-4 gap)."


def send_chat_message(conversation, user_text: str) -> str:
    """
    Foydalanuvchi xabarini AI ga yuboradi va javobni qaytaradi.
    Chaqiruvchi (view) javobni ChatMessage sifatida saqlaydi.
    """
    history_qs = conversation.messages.order_by("created_at")
    messages = [{"role": "system", "content": _build_system_prompt(conversation)}]
    for msg in history_qs:
        if msg.role in ("user", "assistant"):
            messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_text})

    return _chat_completion(messages)


def generate_session_feedback(conversation) -> dict:
    """
    Suhbat yakunlangach, AI dan butun dialog bo'yicha JSON formatdagi baholash so'raydi.
    Natija: grammar_accuracy, suggested_level, summary_notes, total_questions, correct_answers.
    Har qanday parsing xatosida ham xavfsiz standart qiymatlar qaytariladi (xatosiz ishlash uchun).
    """
    transcript = "\n".join(
        f"{m.get_role_display()}: {m.content}" for m in conversation.messages.order_by("created_at")
    )
    if not transcript.strip():
        return {
            "grammar_accuracy": None,
            "suggested_level": conversation.target_level,
            "summary_notes": "Suhbatda xabarlar bo'lmadi.",
            "total_questions": 0,
            "correct_answers": 0,
        }

    instruction = (
        "Quyida foydalanuvchi va AI o'qituvchi o'rtasidagi suhbat matni berilgan. "
        "Faqat quyidagi kalitlarga ega JSON obyekt bilan javob bering, boshqa hech narsa yozmang:\n"
        '{"grammar_accuracy": 0-100 son yoki null (agar baholab bo\'lmasa), '
        '"suggested_level": "A1..C2 yoki Beginner..Advanced", '
        '"summary_notes": "o\'zbek tilida 1-2 gaplik qisqa xulosa", '
        '"total_questions": son, "correct_answers": son}'
    )
    messages = [
        {"role": "system", "content": "Siz til/matematika ta'limi baholovchisiz. Faqat JSON qaytaring."},
        {"role": "user", "content": f"{instruction}\n\nSuhbat:\n{transcript}"},
    ]

    try:
        raw = _chat_completion(messages, json_mode=True)
        data = json.loads(raw)
    except AIServiceError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("AI feedback JSON parse xatosi: %s", exc)
        # AI JSON qaytarmasa ham dastur qulamaydi - xavfsiz standart qiymat
        return {
            "grammar_accuracy": None,
            "suggested_level": conversation.target_level,
            "summary_notes": "AI baholashni tahlil qilib bo'lmadi.",
            "total_questions": 0,
            "correct_answers": 0,
        }

    return {
        "grammar_accuracy": data.get("grammar_accuracy"),
        "suggested_level": data.get("suggested_level") or conversation.target_level,
        "summary_notes": data.get("summary_notes", ""),
        "total_questions": int(data.get("total_questions") or 0),
        "correct_answers": int(data.get("correct_answers") or 0),
    }


def solve_math_problem(problem_text: str, level: str = "") -> str:
    """TZ 3.3: Matematika - bosqichma-bosqich yechim (SymPy o'rniga/qo'shimcha AI tushuntirish)."""
    level_hint = f" Foydalanuvchi darajasi: {level}." if level else ""
    messages = [
        {"role": "system", "content": SUBJECT_PERSONAS["math"] + level_hint},
        {"role": "user", "content": f"Quyidagi masalani bosqichma-bosqich yeching:\n{problem_text}"},
    ]
    return _chat_completion(messages)
