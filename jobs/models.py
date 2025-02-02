from django.db import models
from django.contrib.auth.models import User



# Job Posting Model
class JobPosting(models.Model):
    title = models.CharField(max_length=200)  # Job title
    description = models.TextField()  # Job description
    location = models.CharField(max_length=100)  # Job location
    required_skills = models.TextField()  # Required skills (comma-separated)
    posted_date = models.DateTimeField(auto_now_add=True)  # Automatically set when job is posted

    def __str__(self):
        return self.title  # Display job title in the admin panel

# User Profile Model (Simple version)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    skills = models.TextField()

    def __str__(self):
        return self.name
    




class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)  # Link to the job
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the applicant
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')  # Store resumes in a 'resumes' folder
    applied_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"