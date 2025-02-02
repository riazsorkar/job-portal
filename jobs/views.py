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

from django.db.models import Q

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



@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()  # Save the job posting to the database
            return redirect('home')  # Redirect to the homepage
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