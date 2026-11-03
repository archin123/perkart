from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.assistant_page_view, name='assistant'),
    path('api/chat/', views.assistant_api_view, name='api_chat'),
    path('api/clear/', views.clear_history_view, name='api_clear'),
]
