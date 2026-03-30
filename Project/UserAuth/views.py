from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout



# Create your views here.

def Login(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "All Fields are required.")
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
            
    return render(request, "login.html")


def Register(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        useremail = request.POST.get('email')
        number = request.POST.get('phone')
        password = request.POST.get('password') 
        confirm_password = request.POST.get('confirm_password')
        
        if not username or not useremail or not number or not password or not confirm_password:
            messages.error(request,"All Fields are required.")
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request,"Password does not Mathced!")
            return redirect('register')
        
        isExists= User.objects.filter(email=useremail).exists()
        if isExists:
            messages.error(request,"Email already exists")
            return render(request,"register.html")
        
        user = User.objects.create_user(username=username,email=useremail,password=password)
        user.save()
        messages.success(request,"Registration successful")
        return render(request,"login.html")
        
        
        
    return render(request,"register.html")

def Logout(request):
    logout(request)
    messages.success(request,"Logged out successfully")
    return redirect('home')
