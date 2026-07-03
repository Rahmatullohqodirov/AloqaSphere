from rest_framework import serializers

from subjects.models import Subject
from .models import Conversation, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("id", "role", "content", "created_at")


class ConversationSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = (
            "id", "subject", "subject_code", "session_type", "target_level",
            "started_at", "ended_at", "is_active",
            "grammar_accuracy", "suggested_level", "summary_notes",
            "total_questions", "correct_answers", "learning_session",
            "messages",
        )
        read_only_fields = (
            "id", "started_at", "ended_at", "is_active", "grammar_accuracy",
            "suggested_level", "summary_notes", "total_questions",
            "correct_answers", "learning_session",
        )


class StartConversationSerializer(serializers.Serializer):
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.filter(is_active=True)
    )
    session_type = serializers.ChoiceField(
        choices=Conversation.SessionType.choices,
        default=Conversation.SessionType.CONVERSATION,
    )
    target_level = serializers.CharField(required=False, allow_blank=True, default="")


class SendMessageSerializer(serializers.Serializer):
    text = serializers.CharField(allow_blank=False, max_length=2000)


class MathSolveSerializer(serializers.Serializer):
    problem_text = serializers.CharField(allow_blank=False, max_length=2000)
    level = serializers.CharField(required=False, allow_blank=True, default="")
