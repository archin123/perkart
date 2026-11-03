from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/verify/', views.submit_verification_view, name='submit_verification'),
    path('admin/verifications/', views.admin_verification_dashboard, name='admin_verifications'),
    path('admin/verifications/<int:pk>/<str:action>/', views.admin_update_verification, name='admin_update_verification'),
]
