from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class GarbageRequest(models.Model):
    GARBAGE_CATEGORIES = (
        ('animal_remains', 'Remains of Animals'),
        ('human_waste', 'Human Wastage'),
        ('household', 'Household Waste'),
        ('construction', 'Construction Debris'),
        ('electronic', 'Electronic Waste'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    # Request details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    landmark = models.CharField(max_length=100, blank=True)
    ward_number = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=GARBAGE_CATEGORIES)
    garbage_image = models.ImageField(upload_to='garbage_images/')
    description = models.TextField(blank=True, help_text="Additional description of the garbage")
    
    # Status and assignment
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    assigned_labour = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_requests',
        limit_choices_to={'role': 'labour'}
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Location coordinates (for future mapping)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Request #{self.id} - {self.get_category_display()} - Ward {self.ward_number}"
    
    @property
    def is_overdue(self):
        if self.assigned_at and self.status not in ['completed', 'approved']:
            return timezone.now() > (self.assigned_at + timedelta(hours=72))
        return False
    
    @property
    def time_remaining(self):
        if self.assigned_at and self.status not in ['completed', 'approved']:
            deadline = self.assigned_at + timedelta(hours=72)
            remaining = deadline - timezone.now()
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                return f"{hours}h {minutes}m"
            return "Overdue"
        return None
    
    @property
    def requester_full_name(self):
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}"

class CompletionReport(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    request = models.ForeignKey(GarbageRequest, on_delete=models.CASCADE, related_name='completion_reports')
    labour = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='completion_reports')
    completion_image = models.ImageField(upload_to='completion_images/')
    notes = models.TextField(blank=True, help_text="Notes about the completion")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_reports'
    )
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Completion Report for Request #{self.request.id}"

class RequestTracking(models.Model):
    ACTION_CHOICES = (
        ('created', 'Request Created'),
        ('assigned', 'Assigned to Labour'),
        ('in_progress', 'Work Started'),
        ('completed', 'Work Completed'),
        ('report_submitted', 'Completion Report Submitted'),
        ('report_approved', 'Report Approved'),
        ('report_rejected', 'Report Rejected'),
        ('overdue_alert', 'Overdue Alert Sent'),
    )
    
    request = models.ForeignKey(GarbageRequest, on_delete=models.CASCADE, related_name='tracking')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_display()} - Request #{self.request.id}"
