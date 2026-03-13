from django.shortcuts import render

def Home(request):
    return render(request,"home.html")

def FindCollection(request):
    return render(request,"find_collection.html")

def ReportWaste(request):
    return render(request,"report_waste.html")

