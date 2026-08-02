from django.db import models

# Create your models here.
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class customUser(AbstractUser):
    # You can add additional fields here if needed
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('public', 'Public'),
        ('municipality', 'Municipality'),
        ('worker', 'Worker'),
        
        
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20,unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='public')
    
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    

class Municipality(models.Model):
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    organization_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    
    official_email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    address = models.TextField()
    
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        blank=True,
        null = True
    )
    
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        blank=True,
        null=True
    )

    
    verification_document = models.FileField(upload_to='municipality_docs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.status}"
    
    

class OtpModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.otp} - Verified: {self.is_verified}"
    

 
    
    
  

