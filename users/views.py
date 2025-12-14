from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from users.models import UserProfile
from django.db.models import Count, Avg
from exercises.models import UserExerciseAttempt, PracticalExercise, ExerciseCategory
from django.utils import timezone
from datetime import timedelta

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Профиль создастся автоматически через сигнал
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('users:profile')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('users:profile')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
def profile(request):
    # Получаем профиль пользователя
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES,
                                         instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile.html', context)


def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')

@login_required
def user_dashboard(request):
    user_attempts = UserExerciseAttempt.objects.filter(user=request.user).order_by('-created_at')
    total_attempts = user_attempts.count()
    completed_exercises = user_attempts.values('exercise').distinct().count()
    avg_rating = user_attempts.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else None
    category_stats = []
    categories = ExerciseCategory.objects.all()
    for category in categories:
        exercises_in_category = PracticalExercise.objects.filter(category=category, is_active=True)
        attempts_in_category = user_attempts.filter(exercise__category=category)

        if attempts_in_category.exists():
            category_stats.append({
                'category': category,
                'attempts_count': attempts_in_category.count(),
                'exercises_count': exercises_in_category.count(),
                'progress': min(100, (attempts_in_category.count() / max(1, exercises_in_category.count())) * 100),
            })

    recent_attempts = user_attempts[:5]

    top_rated_attempts = user_attempts.filter(rating__isnull=False).order_by('-rating')[:3]

    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_days = UserExerciseAttempt.objects.filter(user=request.user).filter(
        user=request.user,
        created_at__gte=thirty_days_ago).dates('created_at', 'day').distinct().count()

    context = {
        'user_attempts': user_attempts,
        'total_attempts': total_attempts,
        'completed_exercises': completed_exercises,
        'avg_rating': avg_rating,
        'category_stats': category_stats,
        'recent_attempts': recent_attempts,
        'top_rated_attempts': top_rated_attempts,
        'active_days': active_days,
        }

    return render(request, 'users/dashboard.html', context)