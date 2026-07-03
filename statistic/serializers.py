from user.models import User,Role
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","first_name","last_name","email","address","phone_number"]
        
class RoleSerializer(serializers.ModelSerializer):
    number_of_staff = serializers.IntegerField(read_only=True)
    staff = UserSerializer(read_only=True,source = "role",many=True)
    class Meta:
        model = Role
        fields = ["id","name","created_at","updated_at","number_of_staff","staff"]