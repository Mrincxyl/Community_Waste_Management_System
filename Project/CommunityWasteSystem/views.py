from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def Home(request):
    return render(request,"home.html")

def FindCollection(request):
    return render(request,"find_collection.html")

@login_required(login_url='login')
def ReportWaste(request):
    return render(request,"report_waste.html")

