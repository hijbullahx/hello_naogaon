from django.urls import path
from . import views, views_dashboard

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    
    # Custom Section-by-Section Card Control Admin Dashboard
    path('dashboard/', views_dashboard.dashboard_home, name='dashboard'),
    path('dashboard/update-hero/', views_dashboard.update_hero_section, name='update_hero'),
    path('dashboard/update-about/', views_dashboard.update_about_section, name='update_about'),
    path('dashboard/delete-about-image/<int:pk>/', views_dashboard.delete_about_image, name='delete_about_image'),
    path('dashboard/update-stats/', views_dashboard.update_stat_counters, name='update_stats'),
    path('dashboard/save-program/', views_dashboard.save_program, name='save_program'),
    path('dashboard/delete-program/<int:pk>/', views_dashboard.delete_program, name='delete_program'),
    path('dashboard/save-news/', views_dashboard.save_news, name='save_news'),
    path('dashboard/delete-news/<int:pk>/', views_dashboard.delete_news, name='delete_news'),
    path('dashboard/update-bank/', views_dashboard.update_bank_and_donation, name='update_bank'),
    path('dashboard/update-donation-content/', views_dashboard.update_donation_page_content, name='update_donation_content'),
    path('dashboard/save-campaign/', views_dashboard.save_campaign, name='save_campaign'),
    path('dashboard/delete-campaign/<int:pk>/', views_dashboard.delete_campaign, name='delete_campaign'),
    path('dashboard/save-emergency-appeal/', views_dashboard.save_emergency_appeal, name='save_emergency_appeal'),
    path('dashboard/delete-emergency-appeal/<int:pk>/', views_dashboard.delete_emergency_appeal, name='delete_emergency_appeal'),
    path('dashboard/save-impact/', views_dashboard.save_donation_impact, name='save_impact'),
    path('dashboard/delete-impact/<int:pk>/', views_dashboard.delete_donation_impact, name='delete_impact'),
    path('dashboard/save-faq/', views_dashboard.save_faq, name='save_faq'),
    path('dashboard/delete-faq/<int:pk>/', views_dashboard.delete_faq, name='delete_faq'),
    path('dashboard/save-donor/', views_dashboard.save_donor, name='save_donor'),
    path('dashboard/delete-donor/<int:pk>/', views_dashboard.delete_donor, name='delete_donor'),
    path('dashboard/save-volunteer/', views_dashboard.save_volunteer, name='save_volunteer'),
    path('dashboard/delete-volunteer/<int:pk>/', views_dashboard.delete_volunteer, name='delete_volunteer'),
    path('dashboard/save-team-member/', views_dashboard.save_team_member, name='save_team_member'),
    path('dashboard/delete-team-member/<int:pk>/', views_dashboard.delete_team_member, name='delete_team_member'),
    path('dashboard/save-transaction/', views_dashboard.save_financial_transaction, name='save_transaction'),
    path('dashboard/delete-transaction/<int:pk>/', views_dashboard.delete_financial_transaction, name='delete_transaction'),
    path('dashboard/export-excel/', views_dashboard.export_financial_excel, name='export_excel'),
    path('dashboard/print-statement/', views_dashboard.print_financial_statement, name='print_statement'),
    path('dashboard/save-gallery/', views_dashboard.save_gallery_photo, name='save_gallery'),
    path('dashboard/update-footer/', views_dashboard.update_footer_section, name='update_footer'),
]

