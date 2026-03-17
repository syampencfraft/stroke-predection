from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('predict/', views.predict, name='predict'),
    path('history/', views.history, name='history'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('doctor/register/', views.doctor_register, name='doctor_register'),
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-doctor/<int:pk>/', views.approve_doctor, name='approve_doctor'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/profile/edit/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('appointment/handle/<int:pk>/<str:action>/', views.handle_appointment, name='handle_appointment'),
    path('doctor/view/<int:pk>/', views.view_doctor_profile, name='view_doctor_profile'),
]
