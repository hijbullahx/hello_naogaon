from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('<int:pk>/', views.program_detail, name='program_detail'),
    path('events/', views.event_list, name='event_list'),
    path('success-stories/', views.success_stories, name='success_stories'),
]
