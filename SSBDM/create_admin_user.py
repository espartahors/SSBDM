import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSBDM.settings')
django.setup()

from django.contrib.auth.models import User

# Create a superuser if one doesn't exist
if not User.objects.filter(username='admin').exists():
    print("Creating admin user...")
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print(f"Admin user created with username 'admin' and password 'admin123'")
else:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print(f"Reset password for admin user to 'admin123'")

# Create a regular user for testing if one doesn't exist
if not User.objects.filter(username='user').exists():
    print("Creating regular user...")
    user = User.objects.create_user(
        username='user',
        email='user@example.com',
        password='user123'
    )
    print(f"Regular user created with username 'user' and password 'user123'")
else:
    user = User.objects.get(username='user')
    user.set_password('user123')
    user.save()
    print(f"Reset password for regular user to 'user123'")

print("User setup complete.") 