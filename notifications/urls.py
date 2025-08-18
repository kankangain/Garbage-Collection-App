from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('<int:notification_id>/read/', views.MarkAsReadView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
    path('api/unread-count/', views.UnreadCountAPIView.as_view(), name='unread_count'),
    path('api/register-device/', views.RegisterDeviceView.as_view(), name='register_device'),
]
