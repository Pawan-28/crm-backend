from django.contrib import admin
from .models import Lead, Note, Activity

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'company', 'status', 'source', 'assigned_to', 'created_at')
    list_filter = ('status', 'source', 'assigned_to', 'created_at')
    search_fields = ('full_name', 'email', 'company', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone', 'company')
        }),
        ('Lead Details', {
            'fields': ('source', 'status', 'assigned_to', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('lead', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('lead__full_name', 'note')
    readonly_fields = ('created_at',)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('lead', 'user', 'action', 'created_at')
    list_filter = ('action', 'user', 'created_at')
    search_fields = ('lead__full_name', 'description')
    readonly_fields = ('created_at',)