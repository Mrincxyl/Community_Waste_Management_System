from django.contrib import admin
from django.utils import timezone
from .models import customUser, Municipality

from .models import OtpModel

# Register your models here.
from .models import customUser 
admin.site.register(customUser) 
admin.site.register(OtpModel)


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ("user", "organization_name", "status", "applied_at")
    list_filter = ("status",)
    search_fields = ("user__email", "organization_name")

    actions = ["approve_request", "reject_request"]

    def approve_request(self, request, queryset):
        for obj in queryset:
            obj.status = "approved"
            obj.reviewed_at = timezone.now()
            obj.save()

            user = obj.user
            user.role = "municipality"
            user.save()

    def reject_request(self, request, queryset):
        queryset.update(status="rejected", reviewed_at=timezone.now())

