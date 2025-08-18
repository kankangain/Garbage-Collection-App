from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages

from .models import Notification, DeviceToken

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

class MarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'status': 'success'})
        
        messages.success(request, 'Notification marked as read.')
        return redirect('notifications:list')

class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'status': 'success'})
        
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')

class UnreadCountAPIView(LoginRequiredMixin, View):
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({'unread_count': count})

class RegisterDeviceView(LoginRequiredMixin, View):
    def post(self, request):
        token = request.POST.get('token')
        platform = request.POST.get('platform', 'web')
        
        if not token:
            return JsonResponse({'error': 'Token required'}, status=400)
        
        device_token, created = DeviceToken.objects.get_or_create(
            user=request.user,
            token=token,
            defaults={'platform': platform}
        )
        
        if not created:
            device_token.platform = platform
            device_token.is_active = True
            device_token.save()
        
        return JsonResponse({
            'status': 'success',
            'created': created
        })
