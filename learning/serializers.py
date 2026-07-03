from rest_framework import serializers

from .models import LearningSession, UserSubjectProgress, DailyActivity


class LearningSessionSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    accuracy_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = LearningSession
        fields = (
            "id", "subject", "subject_code", "session_type",
            "started_at", "ended_at", "duration_minutes",
            "pronunciation_accuracy", "grammar_accuracy", "level_at_session",
            "total_questions", "correct_answers", "accuracy_percent",
            "notes", "created_at",
        )
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, attrs):
        if attrs["ended_at"] <= attrs["started_at"]:
            raise serializers.ValidationError(
                "ended_at started_at dan katta bo'lishi kerak."
            )
        return attrs


class UserSubjectProgressSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    subject_name = serializers.CharField(source="subject.display_name", read_only=True)
    average_session_length = serializers.FloatField(read_only=True)
    correct_answer_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = UserSubjectProgress
        fields = (
            "id", "subject", "subject_code", "subject_name",
            "total_minutes", "sessions_count", "current_level",
            "average_pronunciation", "average_grammar",
            "average_session_length", "correct_answer_rate", "updated_at",
        )


class DailyActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyActivity
        fields = ("date", "minutes_spent", "sessions_count")
