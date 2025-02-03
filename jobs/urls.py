from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('post-job/', views.post_job, name='post_job'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
     path('employer-dashboard/', views.employer_dashboard, name='employer_dashboard'),  # Add this line
    path('view-applications/<int:job_id>/', views.view_applications, name='view_applications'),
]