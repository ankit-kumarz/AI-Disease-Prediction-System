import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Predictor.settings')
django.setup()

from django.contrib.auth.models import User, Group

username = '22bcon1163'
user = User.objects.get(username=username)

# Create Admin group if it doesn't exist
admin_group, created = Group.objects.get_or_create(name='Admin')

# Add user to Admin group
user.groups.clear()  # Clear existing groups
user.groups.add(admin_group)

# Make user staff
user.is_staff = True
user.save()

print(f"✓ User '{username}' is now an admin!")
print(f"✓ Groups: {list(user.groups.values_list('name', flat=True))}")
print(f"✓ Is staff: {user.is_staff}")
print(f"\nYou can now login at: http://127.0.0.1:8000/auth/admin-login/")
