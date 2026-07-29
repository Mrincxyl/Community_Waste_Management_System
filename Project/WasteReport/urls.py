from django.urls import path
from . import views

urlpatterns = [
    path("find_collection/", views.FindCollection, name="find_collection"),     
    path("report_waste/", views.ReportWaste, name="report_waste"),
    path("my_reports/",views.my_reports,name="my_reports"),
    path("municipality_dashboard/", views.municipality_dashboard, name="municipality_dashboard"),
    path("update_report/<int:id>/",views.update_report_status,name="update_report" ), 
]   