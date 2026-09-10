from django.contrib import admin
from django.utils import timezone
import traceback

from .models import customUser, Municipality, OtpModel

from .email_utils import send_officer_approved_email 

@admin.register(customUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",
        "role",
    )

    search_fields = (
        "full_name",
        "email",
    )


admin.site.register(OtpModel)


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):

    list_display = (
        "organization_name",
        "official_email",
        "district",
        "state",
        "status",
        "applied_at",
    )

    list_filter = (
        "status",
        "state",
    )

    search_fields = (
        "organization_name",
        "official_email",
        "district",
    )

    readonly_fields = (
        "applied_at",
        "reviewed_at",
    )

    actions = (
        "approve_request",
        "reject_request",
    )

    def approve_request(self, request, queryset):

        for obj in queryset:

            obj.status = "approved"
            obj.reviewed_at = timezone.now()
            obj.save()

            user = obj.user
            user.role = "municipality"
            user.save()

            try:
                send_officer_approved_email(user)
                print("Officer approval email sent successfully.")
            except Exception:
                traceback.print_exc()
                

        self.message_user(
            request,
            f"{queryset.count()} municipality account(s) approved successfully."
        )

    approve_request.short_description = "Approve selected municipality registrations"

    def reject_request(self, request, queryset):

        queryset.update(
            status="rejected",
            reviewed_at=timezone.now()
        )

        self.message_user(
            request,
            f"{queryset.count()} municipality account(s) rejected."
        )

    reject_request.short_description = "Reject selected municipality registrations"