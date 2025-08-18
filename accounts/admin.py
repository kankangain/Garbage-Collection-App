from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone_number', 'email', 'role', 'ward_number', 'is_active', 'date_joined')
    list_filter = ('role', 'ward_number', 'is_active', 'is_verified')
    search_fields = ('username', 'phone_number', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'ward_number', 'is_verified')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'ward_number')
        }),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'first_name', 'last_name', 'address')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(CustomUser, CustomUserAdmin)
