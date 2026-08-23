from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donation_page_view, name='index'),
    path('donate/', views.donation_page_view, name='donate'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-fail/', views.payment_fail, name='payment_fail'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment-ipn/', views.payment_ipn, name='payment_ipn'),
    path('receipt/<int:donation_id>/', views.donation_receipt_view, name='receipt'),
    path('submit/', views.submit_donation, name='submit'),
    path('program-donation/', views.submit_program_donation, name='program_donation'),
    path('api/member-pledge/', views.member_pledge_lookup, name='member_pledge_lookup'),
]
