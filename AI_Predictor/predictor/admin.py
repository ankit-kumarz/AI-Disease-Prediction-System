"""
Django Admin Configuration for AI Disease Prediction System

Registers all models with enhanced admin interfaces for easy management.
"""

from django.contrib import admin
from .models import (
    PredictionRecord,
    PatientProfile,
    ConsentRecord,
    AuditLog,
    ChatMessage
)


@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'disease', 'prediction_label',
        'risk_level', 'probability', 'created_at'
    ]
    list_filter = ['disease', 'risk_level', 'created_at']
    search_fields = ['prediction_label', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'disease', 'prediction_label', 'probability', 'created_at')
        }),
        ('Risk Assessment', {
            'fields': ('risk_level', 'risk_factors')
        }),
        ('AI Explainability', {
            'fields': ('feature_importance', 'top_features'),
            'classes': ('collapse',)
        }),
        ('Recommendations', {
            'fields': ('recommendations',),
            'classes': ('collapse',)
        }),
        ('Raw Data', {
            'fields': ('inputs', 'probabilities'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'age', 'gender', 'bmi',
        'blood_group', 'created_at', 'updated_at'
    ]
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'bmi']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Demographics', {
            'fields': ('age', 'gender', 'blood_group')
        }),
        ('Physical Metrics', {
            'fields': ('height', 'weight', 'bmi')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact')
        }),
        ('Medical History', {
            'fields': ('medical_conditions', 'medications', 'allergies'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'consent_type', 'consent_given',
        'ip_address', 'created_at'
    ]
    list_filter = ['consent_type', 'consent_given', 'created_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Consent Information', {
            'fields': ('user', 'consent_type', 'consent_given', 'consent_text')
        }),
        ('Tracking Information', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'action_type', 'description',
        'ip_address', 'created_at'
    ]
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['created_at', 'ip_address', 'user_agent', 'metadata']
    date_hierarchy = 'created_at'
    list_per_page = 100
    
    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'action_type', 'description')
        }),
        ('Tracking Information', {
            'fields': ('ip_address', 'user_agent', 'created_at')
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs (compliance requirement)
        return request.user.is_superuser


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'message_preview', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['user__username', 'message', 'response']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Chat Information', {
            'fields': ('user', 'message', 'response', 'created_at')
        }),
        ('Context', {
            'fields': ('context',),
            'classes': ('collapse',)
        }),
    )
    
    def message_preview(self, obj):
        return obj.message[:75] + '...' if len(obj.message) > 75 else obj.message
    message_preview.short_description = 'Message'

