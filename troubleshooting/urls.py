from django.urls import path
from . import views

app_name = 'troubleshooting'

urlpatterns = [
    path('', views.error_code_list_view, name='error_list'),
    path('simulate/', views.simulate_error_view, name='simulate_error'),
    path('<str:code>/', views.error_code_detail_view, name='error_detail'),
]
