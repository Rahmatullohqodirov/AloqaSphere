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
class SendEmailView(CreateAPIView):
    serializer_class = UserSendEmailSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = request.data.get("email").lower()
            code = random.randint(100000,999999)
            
            is_sent = send_mail(
                subject="AloqaSphere",
                message=f"Sizning registrasiya kodingiz {code}",
                from_email=config("EMAIL_HOST_USER"),
                recipient_list=[email]
            )
            cache.set(f"otp_{email}",code,timeout=300)
            cache.set(f"user_data_{email}",serializer.validated_data,timeout=300)
          
            if is_sent == 1:
                return Response({"msg": "kodi junatildi"},status=status.HTTP_200_OK)
            return Response({"msg":"kodi junatilmadi"},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserSaveView(CreateAPIView):
    queryset = User.objects.all()
    
    def post(self, request, *args, **kwargs):
        
        input_email = request.data.get("input_email").lower()
        input_code = request.data.get("input_code")
        cache_code = cache.get(f"otp_{input_email}")
        user_data = cache.get(f"user_data_{input_email}")
        role = User.objects.get(name="user")
    
        if cache_code is not None:
            if int(input_code) == int(cache_code):
                User.objects.create_user(
                    email=input_email,
                    password=user_data["password"],
                    first_name = user_data["first_name"],
                    last_name = user_data["last_name"],
                    phone_number = user_data["phone_number"],
                    address = user_data["address"],
                    is_verified=True,
                    role = role
                )
                
                return Response({"msg": "user muvafaqiyatli yaratildi!"},status=status.HTTP_201_CREATED)
            return Response({"msg": "kodi hato"})
        print(cache_code)
        return Response({"msg": "kodi vaqti tugadi!"})
    

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    
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
          
    
                    