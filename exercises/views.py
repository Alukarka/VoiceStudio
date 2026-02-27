from django.shortcuts import render, get_object_or_404, redirect
from .models import ExerciseCategory, PracticalExercise, UserExerciseAttempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .forms import AudioUploadForm


def _video_enabled_exercises_queryset():
    return PracticalExercise.objects.filter(is_active=True).filter(
        (Q(video_file__isnull=False) & ~Q(video_file='')) | ~Q(video_url='')
    ).distinct()


def exercises_list(request):
    category_filter = request.GET.get('category')
    categories = ExerciseCategory.objects.annotate(
        active_exercises_count=Count('practicalexercise', filter=Q(practicalexercise__is_active=True))
    )
    exercises = PracticalExercise.objects.filter(is_active=True)
    selected_category = None

    if category_filter:
        if category_filter.isdigit():
            selected_category = categories.filter(id=int(category_filter)).first()
        else:
            selected_category = categories.filter(name__iexact=category_filter).first()

        if selected_category:
            exercises = exercises.filter(category=selected_category)

    return render(request, 'exercises/list.html', {
        'categories': categories,
        'exercises': exercises,
        'selected_category': selected_category,
        'selected_category_id': selected_category.id if selected_category else None,
    })

def studio_exercises_list(request):
    exercises = _video_enabled_exercises_queryset()

    return render(request, 'exercises/studio_list.html', {
        'exercises': exercises,
    })


def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(PracticalExercise, id=exercise_id, is_active=True)
    has_studio = bool(exercise.video_file or exercise.video_url)
    return render(request, 'exercises/detail.html', {
        'exercise': exercise,
        'has_studio': has_studio,
    })

def exercises_by_category(request, category_id):
    category = get_object_or_404(ExerciseCategory, id=category_id)
    exercises = PracticalExercise.objects.filter(category=category, is_active=True)
    all_categories = ExerciseCategory.objects.all()

    return render(request, 'exercises/by_category.html', {
        'exercises': exercises,
        'category': category,
        'all_categories': all_categories,
    })

def record_attempt(request, exercise_id):
    exercise = get_object_or_404(PracticalExercise, id=exercise_id, is_active=True)

    if not request.user.is_authenticated:
        messages.warning(request, 'Чтобы начать упражнение - Вам нужно авторизоваться :)')
        return redirect('exercises:detail', exercise_id=exercise.id)

    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            attempt = form.save(commit=False)
            attempt.exercise = exercise
            attempt.user = request.user
            if 'audio_file' in request.FILES:
                audio_file = request.FILES['audio_file']
                allowed_extensions = ('.wav', '.mp3', '.ogg', '.m4a', '.webm', '.flac', '.aiff', '.aac')
                if not audio_file.name.lower().endswith(allowed_extensions):
                    messages.error(request, 'Неподдерживаемый формат аудио. Используйте файлы с расширениями: WAV, MP3, OGG, M4A или WEBM')
                else:
                    attempt.save()
                    messages.success(request, 'Запись успешно сохранена!')
                    return redirect('exercises:attempt_detail', attempt_id=attempt.id)
            else:
                messages.error(request, 'Аудиофайл не найден. Попробуйте еще раз.')
    else:
        form = AudioUploadForm()

    studio_exercises = _video_enabled_exercises_queryset().exclude(id=exercise.id)[:6]

    return render(request, 'exercises/record.html', {
        'exercise': exercise,
        'form': form,
        'studio_exercises': studio_exercises,
    })

def studio_session(request, exercise_id):
    exercise = get_object_or_404(PracticalExercise, id=exercise_id, is_active=True)

    if not request.user.is_authenticated:
        messages.warning(request, 'Чтобы начать упражнение - Вам нужно авторизоваться')
        return redirect('exercises:detail', exercise_id=exercise.id)

    if not exercise.video_file and not exercise.video_url:
        messages.info(request, 'Для этого упражнения пока не добавлено видео для виртуальной студии.')
        return redirect('exercises:detail', exercise_id=exercise.id)

    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            attempt = form.save(commit=False)
            attempt.exercise = exercise
            attempt.user = request.user
            if 'audio_file' in request.FILES:
                audio_file = request.FILES['audio_file']
                allowed_extensions = ('.wav', '.mp3', '.ogg', '.m4a', '.webm', '.flac', '.aiff', '.aac')
                if not audio_file.name.lower().endswith(allowed_extensions):
                    messages.error(request, 'Неподдерживаемый формат аудио. Используйте файлы с расширениями: WAV, MP3, OGG, M4A или WEBM')
                else:
                    attempt.save()
                    messages.success(request, 'Дубляж успешно сохранен!')
                    return redirect('exercises:attempt_detail', attempt_id=attempt.id)
            else:
                messages.error(request, 'Аудиофайл не найден. Попробуйте еще раз.')
    else:
        form = AudioUploadForm()

    return render(request, 'exercises/studio.html', {
        'exercise': exercise,
        'form': form,
    })


@login_required
def attempt_detail(request, attempt_id):
    attempt = get_object_or_404(UserExerciseAttempt, id=attempt_id)
    #проверка записи(пользователя или публичная)
    if attempt.user != request.user and not request.is_public:
        return redirect('exercises:list')
    return render(request, 'exercises/attempt_detail.html', {
        'attempt': attempt,
    })

@login_required
def delete_attempt(request, attempt_id):
    attempt = get_object_or_404(UserExerciseAttempt, id=attempt_id)
    if attempt.user != request.user:
        messages.error(request, 'Вы не можете удалить эту запись.')
        return redirect('exercises:list')
    if request.method == 'POST':
        exercise_id = attempt.exercise.id
        attempt.delete()
        messages.success(request, 'Запись удалена.')
        return redirect('exercises:detail', exercise_id=exercise_id)
    return redirect('exercises:attempt_detail', attempt_id=attempt_id)

@login_required
def toggle_public(request, attempt_id):
    attempt = get_object_or_404(UserExerciseAttempt, id=attempt_id)
    if attempt.user != request.user:
        messages.error(request, 'Вы не можете изменить настройки этой записи.')

    attempt_is_public = not attempt.is_public
    attempt.save()

    status = "публичной" if attempt.is_public else "приватной"
    messages.success(request, f'Запись теперь {status}')

    return redirect('exercises:attempt_detail', attempt_id=attempt_id)
