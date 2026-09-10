from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


def send_assignment_email(report, worker):
    subject = "Waste Task Has Been Assigned"

    html_content = render_to_string(
        "emails/worker_assignment_email.html",
        {
            "worker": worker,
            "report": report,
        },
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=f"A new waste task '{report.title}' has been assigned to you.",
        from_email=settings.EMAIL_HOST_USER,
        to=[worker.user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


def send_status_update_email(update_report):
    subject = "Waste Report Status Updated"

    html_content = render_to_string(
        "emails/status_update_email.html",
        {
            "user": update_report.user,
            "report": update_report,
        },
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body="Your waste report status has been updated.",
        from_email=settings.EMAIL_HOST_USER,
        to=[update_report.user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


def send_submit_report_email(waste_report):
    subject = "Report Submit Successfully!"

    html_content = render_to_string(
        "emails/submit_report_email.html",
        {
            "user": waste_report.user,
            "report": waste_report,
        },
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body="Your waste report has been uploaded successfully.",
        from_email=settings.EMAIL_HOST_USER,
        to=[waste_report.user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
    