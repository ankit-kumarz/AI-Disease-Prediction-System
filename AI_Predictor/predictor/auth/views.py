"""
Authentication views for login, signup, and logout.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm


def signup_view(request):
    """
    User signup page.
    Creates a new user account with 'User' role.
    """
    if request.user.is_authenticated:
        # Already logged in, redirect to home
        return redirect('home')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('auth_login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    
    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    """
    User login page (for regular users only).
    Admins should use /auth/admin-login/
    """
    if request.user.is_authenticated:
        # Already logged in
        if request.user.groups.filter(name='Admin').exists() or request.user.is_superuser:
            return redirect('admin_dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is trying to login as regular user but is admin
                if user.groups.filter(name='Admin').exists() or user.is_superuser:
                    messages.error(request, 'Admin users must use the admin login page.')
                    return redirect('admin_login')
                
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form, 'login_type': 'user'})


def admin_login_view(request):
    """
    Admin login page (for admins and superusers only).
    Regular users should use /auth/login/
    """
    if request.user.is_authenticated:
        # Already logged in
        if request.user.groups.filter(name='Admin').exists() or request.user.is_superuser:
            return redirect('admin_dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user has admin privileges
                if not (user.groups.filter(name='Admin').exists() or user.is_superuser):
                    messages.error(request, 'You do not have admin privileges. Please use the regular user login.')
                    return redirect('auth_login')
                
                login(request, user)
                messages.success(request, f'Welcome back, Admin {username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid admin credentials.')
        else:
            messages.error(request, 'Invalid admin credentials.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/admin_login.html', {'form': form, 'login_type': 'admin'})


@login_required
def logout_view(request):
    """
    Logout current user and redirect to home page.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


def unauthorized_view(request):
    """
    Page shown when user tries to access restricted content.
    """
    return render(request, 'auth/unauthorized.html', status=403)
