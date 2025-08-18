from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('chairman', 'Chairman'),
        ('councilor', 'Councilor'),
        ('labour', 'Labour'),
        ('user', 'User'),
    )
    
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    phone_number = models.CharField(max_length=15, unique=True)
    ward_number = models.IntegerField(null=True, blank=True, help_text="Ward number for councilors and labour")
    is_verified = models.BooleanField(default=False)
    
    # Override email to make it optional
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    landmark = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}"
