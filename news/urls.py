from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='article_list'),
    path('', views.news_list, name='news_list'),
    path('<int:pk>/', views.news_detail, name='article_detail'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
]

