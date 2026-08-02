from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.Login, name="login"),
    path("register/", views.Register, name="register"),
    path("logout/",views.Logout,name="logout"),
    
    path("officer/",views.officer_portal,name="officer_portal"),
    path(
    "officer/login/",
    views.officer_login,
    name="officer_login",
),
    
    path(
    "officer/register/",
    views.officer_register,
    name="officer_register",
),
    
    
    path("apply_municipality/", views.apply_municipality, name="apply_municipality"),
    
    path("forget_password/",views.ForgetPassword,name="forget_password"),
    path("submit_otp/",views.SubmitOTP,name="submit_otp"),
    path("reset_password/",views.ResetPassword,name="reset_password"),
    
    
    path("profile/",views.ProfileView, name="profile"),
    path("profile/edit/",views.EditProfileView, name="edit_profile"),
]