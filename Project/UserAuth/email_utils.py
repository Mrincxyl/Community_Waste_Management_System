from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


def send_welcome_email(user):
    subject = "🕷️ Welcome to Community Waste Reporting!"
                
    html_content = render_to_string(
                    "emails/welcome_email.html",
                    {
                        "user":user,
                    }
                )
    email = EmailMultiAlternatives(
                    subject=subject,
                    body = "Welcome  to Waste Management Community Reporting!",
                    from_email=settings.EMAIL_HOST_USER,
                    to = [user.email],
                )
                
    email.attach_alternative(html_content,"text/html")
                
    email.send()

def send_otp_email(user,otp):
    
    subject = "OTP For Password Reset"
                
    html_content = render_to_string(
        "emails/otp_email.html",
        {
            "user":user,
            "otp":otp,
            
        }
        
    
    )
    
    email = EmailMultiAlternatives(
        subject= subject,
        body = f"Your OTP is {otp}",
        from_email= settings.EMAIL_HOST_USER,
        to = [user.email],
        
    )
    
    email.attach_alternative(html_content,"text/html")
    
    email.send()
    
    
def send_municipality_applied_email(municipality):
    subject = "Municipality Application Submitted"
                    
    html_content = render_to_string(
        "emails/municipality_applied_email.html",
        {
            "user":municipality.user,
            "municipality":municipality,
            
        }
    )
    
    email = EmailMultiAlternatives(
        subject= subject,
        body = "Municipality Application Submitted",
        from_email= settings.EMAIL_HOST_USER,
        to = [municipality.user.email],
        
    )
    
    email.attach_alternative(html_content,"text/html")
    
    email.send()
    
    
    