from django.shortcuts import render
from .models import JobPosting

def home(request):
    jobs = JobPosting.objects.all()  # Get all job postings
    return render(request, 'jobs/home.html', {'jobs': jobs})