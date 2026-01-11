"""
Django management command to set up groups and initial admin user.
Run: python manage.py setup_auth
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from predictor.models import PredictionRecord


class Command(BaseCommand):
    help = 'Set up user groups and create initial admin user'

    def handle(self, *args, **options):
        self.stdout.write('Setting up authentication groups...')
        
        # Create Admin group
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Admin group'))
            
            # Add all permissions to Admin group
            content_type = ContentType.objects.get_for_model(PredictionRecord)
            permissions = Permission.objects.filter(content_type=content_type)
            admin_group.permissions.set(permissions)
            
            # Add User model permissions
            user_content_type = ContentType.objects.get_for_model(User)
            user_permissions = Permission.objects.filter(content_type=user_content_type)
            admin_group.permissions.add(*user_permissions)
            
            self.stdout.write(self.style.SUCCESS('Added permissions to Admin group'))
        else:
            self.stdout.write('Admin group already exists')
        
        # Create User group
        user_group, created = Group.objects.get_or_create(name='User')
        if created:
            self.stdout.write(self.style.SUCCESS('Created User group'))
            
            # Add limited permissions to User group
            view_perm = Permission.objects.get(
                content_type=content_type,
                codename='view_predictionrecord'
            )
            user_group.permissions.add(view_perm)
            
            self.stdout.write(self.style.SUCCESS('Added permissions to User group'))
        else:
            self.stdout.write('User group already exists')
        
        # Create initial admin user
        admin_username = 'admin'
        admin_email = 'admin@example.com'
        admin_password = 'admin123'
        
        if not User.objects.filter(username=admin_username).exists():
            admin_user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            admin_user.groups.add(admin_group)
            
            self.stdout.write(self.style.SUCCESS(
                f'Created admin user: {admin_username} / {admin_password}'
            ))
        else:
            self.stdout.write('Admin user already exists')
        
        # Create test user
        test_username = 'testuser'
        test_password = 'test123'
        
        if not User.objects.filter(username=test_username).exists():
            test_user = User.objects.create_user(
                username=test_username,
                email='test@example.com',
                password=test_password
            )
            test_user.groups.add(user_group)
            
            self.stdout.write(self.style.SUCCESS(
                f'Created test user: {test_username} / {test_password}'
            ))
        else:
            self.stdout.write('Test user already exists')
        
        self.stdout.write(self.style.SUCCESS('\nSetup complete!'))
        self.stdout.write('Admin credentials: admin / admin123')
        self.stdout.write('Test user credentials: testuser / test123')
