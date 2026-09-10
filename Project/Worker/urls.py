from django.urls import path
from . import views

urlpatterns = [

    path("list/", views.worker_list, name="worker_list"),
    path("add/",views.add_worker,name="add_worker"),
    path("edit/<int:pk>/",views.edit_worker,name="edit_worker"),
    path("delete/<int:id>/", views.delete_worker, name="delete_worker"),
    path(
    "view/<int:pk>/",
    views.worker_detail,
    name="worker_detail",
),
    path(
        "deactivate/<int:pk>/",
        views.deactivate_worker,
        name="deactivate_worker",
    ),
    
    path(
    "dashboard/",
    views.worker_dashboard,
    name="worker_dashboard",
),
    path(
    "complete/<int:report_id>/",
    views.complete_assigned_report,
    name="complete_assigned_report",
),
    
    path(
    "assign/<int:report_id>/",
    views.assign_worker,
    name="worker_assign_report",
),
    
]