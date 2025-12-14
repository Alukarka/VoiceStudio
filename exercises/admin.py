from django.contrib import admin
from .models import ExerciseCategory, PracticalExercise, UserExerciseAttempt

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'exercise_count']
    search_fields = ['name']
    list_per_page = 20
    def exercise_count(self, obj):
        return obj.practicalexercise_set.count()
    exercise_count.short_description = 'Количество упражнений'

@admin.register(PracticalExercise)
class PracticalExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'estimated_time', 'is_active', 'created_at']
    list_filter = ['category', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'category__name']
    list_editable = ['is_active', 'difficulty', 'estimated_time']
    list_per_page = 20

    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'category', 'description', 'instruction')
            }),
        ('Материалы для упражнения', {
            'fields': ('text_content', 'audio_example'),
            'classes': ('collapse',),
            }),
        ('Настройки', {
            'fields': ('difficulty', 'estimated_time', 'is_active')
            }),
        ('Дополнительно', {
         'fields': ('created_at', 'updated_at'),
         'classes': ('collapse',)}),
    )

    readonly_fields = ['created_at', 'updated_at']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'category':
            kwargs["queryset"] = ExerciseCategory.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(UserExerciseAttempt)
class UserExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'category', 'rating', 'created_at']
    list_filter = ['exercise__category', 'rating', 'created_at']
    search_fields = ['user__username', 'exercise__title']
    readonly_fields = ['created_at']
    list_per_page = 20

    def category(self, obj):
        return obj.exercise.category.name if obj.exercise.category else '-'
    category.short_description = 'Категория'
    category.admin_order_field = 'exercise__category__name'


# Register your models here.
