"""
Management command to create admin users.
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Create an admin user with Admin group privileges'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        
        # If arguments not provided, prompt for them
        if not username:
            username = input('Admin username: ')
        if not email:
            email = input('Admin email: ')
        if not password:
            password = input('Admin password: ')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists!'))
            return
        
        # Create the admin user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )
        
        # Get or create Admin group
        admin_group, created = Group.objects.get_or_create(name='Admin')
        user.groups.add(admin_group)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Group: Admin'))
        self.stdout.write(self.style.WARNING('This user can login at: /auth/admin-login/'))
