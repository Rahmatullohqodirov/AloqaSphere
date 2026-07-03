from rest_framework import serializers

from .models import Subject, SubjectLevel


class SubjectLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectLevel
        fields = ("id", "code", "order")


class SubjectSerializer(serializers.ModelSerializer):
    levels = SubjectLevelSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ("id", "code", "display_name", "is_language", "icon", "levels")
