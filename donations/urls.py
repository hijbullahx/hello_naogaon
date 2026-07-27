from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('donate/', views.donation_page_view, name='donate'),
]
