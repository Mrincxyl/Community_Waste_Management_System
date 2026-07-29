from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from WasteReport.models import WasteReport
from UserAuth.models import customUser as user


def Home(request):
    total_report = WasteReport.objects.count()
    total_resolved = WasteReport.objects.filter(status='resolved').count()
    total_user = user.objects.count()

    info = {
        "report" : total_report,
        "resolved" :total_resolved,
        "total_users" : total_user
    }

    reports = WasteReport.objects.order_by('-updated_at')[:3]
    print(reports)
    print("Most recent reports retrieved successfully.")

    return render(request,"home.html",{"info": info,"reports": reports})








