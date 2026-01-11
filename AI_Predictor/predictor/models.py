"""
Database models for the prediction system.

Models:
- PredictionRecord: Stores prediction inputs, outputs, explanations, and recommendations
- PatientProfile: Stores patient demographics and health information
- ConsentRecord: Tracks user consent for data usage and medical disclaimers
- AuditLog: Logs all system actions for security and compliance
- ChatMessage: Stores AI assistant conversation history
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class PredictionRecord(models.Model):
    """
    Stores a single disease prediction with all inputs and outputs.
    
    Fields:
        user: User who made the prediction
        disease: Type of disease predicted (diabetes, heart, breast)
        inputs: JSON field storing all input features
        prediction_label: Human-readable prediction result
        probability: Confidence score for the prediction (0.0 to 1.0)
        probabilities: JSON field storing all class probabilities
        risk_level: Risk stratification (LOW, MEDIUM, HIGH)
        feature_importance: Feature importance scores for explainability
        top_features: Top contributing features
        risk_factors: Identified risk factors
        recommendations: Personalized health recommendations
        created_at: Timestamp of prediction
    """
    # Core prediction fields
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='predictions',
        null=True,
        blank=True,
        help_text="User who made this prediction"
    )
    disease = models.CharField(
        max_length=50,
        help_text="Disease type: diabetes, heart, or breast"
    )
    inputs = models.JSONField(
        help_text="Dictionary of input features used for prediction"
    )
    prediction_label = models.CharField(
        max_length=50,
        help_text="Human-readable prediction result"
    )
    probability = models.FloatField(
        help_text="Probability/confidence of the prediction (0.0 to 1.0)"
    )
    probabilities = models.JSONField(
        null=True,
        blank=True,
        help_text="Dictionary of all class probabilities"
    )
    
    # Advanced features
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
    ]
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVELS,
        null=True,
        blank=True,
        help_text="Risk stratification level"
    )
    feature_importance = models.JSONField(
        null=True,
        blank=True,
        help_text="Feature importance scores for explainability"
    )
    top_features = models.JSONField(
        null=True,
        blank=True,
        help_text="Top contributing features with values"
    )
    risk_factors = models.JSONField(
        null=True,
        blank=True,
        help_text="Identified risk factors"
    )
    recommendations = models.JSONField(
        null=True,
        blank=True,
        help_text="Personalized health recommendations"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when prediction was made"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['disease', '-created_at']),
            models.Index(fields=['user', 'risk_level', '-created_at']),
        ]
    
    def __str__(self):
        risk_str = f" [{self.risk_level}]" if self.risk_level else ""
        return f"{self.disease.title()} - {self.prediction_label}{risk_str} ({self.probability:.2%}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_risk_badge_class(self):
        """Return Bootstrap badge class for risk level"""
        return {
            'LOW': 'success',
            'MEDIUM': 'warning',
            'HIGH': 'danger',
        }.get(self.risk_level, 'secondary')


class PatientProfile(models.Model):
    """
    Patient demographic and health information profile.
    
    Stores comprehensive patient data for auto-filling prediction forms
    and tracking health metrics over time.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        help_text="Associated user account"
    )
    
    # Demographics
    age = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        help_text="Patient age in years"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        help_text="Biological sex"
    )
    
    # Physical metrics
    height = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Height in centimeters"
    )
    weight = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Weight in kilograms"
    )
    bmi = models.FloatField(
        null=True,
        blank=True,
        help_text="Body Mass Index (auto-calculated)"
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        null=True,
        blank=True
    )
    
    # Contact information
    phone = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    
    # Medical history
    medical_conditions = models.TextField(
        null=True,
        blank=True,
        help_text="Pre-existing medical conditions (comma-separated)"
    )
    medications = models.TextField(
        null=True,
        blank=True,
        help_text="Current medications (comma-separated)"
    )
    allergies = models.TextField(
        null=True,
        blank=True,
        help_text="Known allergies (comma-separated)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.age}y {self.get_gender_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate BMI if height and weight are provided"""
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100  # Convert cm to meters
            self.bmi = round(self.weight / (height_m ** 2), 2)
        super().save(*args, **kwargs)


class ConsentRecord(models.Model):
    """
    Tracks user consent for terms, privacy policy, and medical disclaimers.
    
    Required for HIPAA and GDPR compliance.
    """
    CONSENT_TYPES = [
        ('TERMS', 'Terms of Service'),
        ('PRIVACY', 'Privacy Policy'),
        ('MEDICAL_DISCLAIMER', 'Medical Disclaimer'),
        ('DATA_USAGE', 'Data Usage Agreement'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consents',
        help_text="User who gave consent"
    )
    consent_type = models.CharField(
        max_length=50,
        choices=CONSENT_TYPES,
        help_text="Type of consent"
    )
    consent_given = models.BooleanField(
        default=False,
        help_text="Whether consent was given"
    )
    consent_text = models.TextField(
        help_text="Full text of consent agreement"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Consent Record'
        verbose_name_plural = 'Consent Records'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Accepted" if self.consent_given else "Declined"
        return f"{self.user.username} - {self.get_consent_type_display()} ({status})"


class AuditLog(models.Model):
    """
    Comprehensive audit trail for all system actions.
    
    Logs user actions, admin operations, and system events for security
    and compliance monitoring.
    """
    ACTION_TYPES = [
        ('PREDICTION', 'Prediction Made'),
        ('PROFILE_UPDATE', 'Profile Updated'),
        ('USER_CREATED', 'User Created'),
        ('USER_DELETED', 'User Deleted'),
        ('ROLE_CHANGED', 'Role Changed'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('EXPORT', 'Data Export'),
        ('CONSENT_GIVEN', 'Consent Given'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        help_text="Type of action performed"
    )
    description = models.TextField(
        help_text="Detailed description of the action"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional action metadata"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{user_str} - {self.get_action_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """
    Stores AI medical assistant conversation history.
    
    Tracks user questions and AI responses for continuous improvement
    and user support.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        help_text="User who sent the message"
    )
    message = models.TextField(
        help_text="User message/question"
    )
    response = models.TextField(
        help_text="AI assistant response"
    )
    context = models.JSONField(
        null=True,
        blank=True,
        help_text="Prediction context used for generating response"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']
    
    def __str__(self):
        preview = self.message[:50] + "..." if len(self.message) > 50 else self.message
        return f"{self.user.username} - {preview}"
