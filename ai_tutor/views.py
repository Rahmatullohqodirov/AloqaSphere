from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from learning.models import LearningSession
from .models import Conversation, ChatMessage
from .serializers import (
    ConversationSerializer, StartConversationSerializer,
    SendMessageSerializer, MathSolveSerializer,
)
from .services import (
    send_chat_message, generate_session_feedback, solve_math_problem, AIServiceError,
)


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Conversation.objects.filter(user=self.request.user).select_related("subject")
        subject_id = self.request.query_params.get("subject")
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).prefetch_related("messages")


class StartConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StartConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_level = serializer.validated_data.get("target_level", "")
        subject = serializer.validated_data["subject"]
        if not target_level:
            from learning.models import UserSubjectProgress
            progress = UserSubjectProgress.objects.filter(
                user=request.user, subject=subject
            ).first()
            target_level = progress.current_level if progress else ""

        conversation = Conversation.objects.create(
            user=request.user,
            subject=subject,
            session_type=serializer.validated_data["session_type"],
            target_level=target_level,
        )
        return Response(
            ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED
        )


class SendMessageView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        conversation = _get_active_conversation_or_404(request.user, pk)
        if conversation is None:
            return Response(
                {"detail": "Faol suhbat topilmadi yoki allaqachon yakunlangan."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_text = serializer.validated_data["text"]

        try:
            ai_reply = send_chat_message(conversation, user_text)
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        ChatMessage.objects.create(conversation=conversation, role=ChatMessage.Role.USER, content=user_text)
        ai_message = ChatMessage.objects.create(
            conversation=conversation, role=ChatMessage.Role.ASSISTANT, content=ai_reply
        )
        return Response(
            {"reply": ai_message.content, "message_id": ai_message.id},
            status=status.HTTP_200_OK,
        )


class EndConversationView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        conversation = _get_active_conversation_or_404(request.user, pk)
        if conversation is None:
            return Response(
                {"detail": "Faol suhbat topilmadi yoki allaqachon yakunlangan."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            feedback = generate_session_feedback(conversation)
        except AIServiceError as exc:
            feedback = {
                "grammar_accuracy": None,
                "suggested_level": conversation.target_level,
                "summary_notes": f"AI baholay olmadi: {exc}",
                "total_questions": 0,
                "correct_answers": 0,
            }

        now = timezone.now()
        duration_minutes = max(1, int((now - conversation.started_at).total_seconds() // 60))

        learning_session = LearningSession.objects.create(
            user=request.user,
            subject=conversation.subject,
            session_type=conversation.session_type,
            started_at=conversation.started_at,
            ended_at=now,
            duration_minutes=duration_minutes,
            grammar_accuracy=feedback["grammar_accuracy"],
            level_at_session=feedback["suggested_level"] or "",
            total_questions=feedback["total_questions"],
            correct_answers=feedback["correct_answers"],
            notes=feedback["summary_notes"],
        )

        conversation.ended_at = now
        conversation.is_active = False
        conversation.grammar_accuracy = feedback["grammar_accuracy"]
        conversation.suggested_level = feedback["suggested_level"] or ""
        conversation.summary_notes = feedback["summary_notes"]
        conversation.total_questions = feedback["total_questions"]
        conversation.correct_answers = feedback["correct_answers"]
        conversation.learning_session = learning_session
        conversation.save()

        return Response(ConversationSerializer(conversation).data, status=status.HTTP_200_OK)


class MathSolveView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MathSolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            solution = solve_math_problem(
                serializer.validated_data["problem_text"],
                serializer.validated_data.get("level", ""),
            )
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({"solution": solution}, status=status.HTTP_200_OK)


def _get_active_conversation_or_404(user, pk):
    return Conversation.objects.filter(user=user, pk=pk, is_active=True).first()
