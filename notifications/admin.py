from django.contrib import admin
from .models import Notification, DeviceToken

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at', 'read_at', 'push_sent_at')
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'title', 'message', 'notification_type')
        }),
        ('Related Objects', {
            'fields': ('request',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_pushed', 'push_sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'platform', 'is_active', 'created_at', 'last_used')
    list_filter = ('platform', 'is_active', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at', 'last_used')
