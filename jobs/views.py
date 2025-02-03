from django.shortcuts import render
from .models import JobPosting
from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .forms import JobPostingForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UpdateProfileForm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import JobPosting, UserProfile
from .models import JobPosting, JobApplication
import os
import zipfile
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q

from django.core.paginator import Paginator

from django.shortcuts import render, redirect, get_object_or_404
from .models import JobPosting, JobApplication
from .forms import JobApplicationForm

def home(request):
    query = request.GET.get('q')  # Get the search query
    if query:
        # Filter jobs by title, location, or required skills
        jobs = JobPosting.objects.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(required_skills__icontains=query)
        )
    else:
        jobs = JobPosting.objects.all()  # Show all jobs if no query

    # Add pagination
    paginator = Paginator(jobs, 4)  # Show 5 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/home.html', {'page_obj': page_obj})



def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()  # Save the profile to the database
            return redirect('home')  # Redirect to the homepage
    else:
        form = UserProfileForm()
    return render(request, 'jobs/create_profile.html', {'form': form})



@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user  # Set the employer to the logged-in user
            job.save()
            return redirect('home')
    else:
        form = JobPostingForm()
    return render(request, 'jobs/post_job.html', {'form': form})



@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'jobs/profile.html', {'profile': user_profile})

@login_required
def update_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UpdateProfileForm(instance=user_profile)
    return render(request, 'jobs/update_profile.html', {'form': form})

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    recommended_jobs = recommend_jobs(user_profile)

    # Perform skill gap analysis for the top recommended job
    if recommended_jobs:
        top_job = recommended_jobs[0][0]
        skill_gap_suggestions = skill_gap_analysis(user_profile, top_job)
    else:
        skill_gap_suggestions = []

    return render(request, 'jobs/dashboard.html', {
        'profile': user_profile,
        'recommended_jobs': recommended_jobs,
        'skill_gap_suggestions': skill_gap_suggestions
    })




def recommend_jobs(user_profile):
    # Get all job postings
    jobs = JobPosting.objects.all()

    # Extract skills from the user profile and job postings
    user_skills = user_profile.skills
    job_skills = [job.required_skills for job in jobs]

    # Combine user skills and job skills into a single list
    all_skills = [user_skills] + job_skills

    # Convert skills into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_skills)

    # Calculate cosine similarity between user skills and job skills
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Sort jobs by similarity score
    recommended_jobs = sorted(zip(jobs, cosine_similarities), key=lambda x: x[1], reverse=True)

    # Return the top 5 recommended jobs
    return recommended_jobs[:5]




def skill_gap_analysis(user_profile, job):
    user_skills = set(user_profile.skills.lower().split(','))
    required_skills = set(job.required_skills.lower().split(','))

    # Find missing skills
    missing_skills = required_skills - user_skills

    # Suggest courses for missing skills (dummy data for now)
    courses = {
        'python': 'https://www.coursera.org/learn/python',
        'machine learning': 'https://www.coursera.org/learn/machine-learning',
        'project management': 'https://www.coursera.org/learn/project-management',
        # Add more skills and courses as needed
    }

    # Get course suggestions for missing skills
    suggestions = []
    for skill in missing_skills:
        if skill.strip() in courses:
            suggestions.append({
                'skill': skill.strip(),
                'course': courses[skill.strip()]
            })

    return suggestions





def apply_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user

            # Calculate similarity score
            job_requirements = job.required_skills
            resume_text = "Extract text from the resume here"  # Replace with actual resume text extraction
            texts = [job_requirements, resume_text]

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()[0]

            application.similarity_score = similarity
            application.save()
            return redirect('home')
    else:
        form = JobApplicationForm()

    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})



@login_required
def employer_dashboard(request):
    # Get all job postings created by the logged-in employer
    jobs = JobPosting.objects.filter(employer=request.user)
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})






@login_required
def view_applications(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, employer=request.user)
    applications = JobApplication.objects.filter(job=job)

    # Handle search query
    search_query = request.GET.get('q')
    if search_query:
        applications = applications.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Handle similarity score filter
    min_score = request.GET.get('min_score')
    if min_score:
        applications = applications.filter(similarity_score__gte=float(min_score))

    # Handle "Download All CVs" request
    if 'download_all' in request.GET:
        zip_filename = f"job_{job_id}_resumes.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for application in applications:
                resume_path = application.resume.path
                zipf.write(resume_path, os.path.basename(resume_path))

        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={zip_filename}'
            return response

    # Add pagination
    paginator = Paginator(applications, 4)  # Show 5 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/view_applications.html', {'job': job, 'page_obj': page_obj})


from django.shortcuts import get_object_or_404, redirect
from .forms import StatusUpdateForm

@login_required
def update_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, job__employer=request.user)

    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect('view_applications', job_id=application.job.id)
    else:
        form = StatusUpdateForm(instance=application)

    return render(request, 'jobs/update_status.html', {'form': form, 'application': application})