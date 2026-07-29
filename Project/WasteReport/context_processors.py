from .models import Notification


def notification_context(request):
    
    if request.user.is_authenticated:
        
        notifications = Notification.objects.filter(user = request.user)[:5]
        
        unread_count = Notification.objects.filter(user = request.user,
                                                   is_read =False).count()
    else:
        
        notifications = []
        unread_count = 0
    
    return {
        "navbar_notifications": notifications,
        "unread_notification_count":unread_count
    }        