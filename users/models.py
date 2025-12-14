from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from exercises.models import PracticalExercise


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    location = models.CharField(max_length = 100, blank=True, verbose_name="Город")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар",
                               default='avatars/default_avatar.png')
    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name="Профиль пользователя"
        verbose_name_plural="Профили пользователей"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    achievement_type = models.CharField(max_length=50, verbose_name='Тип достижения')
    exercise = models.ForeignKey('exercises.PracticalExercise', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Упражнение')
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения')

    def __str__(self):
        return f'{self.user.username} - {self.achievement_type}'

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'


# Create your models here.
