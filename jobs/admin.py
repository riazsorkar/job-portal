from django.contrib import admin
from .models import JobPosting, UserProfile

# Register your models here
admin.site.register(JobPosting)
admin.site.register(UserProfile)