from django.urls import path
from . import views

app_name="exercises"

urlpatterns=[
    path('',views.exercises_list, name='list'),
    path('category/<int:category_id>',views.exercises_by_category, name='by_category'),
    path('<int:exercise_id>/',views.exercise_detail, name='detail'),
    path('<int:exercise_id>/record/',views.record_attempt, name='record'),
    path('attempt/<int:attempt_id>/',views.attempt_detail, name='attempt_detail'),
    path('attempt/<int:attempt_id>/delete/', views.delete_attempt, name='delete_attempt'),
    path('attempt/<int:attempt_id>/toggle-public/',views.toggle_public, name='toggle_public'),
]
