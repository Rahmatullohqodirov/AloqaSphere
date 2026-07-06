from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
import random
from decouple import config
from django.conf import settings
from rest_framework.generics import CreateAPIView,GenericAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .serializers import UserSendEmailSerializer,LoginSerializer,RoleSerializer
from django.core.cache import cache
from rest_framework import status
from .models import User,Role
from rest_framework_simplejwt.tokens import RefreshToken
from .permissons import RolePermissions
from rest_framework.permissions import AllowAny
from .tasks import send_verification_code
class SendEmailView(CreateAPIView):
    serializer_class = UserSendEmailSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email", request.data.get("email")).lower()
            code = random.randint(100000,999999)
            
            
            cache.set(f"otp_{email}",code,timeout=300)
            cache.set(f"user_data_{email}",serializer.validated_data,timeout=300)
            send_verification_code.delay(email, code)
            return Response({"msg":"kodi junatildi"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class UserSaveView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        input_email = request.data.get("input_email")
        input_code = request.data.get("input_code")

        if not input_email or not input_code:
            return Response({"msg": "email yoki kod kiritilmagan"}, status=status.HTTP_400_BAD_REQUEST)

        input_email = input_email.lower()
        cache_code = cache.get(f"otp_{input_email}")
        user_data = cache.get(f"user_data_{input_email}")

        if cache_code is None or user_data is None:
            return Response({"msg": "kodi vaqti tugadi!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if int(input_code) != int(cache_code):
                return Response({"msg": "kodi hato"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"msg": "kod noto'g'ri formatda"}, status=status.HTTP_400_BAD_REQUEST)

        role = Role.objects.filter(name="operator").only("id").first()
        if role is None:
            return Response({"msg": "operator roli topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        User.objects.create_user(
            email=input_email,
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone_number=user_data["phone_number"],
            address=user_data["address"],
            is_verified=True,
            role=role
        )

        cache.delete(f"otp_{input_email}")
        cache.delete(f"user_data_{input_email}")

        return Response({"msg": "user muvafaqiyatli yaratildi!"}, status=status.HTTP_201_CREATED)

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data.get("user")
        refresh = RefreshToken.for_user(user=user)
        
        return Response({
            "email": str(user.email),
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": str(user.role)
        },status=status.HTTP_200_OK)
        
class RoleView(ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [RolePermissions]
    
class RoleObjectView(RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [RolePermissions]