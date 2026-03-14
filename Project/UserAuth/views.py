from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

def Login(request):
    
    if request.method == "POST":
        useremail = request.POST.get('email')
        
        if User.objects.filter(email=useremail).exists():
            messages.success(request,"You Logging Successfully")
            return render(request,'home.html')
        else:
            messages.error(request,"Please Create A Account.")
            return render(request,'register.html')    
    return render(request,"login.html") 


def Register(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        useremail = request.POST.get('email')
        number = request.POST.get('phone')
        password = request.POST.get('password') 
        
        isExists= User.objects.filter(email=useremail).exists()
        if isExists:
            messages.error(request,"Email already exists")
            return render(request,"register.html")
        
        user = User.objects.create_user(username=username,email=useremail,password=password)
        user.save()
        messages.success(request,"Registration successful")
        return render(request,"login.html")
        
        
        
    return render(request,"register.html")