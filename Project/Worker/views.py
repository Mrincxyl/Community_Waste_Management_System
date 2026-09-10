from .forms import WorkerForm
from UserAuth.models import customUser, Municipality, WorkerProfile
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.core.paginator import Paginator
from WasteReport.models import WasteReport, Notification
from WasteReport.email_utils import send_assignment_email, send_status_update_email
from django.shortcuts import get_object_or_404
from django.http import HttpResponse





@login_required(login_url="login")
def worker_list(request):
    if request.user.role != "municipality":
        messages.error(request, "Unauthorized access.")
        return redirect("home")

    municipality = Municipality.objects.filter(
        user=request.user
    ).first()

    workers = WorkerProfile.objects.filter(
        municipality=municipality,
        is_active=True,
    ).select_related("user").order_by("employee_id")
    
    total_workers = WorkerProfile.objects.filter(
        municipality=municipality,
        is_active=True,
    ).count()

    available_workers = WorkerProfile.objects.filter(
        municipality=municipality,
        is_active=True,
        status="available",
    ).count()

    busy_workers = WorkerProfile.objects.filter(
        municipality=municipality,
        is_active=True,
        status="busy",
    ).count()

    offline_workers = WorkerProfile.objects.filter(
        municipality=municipality,
        is_active=True,
        status="offline",
    ).count()
    
    

    search = request.GET.get("search", "")

    if search:
        workers = workers.filter(
            Q(employee_id__icontains=search) |
            Q(user__full_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__phone__icontains=search)
        )

    paginator = Paginator(workers, 8)

    page = request.GET.get("page")

    workers = paginator.get_page(page)

    context = {
        "workers": workers,
        "search": search,
        "total_workers": total_workers,
        "available_workers": available_workers,
        "busy_workers": busy_workers,
        "offline_workers": offline_workers,
    }

    return render(
        request,
        "worker/worker_list.html",
        context,
    )
    

@login_required(login_url="login")
def add_worker(request):

    if request.user.role != "municipality":
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")

    municipality = Municipality.objects.filter(
        user=request.user
    ).first()

    if municipality is None:
        messages.error(
            request,
            "Municipality profile not found."
        )
        return redirect("home")

    if request.method == "POST":

        form = WorkerForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if password != confirm_password:
                messages.error(
                    request,
                    "Passwords do not match."
                )
                return redirect("add_worker")

            email = form.cleaned_data["email"]

            if customUser.objects.filter(email=email).exists():
                messages.error(
                    request,
                    "Email already exists."
                )
                return redirect("add_worker")

            phone = form.cleaned_data["phone"]

            if customUser.objects.filter(phone=phone).exists():
                messages.error(
                    request,
                    "Phone number already exists."
                )
                return redirect("add_worker")

            worker = form.save(commit=False)

            base_username = email.split("@")[0]
            username = base_username
            counter = 1

            while customUser.objects.filter(
                username=username
            ).exists():

                username = f"{base_username}{counter}"
                counter += 1

            worker.username = username
            worker.role = "worker"
            worker.set_password(password)
            worker.save()

            last_worker = WorkerProfile.objects.aggregate(
                Max("employee_id")
            )["employee_id__max"]

            if last_worker:
                number = int(last_worker.replace("EMP", "")) + 1
            else:
                number = 1

            employee_id = f"EMP{number:04d}"
            
            WorkerProfile.objects.create(
                user=worker,
                municipality=municipality,
                employee_id=employee_id,
                ward=form.cleaned_data["ward"],
            )

            messages.success(
                request,
                "Worker added successfully."
            )

            return redirect("worker_list")

    else:

        form = WorkerForm()

    return render(
        request,
        "worker/add_worker.html",
        {
            "form": form
        }
    )

@login_required(login_url="login")
def edit_worker(request, pk):

    if request.user.role != "municipality":
        messages.error(request, "Unauthorized access.")
        return redirect("home")

    municipality = Municipality.objects.filter(
        user=request.user
    ).first()

    worker = get_object_or_404(
        WorkerProfile.objects.select_related("user"),
        id=pk,
        municipality=municipality,
    )

    user = worker.user

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        ward = request.POST.get("ward")
        status = request.POST.get("status")

        if customUser.objects.filter(phone=phone).exclude(id=user.id).exists():
            messages.error(request, "Phone number already exists.")
            return redirect("edit_worker", pk=worker.id)

        user.full_name = full_name
        user.phone = phone
        user.address = address

        if request.FILES.get("profile_picture"):
            user.profile_picture = request.FILES["profile_picture"]

        user.save()

        worker.ward = ward
        worker.status = status
        worker.save()

        messages.success(request, "Worker updated successfully.")

        return redirect("worker_detail", pk=worker.id)

    return render(
        request,
        "worker/edit_worker.html",
        {
            "worker": worker,
        },
    )


@login_required(login_url="login")
def delete_worker(request, id):
    if request.user.role != "municipality":
        messages.error(request, "Unauthorized access.")
        return redirect("home")

    municipality = Municipality.objects.filter(user=request.user).first()
    worker = get_object_or_404(
        WorkerProfile,
        id=id,
        municipality=municipality,
    )

    user = worker.user
    worker.delete()
    user.delete()

    messages.success(request, f"{user.full_name} has been deleted successfully.")
    return redirect("worker_list")


@login_required(login_url="login")
def worker_detail(request, pk):

    if request.user.role != "municipality":
        messages.error(request, "Unauthorized access.")
        return redirect("home")

    municipality = Municipality.objects.filter(
        user=request.user
    ).first()

    worker = get_object_or_404(
        WorkerProfile.objects.select_related("user"),
        id=pk,
        municipality=municipality,
    )

    context = {
        "worker": worker,
    }

    return render(
        request,
        "worker/worker_detail.html",
        context,
    )



@login_required(login_url="login")
def deactivate_worker(request, pk):

    if request.user.role != "municipality":
        messages.error(request, "Unauthorized access.")
        return redirect("home")

    municipality = Municipality.objects.filter(
        user=request.user
    ).first()

    worker = get_object_or_404(
        WorkerProfile,
        id=pk,
        municipality=municipality,
    )

    worker.is_active = False
    worker.save()

    messages.success(
        request,
        f"{worker.user.full_name} has been deactivated successfully."
    )

    return redirect("worker_list")


@login_required(login_url="login")
def assign_worker(request, report_id):

    if request.user.role != "municipality":
        messages.error(request, "Unauthorized access.")
        return redirect("home")

    municipality = get_object_or_404(
        Municipality,
        user=request.user,
    )

    report = get_object_or_404(
        WasteReport,
        id=report_id,
        assigned_municipality=municipality,
    )

    workers = WorkerProfile.objects.filter(
        municipality=municipality,
        is_active=True,
    ).select_related("user").order_by("employee_id")

    if request.method == "POST":

        worker_id = request.POST.get("worker")

        worker = get_object_or_404(
            WorkerProfile,
            id=worker_id,
            municipality=municipality,
            is_active=True,
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
            f"{worker.user.full_name} assigned successfully."
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


@login_required(login_url="worker_login")
def worker_dashboard(request):

    if request.user.role != "worker":
        return redirect("home")

    assigned_reports = WasteReport.objects.filter(
        assigned_worker__user=request.user,
        assigned_worker__is_active=True,
    ).select_related("user", "assigned_municipality", "assigned_worker").order_by("-updated_at")

    pending_jobs = assigned_reports.filter(status="pending").count()
    in_progress_jobs = assigned_reports.filter(status="in_progress").count()
    resolved_jobs = assigned_reports.filter(status="resolved").count()

    context = {
        "worker": request.user,
        "assigned_reports": assigned_reports,
        "pending_jobs": pending_jobs,
        "in_progress_jobs": in_progress_jobs,
        "resolved_jobs": resolved_jobs,
    }

    return render(request, "worker/dashboard.html", context)


@login_required(login_url="worker_login")
def complete_assigned_report(request, report_id):
    if request.user.role != "worker":
        return redirect("home")

    report = get_object_or_404(
        WasteReport,
        id=report_id,
        assigned_worker__user=request.user,
    )

    if request.method == "POST":
        action = request.POST.get("action", "resolved")
        proof_image = request.FILES.get("proof_image")
        latitude = request.POST.get("latitude") or report.latitude
        longitude = request.POST.get("longitude") or report.longitude

        if not proof_image:
            messages.error(
                request,
                "Proof image is required before completing this report.",
            )
            return redirect("worker_dashboard")

        if latitude in (None, "", "undefined") or longitude in (None, "", "undefined"):
            messages.error(
                request,
                "Current GPS location is required before completing this report.",
            )
            return redirect("worker_dashboard")

        report.proof_image = proof_image
        report.latitude = latitude
        report.longitude = longitude

        if action == "rejected":
            report.status = "rejected"
        else:
            report.status = "resolved"

        if report.assigned_worker:
            report.assigned_worker.status = "available"
            report.assigned_worker.save()

        report.save()

        Notification.objects.create(
            user=report.user,
            report=report,
            title="Worker Update on Waste Report",
            message=f'Your report "{report.title}" was updated by the assigned worker and is now marked as "{report.get_status_display()}".',
        )

        try:
            send_status_update_email(report)
        except Exception as e:
            print("Status Email Error:", e)

        messages.success(request, "Report status updated successfully.")
        return redirect("worker_dashboard")

    return redirect("worker_dashboard")
