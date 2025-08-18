from django.contrib import admin
from .models import GarbageRequest, CompletionReport, RequestTracking

@admin.register(GarbageRequest)
class GarbageRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester_full_name', 'category', 'ward_number', 'status', 'assigned_labour', 'created_at')
    list_filter = ('status', 'category', 'ward_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'address', 'phone_number')
    readonly_fields = ('created_at', 'assigned_at', 'completed_at', 'approved_at')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'first_name', 'middle_name', 'last_name', 'phone_number', 'email')
        }),
        ('Location', {
            'fields': ('address', 'landmark', 'ward_number', 'latitude', 'longitude')
        }),
        ('Garbage Details', {
            'fields': ('category', 'garbage_image', 'description')
        }),
        ('Assignment', {
            'fields': ('status', 'assigned_labour', 'assigned_at')
        }),
        ('Completion', {
            'fields': ('completed_at', 'approved_at')
        }),
    )
    
    def requester_full_name(self, obj):
        return obj.requester_full_name
    requester_full_name.short_description = 'Requester Name'

@admin.register(CompletionReport)
class CompletionReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'labour', 'status', 'submitted_at', 'reviewed_by')
    list_filter = ('status', 'submitted_at')
    search_fields = ('request__first_name', 'request__last_name', 'labour__username')
    readonly_fields = ('submitted_at', 'reviewed_at')

@admin.register(RequestTracking)
class RequestTrackingAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'action', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('request__first_name', 'request__last_name', 'user__username')
    readonly_fields = ('timestamp',)
