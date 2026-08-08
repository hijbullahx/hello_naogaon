from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='article_list'),
    path('<int:pk>/', views.news_detail, name='article_detail'),
]

