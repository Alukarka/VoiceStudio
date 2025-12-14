from django.db import models
from django.urls import reverse

# Create your models here.

class VoiceStudio(models.Model):
    '''Название моей модели, типичный класс модели, производный от класса Model.'''

    my_field_name = models.CharField(max_length=20, help_text='Введите описание поля')

class Meta:
    ordering = ['-my_field_name']

def get_absolute_url(self):
    return reverse('model-detail-view', args=[str(self.id)])

def __str__(self):
    return self.my_field_name

