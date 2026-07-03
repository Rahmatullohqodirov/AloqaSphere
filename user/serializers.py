from rest_framework import serializers
from rest_framework.authentication import authenticate
from .models import User,Role

class UserSendEmailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields= ["role"]
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    
    def validate(self, data):
        user = authenticate(username = data["email"], password = data["password"])
        if not user:
            raise serializers.ValidationError("gmail yoki password xato")
        data["user"] = user
        return data
    
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
        

        