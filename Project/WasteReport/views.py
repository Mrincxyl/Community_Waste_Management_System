from multiprocessing import context
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import WasteReport, Notification
from .forms import wasteReportForm, wasteReportUpdateForm
from django.conf import settings
from django.core.files.storage import default_storage   #Imported By Mahabir [To Store waste report image temporary]
from . import waste_detection as wd

from .email_utils import send_assignment_email, send_status_update_email, send_submit_report_email

from UserAuth.models import Municipality, WorkerProfile

from django.core.paginator import Paginator


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

            waste_report.save()

            municipality = Municipality.objects.filter(
                state__iexact=waste_report.state,
                district__iexact=waste_report.district,
                city__iexact=waste_report.city,
                status="approved"
            ).first()

            if municipality:
                waste_report.assigned_municipality = municipality
                waste_report.save(update_fields=["assigned_municipality"])
                Notification.objects.create(
                    user=municipality.user,
                    report=waste_report,
                    title="New Waste Report Submitted",
                    message=f'A new waste report "{waste_report.title}" was submitted in your municipality and needs review.',
                )

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

    if request.user.role != "municipality":
        messages.error(request, "You are not allowed to access this page.")
        return redirect("home")

    municipality = Municipality.objects.filter(
        user=request.user
    ).first()
 
    reports = WasteReport.objects.filter(
        assigned_municipality__user=request.user
    )
    
    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    waste_type = request.GET.get("waste_type", "")
    priority = request.GET.get("priority", "")

    if search:
        reports = reports.filter(title__icontains=search)

    if status_filter:
        reports = reports.filter(status=status_filter)

    if waste_type:
        reports = reports.filter(waste_type=waste_type)

    if priority:
        reports = reports.filter(urgency_level=priority)

    pending_reports_queryset = reports.filter(status="pending")
    in_progress_reports_queryset = reports.filter(status="in_progress")
    resolved_reports_queryset = reports.filter(status="resolved")
    rejected_reports_queryset = reports.filter(status="rejected")

    pending = pending_reports_queryset.count()
    in_progress = in_progress_reports_queryset.count()
    resolved = resolved_reports_queryset.count()
    rejected = rejected_reports_queryset.count()

    pending_paginator = Paginator(pending_reports_queryset, 6)
    pending_reports = pending_paginator.get_page(
        request.GET.get("pending_page")
    ) 

    in_progress_paginator = Paginator(in_progress_reports_queryset, 6)
    in_progress_reports = in_progress_paginator.get_page(
        request.GET.get("progress_page")
    )

    resolved_paginator = Paginator(resolved_reports_queryset, 6)
    resolved_reports = resolved_paginator.get_page(
        request.GET.get("resolved_page")
    )

    rejected_paginator = Paginator(rejected_reports_queryset, 6)
    rejected_reports = rejected_paginator.get_page(
        request.GET.get("rejected_page")
    )

    context = {
    "municipality": municipality,
    "reports": reports,

    "pending_reports": pending_reports,
    "in_progress_reports": in_progress_reports,
    "resolved_reports": resolved_reports,
    "rejected_reports": rejected_reports,

    "pending": pending,
    "in_progress": in_progress,
    "resolved": resolved,
    "rejected": rejected,

    "search": search,
    "status_filter": status_filter,
    "waste_type_filter": waste_type,
    "priority_filter": priority,

    "waste_types": WasteReport.WASTE_TYPE_CHOICES,
    "status_choices": WasteReport.STATUS_CHOICES,
    "priority_choices": WasteReport.URGENCY_LEVEL_CHOICES,
}

    return render(request, "municipality/dashboard.html", context)


@login_required(login_url='login')
def municipality_reports(request):

    if request.user.role != "municipality":
        messages.error(request, "You are not allowed to access this page.")
        return redirect("home")

    municipality = Municipality.objects.filter(user=request.user).first()
    reports = WasteReport.objects.filter(
        assigned_municipality=municipality
    ).select_related("user", "assigned_worker__user").order_by("-updated_at")

    return render(
        request,
        "municipality/reports.html",
        {
            "municipality": municipality,
            "reports": reports,
        },
    )


@login_required(login_url='login')
def update_report_status(request,id):
     
    if request.user.role != "municipality":
        messages.error(request,"You are not allowed to access this page.")
        return redirect('home')   

    report = get_object_or_404(WasteReport,id=id)
    
    old_status =  report.status
    
    if request.method == 'POST':
        
        form = wasteReportUpdateForm(request.POST, request.FILES, instance=report)
        
        if form.is_valid():
            update_report = form.save(commit=False)

            if request.FILES.get("proof_image"):
                update_report.proof_image = request.FILES["proof_image"]

            status_order = {
                "pending": 1,
                "in_progress": 2,
                "resolved": 3,
                "rejected": 3,
            }

            current_order = status_order.get(old_status, 0)
            new_order = status_order.get(update_report.status, 0)

            if new_order < current_order:
                messages.error(request, "Status cannot be rolled back to a previous state.")
                return redirect("municipality_dashboard")
            
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

    if request.user.role == 'municipality':
        base_template = 'municipality/base_municipality.html'
    elif request.user.role == 'worker':
        base_template = 'worker/base_worker.html'
    else:
        base_template = 'base.html'
    
    return render(request,"notifications.html",{"notifications":notifications, "base_template": base_template})

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

    if request.user.role == "worker":
        return redirect("worker_dashboard")
    if request.user.role == "municipality":
        return redirect("municipality_dashboard")
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




@login_required(login_url="login")
def assign_worker(request, pk):

    if request.user.role != "municipality":
        return redirect("home")

    municipality = Municipality.objects.filter(
        user=request.user
    ).first()

    report = get_object_or_404(
        WasteReport,
        id=pk,
        assigned_municipality=municipality,
    )

    workers = WorkerProfile.objects.filter(
        municipality=municipality,
        is_active=True,
        status="available",
    ).select_related("user")

    if request.method == "POST":

        worker = get_object_or_404(
            WorkerProfile,
            id=request.POST.get("worker"),
            municipality=municipality,
        )

        report.assigned_worker = worker
        report.status = "in_progress"
        report.save()

        worker.status = "busy"
        worker.save()

        Notification.objects.create(
            user=report.user,
            report=report,
            title="Waste Report Assigned to Worker",
            message=f'Your report "{report.title}" has been assigned to worker {worker.user.full_name} and is now in progress.',
        )

        Notification.objects.create(
            user=worker.user,
            report=report,
            title="New Waste Assignment",
            message=f'You have been assigned a new job: "{report.title}". Please review and start work on it.',
        )

        try:
            send_assignment_email(report, worker)
        except Exception as e:
            print("Assignment Email Error:", e)

        messages.success(
            request,
            "Worker assigned successfully."
        )

        return redirect("municipality_dashboard")

    return render(
        request,
        "worker/assign_worker.html",
        {
            "report": report,
            "workers": workers,
        },
    )