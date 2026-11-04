from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.global_search_view, name='global_search'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('health/', views.health_check_view, name='health_check'),
    path('status/', views.system_status_view, name='system_status'),
    path('rubric/', views.evaluation_rubric_view, name='evaluation_rubric'),
]
