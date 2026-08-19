from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('donate/', views.donation_page_view, name='donate'),
    path('program-donation/', views.submit_program_donation, name='program_donation'),
]
