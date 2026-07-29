from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import WasteReport, Notification
from .forms import wasteReportForm, wasteReportUpdateForm
from django.conf import settings

from .email_utils import send_status_update_email, send_submit_report_email

def FindCollection(request):
    return render(request,"find_collection.html")

@login_required(login_url='login')
def ReportWaste(request):
    if request.method == 'POST':
        form = wasteReportForm(request.POST, request.FILES)
        if form.is_valid():
            waste_report = form.save(commit=False)
            waste_report.user = request.user
            waste_report.save()
            
            try:
                send_submit_report_email(waste_report)
            except Exception as e:
                print(e)    
                
            messages.success(request, 'Waste report submitted successfully!')
            return redirect('report_waste')
        else:
            print(form.errors)  # Print form errors to the console for debugging    
    else:
        form = wasteReportForm()
    
    return render(request,"report_waste.html",{'form': form })



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
    
    reports = WasteReport.objects.all().order_by("-created_at")
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




   