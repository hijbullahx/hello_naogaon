from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donation_page_view, name='index'),
    path('donate/', views.donation_page_view, name='donate'),
    path('submit/', views.submit_donation, name='submit'),
    path('program-donation/', views.submit_program_donation, name='program_donation'),
]
