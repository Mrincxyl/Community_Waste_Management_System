from django.contrib import admin
from .models import WasteReport, Notification

# Register your models here.
@admin.register(WasteReport)
class WasteReportAdmin(admin.ModelAdmin):
    list_display = ('title','user', 'waste_type', 'urgency_level', 'status', 'created_at')
    list_filter = ('waste_type', 'urgency_level', 'status')
    search_fields = ('title', 'description', 'landmark','user__email')
    
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    
    list_display = (
        "id",
        "user",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__full_name",
        "user__email",
        "title",
    )
    
    