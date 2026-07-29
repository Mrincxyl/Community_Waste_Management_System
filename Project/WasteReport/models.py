from django.db import models

# Create your models here.
from django.conf import settings

class WasteReport(models.Model):
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected','Rejected'),
        )
    WASTE_TYPE_CHOICES = (
        ('household', 'Household Waste'),
        ('industrial', 'Industrial Waste'),
        ('organic', 'Organic Waste'),
        ('hazardous', 'Hazardous Waste'),
        ('electronic', 'Electronic Waste'),
        ('construction', 'Construction Waste'),
        ('medical', 'Medical Waste'),
        ('recyclable', 'Recyclable Waste'),
        ('other', 'Other Waste'),
         )
    
    URGENCY_LEVEL_CHOICES = (
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    
    title = models.CharField(max_length=200)
    waste_type = models.CharField(max_length=50, choices=WASTE_TYPE_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='waste_images/', blank=True, null=True)
    urgency_level = models.CharField(max_length=20,choices = URGENCY_LEVEL_CHOICES, default='low')
    landmark = models.CharField(max_length=200, blank=True, null=True)
    
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    # Auto-filled from GPS
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    full_address = models.TextField(blank=True,null=True)

    assigned_municipality = models.ForeignKey(
        "UserAuth.Municipality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_reports"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title 
    
    
    
    
class Notification(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications")
    
    
    report = models.ForeignKey(
        WasteReport,
        on_delete=models.CASCADE,
        related_name="notifications"
                               ) 
    title = models.CharField(max_length=200) 
    
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title    
    
    
    
    