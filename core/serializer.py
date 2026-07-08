from rest_framework import serializers

class ScoreUpInputSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="Foydalanuvchining ID raqami")
    points_earned = serializers.IntegerField(help_text="Qo'shiladigan ball miqdori")

class ScoreUpOutputSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    new_score = serializers.IntegerField()