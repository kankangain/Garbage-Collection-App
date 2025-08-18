from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('request_created', 'New Request Created'),
        ('request_assigned', 'Request Assigned'),
        ('work_completed', 'Work Completed'),
        ('report_submitted', 'Completion Report Submitted'),
        ('report_approved', 'Report Approved'),
        ('report_rejected', 'Report Rejected'),
        ('overdue_alert', 'Overdue Alert'),
        ('general', 'General Notification'),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    
    # Related objects
    request = models.ForeignKey('gc_requests.GarbageRequest', on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Push notification fields
    is_pushed = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = models.timezone.now()
            self.save()

class DeviceToken(models.Model):
    """Store device tokens for push notifications"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, unique=True)
    platform = models.CharField(max_length=10, choices=[('android', 'Android'), ('ios', 'iOS'), ('web', 'Web')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.platform}"
