import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Predictor.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

username = '22bcon1163'
password = 'Kalpana@1163'

# Get user
try:
    user = User.objects.get(username=username)
    print(f"✓ User found: {user.username}")
    print(f"✓ Email: {user.email}")
    print(f"✓ Is active: {user.is_active}")
    print(f"✓ Is staff: {user.is_staff}")
    print(f"✓ Is superuser: {user.is_superuser}")
    print(f"✓ Groups: {list(user.groups.values_list('name', flat=True))}")
    print()
    
    # Test authentication
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print(f"✓ Authentication successful!")
        print(f"✓ User can login with these credentials")
    else:
        print("✗ Authentication failed!")
        print("✗ Password might be incorrect")
        print()
        print("Resetting password to: Kalpana@1163")
        user.set_password('Kalpana@1163')
        user.save()
        print("✓ Password reset complete. Try logging in again.")
        
except User.DoesNotExist:
    print(f"✗ User '{username}' not found!")
