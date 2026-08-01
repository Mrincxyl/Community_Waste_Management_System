from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import WasteReport, Notification
from .forms import wasteReportForm, wasteReportUpdateForm
from django.conf import settings
from django.core.files.storage import default_storage   #Imported By Mahabir [To Store waste report image temporary]
from . import waste_detection as wd

from .email_utils import send_status_update_email, send_submit_report_email

from UserAuth.models import Municipality

def FindCollection(request):
    return render(request,"find_collection.html")

@login_required(login_url='login')
def ReportWaste(request):
    if request.method == 'POST':
        form = wasteReportForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.cleaned_data["image"]

            path = default_storage.save(f"temp/{image.name}", image)
            full_path = default_storage.path(path)

            res = wd.predict_waste(full_path)

            if res["detect_res"] == 0:
                messages.error(
                    request,
                    "Your report could not be submitted because no significant waste was detected in the uploaded image."
                )
                return render(request, "report_waste.html", {"form": form})

            messages.success(request, "Waste Detected Successfully!!")

            waste_report = form.save(commit=False)
            waste_report.user = request.user

            municipality = Municipality.objects.filter(
                state__iexact=waste_report.state,
                district__iexact=waste_report.district,
                city__iexact=waste_report.city,
                status="approved"
            ).first()

            if municipality:
                waste_report.assigned_municipality = municipality

            waste_report.save()

            try:
                send_submit_report_email(waste_report)
            except Exception as e:
                print(e)

            messages.success(request, "Waste report submitted successfully!")
            return redirect("report_waste")

        else:
            print(form.errors)

    else:
        form = wasteReportForm()

    return render(request, "report_waste.html", {"form": form})



@login_required(login_url='login')
def my_reports(request):
    reports = WasteReport.objects.filter(user=request.user).order_by("-created_at")
    
    pending = reports.filter(status="pending").count()
    in_progress = reports.filter(status="in_progress").count()
    resolved = reports.filter( status="resolved").count()
    
    context = {
        "reports":reports,
        "pending":pending,
        "in_progress":in_progress,
        "resolved":resolved,
    }
    
    return render(request,'my_reports.html',context)


@login_required(login_url='login')
def municipality_dashboard(request):
    
    
    if request.user.role != 'municipality':
        messages.error(request, "You are not allowed to access this page.")
        return redirect("home")
    
    reports = WasteReport.objects.filter(assigned_municipality__user = request.user)
    pending = reports.filter(status="pending").count()
    in_progress = reports.filter(status="in_progress").count()
    resolved = reports.filter(status="resolved").count()
    
    return render(request,'municipality_dashboard.html',{"reports":reports, "pending":pending, "in_progress":in_progress, "resolved":resolved})



@login_required(login_url='login')
def update_report_status(request,id):
     
    if request.user.role != "municipality":
        messages.error(request,"You are not allowed to access this page.")
        return redirect('home')   

    report = get_object_or_404(WasteReport,id=id)
    
    old_status =  report.status
    
    if request.method == 'POST':
        
        form = wasteReportUpdateForm(request.POST,instance=report)
        
        if form.is_valid():
            update_report = form.save(commit=False)
            
            status_changed = old_status != update_report.status
            
            update_report.save()
            
            if status_changed:
                
                Notification.objects.create(
                    user = report.user,
                    report = update_report,
                    title = "Waste Report Status Updated",
                    message = f'Your report "{update_report.title}" has been marked as "{update_report.get_status_display()}".'
                    
                )
                try:
                    send_status_update_email(update_report)   
                except Exception as e:
                    print("Email Error:",e)    
            messages.success(request,'Report updated successfully!')
            return redirect('municipality_dashboard')
    else:
        form = wasteReportUpdateForm(instance=report)
            
    return render(request,"update_report.html",{"form":form,"report":report} ) 


@login_required(login_url='login')
def notification_list(request):
    
    notifications = Notification.objects.filter(user = request.user)
    
    return render(request,"notifications.html",{"notifications":notifications})

@login_required(login_url="login")
def mark_notification_read(request,id):
    
    notification = get_object_or_404(Notification,id=id,user=request.user)
    
    notification.is_read = True
    notification.save()
    
    return redirect("notification_list")


@login_required(login_url="login")
def mark_all_notifications_read(request):
    
    notifications = Notification.objects.filter(user=request.user,is_read=False)
    
    notifications.update(is_read=True)
    
    return redirect("notification_list")
   
   
   
@login_required(login_url="login")
def open_notification(request, id):

    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user
    )

    if not notification.is_read:
        notification.is_read = True
        notification.save()

    return redirect("my_reports")

@login_required(login_url="login")
def delete_notification(request, id):

    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user
    )

    notification.delete()

    messages.success(request, "Notification deleted successfully.")

    return redirect("notification_list")

@login_required(login_url="login")
def clear_notifications(request):

    Notification.objects.filter(
        user=request.user
    ).delete()

    messages.success(request, "All notifications cleared.")

    return redirect("notification_list")