from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Создает профили для всех пользователей'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан профиль для {user.username}'))
            else:
                self.stdout.write(f'Профиль уже существует для {user.username}')