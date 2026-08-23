from django.urls import path
from . import views

app_name = 'volunteers'

urlpatterns = [
    path('blood-donors/', views.blood_donors_list, name='blood_donors'),
    path('register-blood-donor/', views.register_blood_donor, name='register_blood_donor'),
    path('apply/', views.apply_volunteer, name='apply'),
]

