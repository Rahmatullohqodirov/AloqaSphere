# SuperTutor AI — Ta'lim platformasi backendi (Django REST Framework)

Bu loyiha TZ hujjatidagi **"Ta'lim platformasi"** (SuperTutor AI) qismining backend
qismini Django + DRF asosida amalga oshiradi. TZda backend FastAPI deb yozilgan edi,
lekin so'rovga ko'ra Django REST Framework asosida qurildi (Rahmatillo odatda DRF bilan ishlaydi).

Diqqat: Avatar, STT (Whisper), TTS, LLM suhbat mantig'i (MuseTalk, Llama va h.k.) — bular
alohida AI/ML mikroservis bo'lishi kerak (Python + PyTorch/FastAPI), chunki ular og'ir
GPU hisoblashlarni talab qiladi. Bu Django backend esa **foydalanuvchilar, fanlar,
sessiyalar va statistika** (TZ 3.1) — ya'ni platformaning "miyasi" hisoblanadi.
AI mikroservis har bir suhbat/mashq tugagach `/api/learning/sessions/` ga natijani yozadi.

## Loyiha strukturasi

```
supertutor_backend/
├── config/            # Django sozlamalari, asosiy urls.py
├── accounts/          # Custom User, ro'yxatdan o'tish, JWT login, profil
├── subjects/          # Fanlar (Ingliz, Rus, Nemis, Turk, Matematika) + CEFR darajalar
├── learning/          # LearningSession, UserSubjectProgress, DailyActivity + streak logikasi
├── statistics_app/    # Dashboard, Heatmap, Weekly report, Leaderboard API'lari
├── ai_tutor/          # AI o'qituvchi: suhbat, baholash, matematika yechimi (OpenAI/Grok)
├── requirements.txt
├── .env.example
└── manage.py
```

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate        # Windowsda: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # va OPENAI_API_KEY ni to'ldiring
python manage.py migrate
python manage.py seed_subjects   # 5 ta fan va darajalarni bazaga yuklaydi
python manage.py createsuperuser # admin panel uchun
python manage.py runserver
```

AI ishlashi uchun `.env` faylida `OPENAI_API_KEY` bo'lishi shart. Kalit bo'lmasa
ilova qulamaydi — AI endpointlari aniq `503` xato xabari bilan javob beradi
("AI xizmati sozlanmagan..."), qolgan barcha funksiyalar (auth, statistika va h.k.)
odatdagidek ishlayveradi.

## API endpointlari

### Autentifikatsiya (`/api/auth/`)
| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/auth/register/` | Ro'yxatdan o'tish |
| POST | `/api/auth/login/` | JWT access/refresh token olish |
| POST | `/api/auth/login/refresh/` | Access tokenni yangilash |
| GET/PATCH | `/api/auth/profile/` | Profil (til, avatar, bio) |

### Fanlar (`/api/subjects/`)
| Method | URL | Tavsif |
|---|---|---|
| GET | `/api/subjects/` | Barcha fanlar (Ingliz, Rus, Nemis, Turk, Matematika) + darajalar |
| GET | `/api/subjects/{id}/` | Bitta fan tafsiloti |

### O'quv sessiyalari (`/api/learning/`)
| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/learning/sessions/` | Yangi sessiya yozish (AI mikroservis tugagach chaqiradi) |
| GET | `/api/learning/sessions/` | Sessiyalar tarixi (`?subject=1` bilan filtrlash) |
| GET | `/api/learning/progress/` | Har bir fan bo'yicha agregatsiya qilingan progress |

### Statistika (`/api/stats/`) — TZ 3.1 ning asosiy qismi
| Method | URL | Tavsif |
|---|---|---|
| GET | `/api/stats/dashboard/` | Umumiy soat, sessiya soni, streak, har fan bo'yicha progress |
| GET | `/api/stats/heatmap/?days=90` | Kunlik faollik xaritasi |
| GET | `/api/stats/weekly-report/` | Joriy va o'tgan hafta taqqoslash (+%) |
| GET | `/api/stats/leaderboard/?subject=english` | Global anonim reyting |

### AI o'qituvchi (`/api/ai/`) — TZ 3.2 / 4-bo'lim
| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/ai/conversations/start/` | Yangi AI suhbat boshlash (`subject`, `session_type`, ixtiyoriy `target_level`) |
| POST | `/api/ai/conversations/{id}/message/` | Xabar yuborish, AI javobini olish (`{"text": "..."}`) |
| POST | `/api/ai/conversations/{id}/end/` | Suhbatni yakunlash → AI baholaydi → avtomatik `LearningSession` yaratiladi → statistika yangilanadi |
| GET | `/api/ai/conversations/` | Suhbatlar tarixi (`?subject=1`) |
| GET | `/api/ai/conversations/{id}/` | Bitta suhbat + barcha xabarlar |
| POST | `/api/ai/math/solve/` | Matematika masalasini bosqichma-bosqich yechish (`problem_text`, ixtiyoriy `level`) |

**Ishlash mexanizmi:** `start` → bir nechta `message` → `end`. Suhbat yakunlanganda
AI butun dialogni tahlil qilib, grammatika aniqligi va darajani baholaydi, so'ng
natija `learning.LearningSession` sifatida yoziladi — bu esa `learning/signals.py`
orqali progress, streak va heatmapni **avtomatik** yangilaydi (qo'lda hech narsa
qilish shart emas).

## Muhim arxitektura qarori: statistikani avtomatik hisoblash

`learning/signals.py` — har safar `LearningSession` yaratilganda (`post_save` signal)
`learning/services.py` dagi `register_session()` funksiyasi avtomatik ishga tushadi va:

1. `UserSubjectProgress` — jami vaqt, session soni, o'rtacha talaffuz/grammar aniqligini yangilaydi
2. `DailyActivity` — heatmap uchun kunlik yozuvni yangilaydi
3. `User.current_streak_days` — ketma-ket faol kunlar sonini qayta hisoblaydi

Bu yondashuv har safar dashboard so'ralganda og'ir aggregate so'rovlar
ishlatish o'rniga, natijalarni oldindan hisoblab saqlaydi (TZ non-functional
talabi: "Javob vaqti < 1.5 soniya").

## Productionga o'tishda qilinadigan o'zgarishlar

- `config/settings.py` dagi SQLite'ni PostgreSQL bilan almashtirish (misol sozlamalar comment qilingan)
- Redis'ni real-time progress yangilanishi (masalan Celery + Channels) uchun ulash
- `SECRET_KEY`, `DEBUG=False`, `CORS_ALLOW_ALL_ORIGINS=False` ni `.env` orqali sozlash
- AI/Avatar mikroservis bilan bog'lovchi ichki API kalitini qo'shish (hozircha ochiq JWT auth)
