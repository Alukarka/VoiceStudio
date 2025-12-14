from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class ExerciseCategory(models.Model):
    """Категории упражнений"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    icon = models.CharField(max_length=50, default="🎭", verbose_name="Иконка")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Категория упражнения"
        verbose_name_plural="Категории упражнений"

class PracticalExercise(models.Model):
    """Практические упражнения"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]

    title = models.CharField(max_length=200, verbose_name = "Название упражнения")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name = "URL-имя")
    category = models.ForeignKey(ExerciseCategory, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    description= models.TextField(verbose_name="Описание")
    instruction= models.TextField(verbose_name="Подробная инструкция")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)    

#Материалы для упражнений

    text_content = models.TextField(blank=True, verbose_name="Текст для озвучки")
    audio_example = models.FileField(upload_to='exercises/examples/',
                                     blank=True, null=True,
                                     verbose_name="Пример аудио")


#Метаданные

    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES,
                                  default= 'beginner', verbose_name="Сложность")
    estimated_time = models.IntegerField(default=5, verbose_name="Примерное время (минуты)")
    is_active = models.BooleanField(default=True, verbose_name = "Активно")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Упражнение"
        verbose_name_plural = "Упражнения"

class UserExerciseAttempt(models.Model):
    """Выполнение упражнения пользователем (попытка)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Пользователь")
    exercise = models.ForeignKey(PracticalExercise, on_delete=models.CASCADE, verbose_name="Упражнение")

    #запись пользователя
    audio_file = models.FileField(upload_to='exercises/attempts/%Y/%m/%d/', verbose_name="Аудиозапись")
    duration= models.IntegerField(default=0, verbose_name="Длительность (секунды)")
    #обратная связь и оценка
    feedback= models.TextField(blank=True, verbose_name="Обратная связь")
    rating = models.IntegerField(choices=[(i, i) for i in range (1, 6)], blank = True,
                                 null=True, verbose_name = "Оценка")
    is_public= models.BooleanField(default=False, verbose_name = "Публичная запись")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} ({self.created_at.date()})"

    class Meta:
        verbose_name="Попытка упражнения"
        verbose_name_plural = "Попытки упражнений"
        ordering = ['-created_at']




# Create your models here.
