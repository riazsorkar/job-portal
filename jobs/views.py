from django.shortcuts import render
from .models import JobPosting
from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .forms import JobPostingForm

def home(request):
    jobs = JobPosting.objects.all()  # Get all job postings
    return render(request, 'jobs/home.html', {'jobs': jobs})


def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()  # Save the profile to the database
            return redirect('home')  # Redirect to the homepage
    else:
        form = UserProfileForm()
    return render(request, 'jobs/create_profile.html', {'form': form})



def post_job(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()  # Save the job posting to the database
            return redirect('home')  # Redirect to the homepage
    else:
        form = JobPostingForm()
    return render(request, 'jobs/post_job.html', {'form': form})