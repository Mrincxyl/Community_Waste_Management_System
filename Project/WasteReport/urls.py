from django.urls import path
from . import views

urlpatterns = [
    path("find_collection/", views.FindCollection, name="find_collection"),     
    path("report_waste/", views.ReportWaste, name="report_waste"),
    path("my_reports/",views.my_reports,name="my_reports"),
    path("municipality_dashboard/", views.municipality_dashboard, name="municipality_dashboard"),
    path("update_report/<int:id>/",views.update_report_status,name="update_report" ), 
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/read/<int:id>/",views.mark_notification_read,name="mark_notification_read"),
    path("notifications/read-all/",views.mark_all_notifications_read,name="mark_all_notifications_read"),
    path("notification/open/<int:id>/",views.open_notification,name="open_notification",),
    path("notification/delete/<int:id>/",views.delete_notification,name="delete_notification",),
    path("notifications/clear/",views.clear_notifications,name="clear_notifications",),
    
]   