from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import MunicipalityForm
from .models import Municipality

from .models import customUser as User   
from WasteReport.models import WasteReport

import re
import random
from .models import OtpModel

from django.conf import settings
from .email_utils import send_welcome_email, send_otp_email, send_municipality_applied_email

# Create your views here.

def Login(request):
    
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("login")

        user_obj = User.objects.filter(email=email).first()

        if user_obj is None:
            messages.error(request, "Invalid email or password.")
            return redirect("login")

        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            if user.role == "municipality":
                messages.success(request, "Logged in successfully as Municipality")
                return redirect("municipality_dashboard")

            messages.success(request, "Logged in successfully")
            return redirect("home")

        messages.error(request, "Invalid email or password")
        return redirect("login")

    return render(request, "login.html")


def Register(request):
    
    if request.user.is_authenticated:
        messages.info(request, "You are already Registered.")
        return redirect("home")
    
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        password = request.POST.get('password') 
        confirm_password = request.POST.get('confirm_password')
        
        if not full_name or not email or not phone or not password or not confirm_password:
            messages.error(request,"All Fields are required.")
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request,"Password does not Matched!")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request,"Email already exists")
            return redirect('register')
        
        if User.objects.filter(phone=phone).exists():
            messages.error(request,"Phone number already exists")
            return redirect('register')
        
        username = email.split('@')[0]  # Generate username from email      
        while User.objects.filter(username=username).exists():
            username += '1'  # Append a number to make it unique
            
        user = User.objects.create_user(username=username, full_name=full_name, email=email, phone=phone, role=role, password=password)
        user.save()
        
        try:
            send_welcome_email(user)
            
        except Exception as e:  
            print(e)  
        messages.success(request,"Registration successful")
        return redirect('login')
          
    return render(request,"register.html")


def Logout(request):
    
    if  not request.user.is_authenticated:
        messages.info(request,"You are already logged out.")
        return redirect('home')
    logout(request)
    messages.success(request,"Logged out successfully")
    return redirect('home')


@login_required(login_url='login')
def apply_municipality(request):
    if request.user.role == "municipality":
        messages.info(request, "You are already a municipality user.")
        return redirect('home')
    
    application = Municipality.objects.filter(user=request.user).first()
    
    if application:
        if application.status == 'pending':
            messages.info(request, "Your application is still pending. Please wait for review.")
            return redirect('home') 
        if application.status == 'approved':
            messages.info(request,'Your application has been approved. You can now access municipality features.')
            return redirect('municipality_dashboard') 
        if application.status == 'rejected':
            messages.info(request,'Your application has been rejected. You can reapply with correct information.')
            return redirect('home')    
                    
    
    if request.method == "POST":
        form = MunicipalityForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user 
            obj.save()
            
            try:
                send_municipality_applied_email(obj)
            except Exception as e:
                print(e)    
            messages.success(request, "Municipality application submitted successfully!")
            return redirect('home')
    else:
        form = MunicipalityForm()
        
    return render(request, "apply_municipality.html", {"form": form}) 


def ForgetPassword(request): 
    
    if request.method == "POST" and 'send_otp' in request.POST:
        username_or_email = request.POST.get('username_or_email')
        if not username_or_email:
            messages.error(request,'Please Enter Your Username or Email.')  
            return redirect('forget_password') 
        else:
            user = None
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if '@' in username_or_email and re.match(email_regex,username_or_email):
                try:
                    user = User.objects.get(email=username_or_email)
                except User.DoesNotExist:
                    messages.error(request,f"No user found with this email {username_or_email}")  
                    return redirect('forget_password')  
            else:
                try:
                    user = User.objects.get(username=username_or_email)    
                except User.DoesNotExist:
                    messages.error(request,f"No user found with this username {username_or_email}")  
                    return redirect('forget_password')
                
        OtpModel.objects.filter(user=user).delete()
        otp = str(random.randint(100000,999999))
        OtpModel.objects.create(user=user,otp=otp)
        
        try:
            send_otp_email(user,otp)
        except Exception as e:
            print(e)
            messages.error(request, "Failed to send OTP.")
            return redirect("forget_password")
            
        messages.success(request,f'OTP sent to your email {user.email}')
        request.session['reset_user'] = user.id
        return redirect('submit_otp')        
                    
    return render(request,'forget_password.html') 



def SubmitOTP(request):
    
    user_id = request.session.get("reset_user")
    
    if not user_id:
        messages.error(request,"Session Expired.")
        return redirect("forget_password")
    
    user = User.objects.get(id = user_id)
    
    if request.method == "POST":
        otp = request.POST.get("otp")
        try:
            otp_obj = OtpModel.objects.get(user=user, otp=otp)
        except OtpModel.DoesNotExist:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("submit_otp")
        
        request.session['verified_user'] = user.id
        otp_obj.delete()  # Delete the OTP after successful verification
        
        return redirect("reset_password") 
    
    return render(request,"submit_otp.html") 
    
 
    
def ResetPassword(request):
        
    user_id = request.session.get("verified_user")
        
    if not user_id:
        messages.error(request,"Unauthorized access.")
        return redirect("forget_password")
        
    user = User.objects.get(id=user_id)
        
    if request.method == 'POST':
            
        password = request.POST.get("password")
            
        confirm_password = request.POST.get("confirm_password")
            
        if password != confirm_password:
            messages.error(request,"Password do not match.")
            return redirect('reset_password')
            
        user.set_password(password)
        user.save()
            
            
        del request.session['verified_user']
        del request.session['reset_user']
            
        messages.success(request,"Password changed successfully.")
            
        return redirect('login')
    
    return render(request,"reset_password.html")    


@login_required(login_url="login")
def ProfileView(request):
    reports = WasteReport.objects.filter(user=request.user).order_by('-created_at')
    pending = reports.filter(status='pending').count()
    in_progress = reports.filter(status='in_progress').count()
    resolved = reports.filter(status='resolved').count()
    rejected = reports.filter(status='rejected').count()
    
    total_reports = reports.count()

    context = {
        'reports': reports,
        'pending': pending,
        'in_progress': in_progress, 
        'resolved': resolved,
        'rejected': rejected,
        'total_reports': total_reports,
    }

    return render(request,"profile.html", context)

@login_required(login_url="login")
def EditProfileView(request):
    
    user = request.user
    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        
        if User.objects.filter(phone=phone).exclude(id=user.id).exists():
            messages.error(request,"Phone number already exists.")
            return redirect('edit_profile')
        
        user.full_name = full_name
        user.phone = phone
        user.address = address
        
        if request.FILES.get("profile_picture"):
            user.profile_picture = request.FILES["profile_picture"]
        
        user.save()
        
        messages.success(request,"Profile Updated Successfully.")
        return redirect("profile")
        
        
    return render(request,"edit_profile.html")       