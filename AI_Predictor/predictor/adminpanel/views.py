"""
Admin panel views for user management, analytics, and predictions.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
from predictor.models import PredictionRecord


def is_admin(user):
    """Check if user is in Admin group."""
    return user.groups.filter(name='Admin').exists()


@login_required
@user_passes_test(is_admin, login_url='/auth/unauthorized/')
def dashboard_view(request):
    """
    Admin dashboard with analytics and statistics.
    """
    # Get statistics
    total_users = User.objects.count()
    total_predictions = PredictionRecord.objects.count()
    
    # Predictions by disease
    disease_stats = PredictionRecord.objects.values('disease').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent predictions (last 10)
    recent_predictions = PredictionRecord.objects.select_related('user').order_by('-created_at')[:10]
    
    # Predictions over time (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    predictions_by_date = PredictionRecord.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra(
        select={'date': 'DATE(created_at)'}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # User activity
    active_users = User.objects.filter(
        predictions__created_at__gte=thirty_days_ago
    ).distinct().count()
    
    context = {
        'total_users': total_users,
        'total_predictions': total_predictions,
        'disease_stats': disease_stats,
        'recent_predictions': recent_predictions,
        'predictions_by_date': list(predictions_by_date),
        'active_users': active_users,
    }
    
    return render(request, 'adminpanel/dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='/auth/unauthorized/')
def users_view(request):
    """
    User management page - view, add, delete, edit users.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_user':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role', 'User')
            
            if username and email and password:
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                    # Assign group
                    group, created = Group.objects.get_or_create(name=role)
                    user.groups.add(group)
                    messages.success(request, f'User {username} created successfully!')
                except Exception as e:
                    messages.error(request, f'Error creating user: {str(e)}')
            else:
                messages.error(request, 'All fields are required!')
        
        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if user != request.user:  # Don't allow deleting self
                    user.delete()
                    messages.success(request, 'User deleted successfully!')
                else:
                    messages.error(request, 'Cannot delete your own account!')
            except User.DoesNotExist:
                messages.error(request, 'User not found!')
        
        elif action == 'change_role':
            user_id = request.POST.get('user_id')
            new_role = request.POST.get('new_role')
            try:
                user = User.objects.get(id=user_id)
                # Remove all groups and add new one
                user.groups.clear()
                group, created = Group.objects.get_or_create(name=new_role)
                user.groups.add(group)
                messages.success(request, f'Role changed to {new_role}!')
            except User.DoesNotExist:
                messages.error(request, 'User not found!')
        
        elif action == 'reset_password':
            user_id = request.POST.get('user_id')
            new_password = request.POST.get('new_password')
            try:
                user = User.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successfully!')
            except User.DoesNotExist:
                messages.error(request, 'User not found!')
        
        return redirect('admin_users')
    
    # Get all users with their groups and prediction counts
    users = User.objects.annotate(
        prediction_count=Count('predictions')
    ).prefetch_related('groups').order_by('-date_joined')
    
    context = {
        'users': users,
    }
    
    return render(request, 'adminpanel/users.html', context)


@login_required
@user_passes_test(is_admin, login_url='/auth/unauthorized/')
def predictions_view(request):
    """
    View all predictions with filters.
    Admin can see all user predictions.
    """
    # Get filter parameters
    disease_filter = request.GET.get('disease', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Start with all predictions
    predictions = PredictionRecord.objects.select_related('user').all()
    
    # Apply filters
    if disease_filter:
        predictions = predictions.filter(disease=disease_filter)
    
    if user_filter:
        predictions = predictions.filter(user__username__icontains=user_filter)
    
    if date_from:
        predictions = predictions.filter(created_at__gte=date_from)
    
    if date_to:
        predictions = predictions.filter(created_at__lte=date_to)
    
    predictions = predictions.order_by('-created_at')
    
    # Get unique diseases and users for filter dropdowns
    diseases = PredictionRecord.objects.values_list('disease', flat=True).distinct()
    users = User.objects.filter(predictions__isnull=False).distinct()
    
    context = {
        'predictions': predictions,
        'diseases': diseases,
        'users': users,
        'current_disease': disease_filter,
        'current_user': user_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'adminpanel/predictions.html', context)


@login_required
@user_passes_test(is_admin, login_url='/auth/unauthorized/')
def export_predictions_csv(request):
    """
    Export all predictions to CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="predictions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Disease', 'Prediction', 'Probability', 'Date'])
    
    # Get filtered predictions (same as predictions_view)
    disease_filter = request.GET.get('disease', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    predictions = PredictionRecord.objects.select_related('user').all()
    
    if disease_filter:
        predictions = predictions.filter(disease=disease_filter)
    if user_filter:
        predictions = predictions.filter(user__username__icontains=user_filter)
    if date_from:
        predictions = predictions.filter(created_at__gte=date_from)
    if date_to:
        predictions = predictions.filter(created_at__lte=date_to)
    
    for pred in predictions:
        writer.writerow([
            pred.id,
            pred.user.username if pred.user else 'Anonymous',
            pred.disease,
            pred.prediction_label,
            f'{pred.probability:.2%}',
            pred.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
@user_passes_test(is_admin, login_url='/auth/unauthorized/')
def analytics_view(request):
    """
    Advanced analytics page with detailed charts and statistics.
    """
    # Disease distribution
    disease_distribution = PredictionRecord.objects.values('disease').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Prediction outcomes by disease
    outcomes_by_disease = {}
    for disease in ['diabetes', 'heart', 'breast']:
        outcomes = PredictionRecord.objects.filter(disease=disease).values(
            'prediction_label'
        ).annotate(count=Count('id'))
        outcomes_by_disease[disease] = list(outcomes)
    
    # User activity
    user_activity = User.objects.annotate(
        pred_count=Count('predictions')
    ).filter(pred_count__gt=0).order_by('-pred_count')[:10]
    
    # Predictions trend (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_predictions = PredictionRecord.objects.filter(
        created_at__gte=twelve_months_ago
    ).extra(
        select={'month': 'strftime("%%Y-%%m", created_at)'}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    context = {
        'disease_distribution': disease_distribution,
        'outcomes_by_disease': outcomes_by_disease,
        'user_activity': user_activity,
        'monthly_predictions': list(monthly_predictions),
    }
    
    return render(request, 'adminpanel/analytics.html', context)
