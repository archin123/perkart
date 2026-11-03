from django.urls import path
from . import views

app_name = 'faq'

urlpatterns = [
    path('', views.faq_list_view, name='faq_list'),
    path('vote/<int:faq_id>/', views.faq_vote_view, name='faq_vote'),
]
