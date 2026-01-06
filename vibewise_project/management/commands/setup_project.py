from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserPreferences

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up the project with initial data'
    
    def handle(self, *args, **options):
        # Create superuser if it doesn't exist
        if not User.objects.filter(email='admin@vibewise.com').exists():
            User.objects.create_superuser(
                username='admin@vibewise.com',
                email='admin@vibewise.com',
                password='admin123',
                name='Admin User'
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin@vibewise.com / admin123')
            )
        
        # Create test user
        if not User.objects.filter(email='test@vibewise.com').exists():
            user = User.objects.create_user(
                username='test@vibewise.com',
                email='test@vibewise.com',
                password='test123',
                name='Test User'
            )
            UserPreferences.objects.create(user=user)
            self.stdout.write(
                self.style.SUCCESS('Created test user: test@vibewise.com / test123')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Project setup completed successfully!')
        )