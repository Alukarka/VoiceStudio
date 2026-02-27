from django.shortcuts import render
from django.db import models

from exercises.models import ExerciseCategory, PracticalExercise

def _find_category(categories, *keywords):
    keywords = tuple(word.lower() for word in keywords)
    for category in categories:
        name = category.name.lower()
        if any(word in name for word in keywords):
            return category
    return None


def home_page(request):
    categories = list(ExerciseCategory.objects.all())
    speech_category = _find_category(categories, 'техника речи', 'речь', 'speech')
    acting_category = _find_category(categories, 'акт', 'acting')
    literature_category = _find_category(categories, 'литератур', 'чтени', 'literature')
    studio_exercises_count = PracticalExercise.objects.filter(is_active=True).filter(
        (models.Q(video_file__isnull=False) & ~models.Q(video_file='')) | ~models.Q(video_url='')
    ).distinct().count()

    return render(request, 'main/home.html', {
        'title': 'VoiceStudio - Главная',
        'message': 'Добро пожаловать в VoiceStudio!',
        'speech_category': speech_category,
        'acting_category': acting_category,
        'literature_category': literature_category,
        'studio_exercises_count': studio_exercises_count,
    })

def contacts_page(request):
    return render(request, 'main/contacts.html', {
        'title': 'VoiceStudio - Контакты',
    })
