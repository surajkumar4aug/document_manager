from django.urls import path
from .views import manage_profile_and_files_view, dashboard_view, custom_password_change,logout_view
from .views import  CustomLoginView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', manage_profile_and_files_view, name='manage_profile_and_files'),
     path('login/', CustomLoginView.as_view(), name='login'),
    
    # Password change view
     path('logout/', logout_view, name='logout'),
    path('password_change/', custom_password_change, name='password_change'),
    
    path('dashboard/', dashboard_view, name='dashboard'),

]
