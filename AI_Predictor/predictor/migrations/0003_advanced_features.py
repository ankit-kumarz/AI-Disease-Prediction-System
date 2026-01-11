# Generated migration for advanced healthcare features

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictor', '0002_predictionrecord_user'),
    ]

    operations = [
        # Add new fields to PredictionRecord
        migrations.AddField(
            model_name='predictionrecord',
            name='risk_level',
            field=models.CharField(
                blank=True,
                choices=[('LOW', 'Low Risk'), ('MEDIUM', 'Medium Risk'), ('HIGH', 'High Risk')],
                help_text='Risk stratification level',
                max_length=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='predictionrecord',
            name='feature_importance',
            field=models.JSONField(
                blank=True,
                help_text='Feature importance scores for explainability',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='predictionrecord',
            name='top_features',
            field=models.JSONField(
                blank=True,
                help_text='Top contributing features with values',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='predictionrecord',
            name='risk_factors',
            field=models.JSONField(
                blank=True,
                help_text='Identified risk factors',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='predictionrecord',
            name='recommendations',
            field=models.JSONField(
                blank=True,
                help_text='Personalized health recommendations',
                null=True
            ),
        ),
        
        # Create PatientProfile model
        migrations.CreateModel(
            name='PatientProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField(help_text='Patient age in years')),
                ('gender', models.CharField(
                    choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
                    help_text='Biological sex',
                    max_length=1
                )),
                ('height', models.FloatField(blank=True, help_text='Height in centimeters', null=True)),
                ('weight', models.FloatField(blank=True, help_text='Weight in kilograms', null=True)),
                ('bmi', models.FloatField(blank=True, help_text='Body Mass Index (auto-calculated)', null=True)),
                ('blood_group', models.CharField(
                    blank=True,
                    choices=[
                        ('A+', 'A+'), ('A-', 'A-'),
                        ('B+', 'B+'), ('B-', 'B-'),
                        ('AB+', 'AB+'), ('AB-', 'AB-'),
                        ('O+', 'O+'), ('O-', 'O-')
                    ],
                    max_length=3,
                    null=True
                )),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('emergency_contact', models.CharField(blank=True, max_length=15, null=True)),
                ('medical_conditions', models.TextField(blank=True, help_text='Pre-existing medical conditions', null=True)),
                ('medications', models.TextField(blank=True, help_text='Current medications', null=True)),
                ('allergies', models.TextField(blank=True, help_text='Known allergies', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='patient_profile',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Patient Profile',
                'verbose_name_plural': 'Patient Profiles',
            },
        ),
        
        # Create ConsentRecord model
        migrations.CreateModel(
            name='ConsentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consent_type', models.CharField(
                    choices=[
                        ('TERMS', 'Terms of Service'),
                        ('PRIVACY', 'Privacy Policy'),
                        ('MEDICAL_DISCLAIMER', 'Medical Disclaimer'),
                        ('DATA_USAGE', 'Data Usage Agreement')
                    ],
                    help_text='Type of consent',
                    max_length=50
                )),
                ('consent_given', models.BooleanField(default=False, help_text='Whether consent was given')),
                ('consent_text', models.TextField(help_text='Full text of consent agreement')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='consents',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Consent Record',
                'verbose_name_plural': 'Consent Records',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create AuditLog model
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(
                    choices=[
                        ('PREDICTION', 'Prediction Made'),
                        ('PROFILE_UPDATE', 'Profile Updated'),
                        ('USER_CREATED', 'User Created'),
                        ('USER_DELETED', 'User Deleted'),
                        ('ROLE_CHANGED', 'Role Changed'),
                        ('PASSWORD_RESET', 'Password Reset'),
                        ('LOGIN', 'User Login'),
                        ('LOGOUT', 'User Logout'),
                        ('EXPORT', 'Data Export'),
                    ],
                    help_text='Type of action performed',
                    max_length=50
                )),
                ('description', models.TextField(help_text='Detailed description of the action')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, help_text='Additional action metadata', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='audit_logs',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Audit Log',
                'verbose_name_plural': 'Audit Logs',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['action_type', '-created_at'], name='audit_action_idx'),
                    models.Index(fields=['user', '-created_at'], name='audit_user_idx'),
                ],
            },
        ),
        
        # Create ChatMessage model
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='User message')),
                ('response', models.TextField(help_text='AI response')),
                ('context', models.JSONField(
                    blank=True,
                    help_text='Prediction context used for response',
                    null=True
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='chat_messages',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Chat Message',
                'verbose_name_plural': 'Chat Messages',
                'ordering': ['created_at'],
            },
        ),
        
        # Add indexes for performance
        migrations.AddIndex(
            model_name='predictionrecord',
            index=models.Index(fields=['user', 'risk_level', '-created_at'], name='pred_user_risk_idx'),
        ),
    ]
