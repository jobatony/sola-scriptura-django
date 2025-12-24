from django.urls import path
from . import views

urlpatterns = [
    
    path('join/', views.join_competition, name='join_competition'),
    path('generate-questions/', views.generate_questions, name='generate_questions'),
    path('api/game/submit-round/', views.submit_round_results, name='submit_round'),
]