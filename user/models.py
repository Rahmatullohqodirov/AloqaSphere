from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from .validations import phone_number_validation


class Role(models.Model):
    name = models.CharField(max_length=50,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    class Meta:
        db_table = "role"
        
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritilishi shart!")
        email = self.normalize_email(email)
        extra_fields.pop('username', None) 
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if 'role' not in extra_fields and 'role_id' not in extra_fields:
            from .models import Role
            admin_role = Role.objects.get_or_create(name='admin')
            extra_fields['role'] = admin_role
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username= None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=13,validators=[phone_number_validation])
    address = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    role = models.ForeignKey(Role,on_delete=models.CASCADE, related_name="role")
    
    objects = CustomUserManager()
    
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name","last_name","phone_number","address"]
    
    class Meta:
        db_table = "user"
    def __str__(self):
        return str(self.email)