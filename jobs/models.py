from django.db import models
from django.contrib.auth.models import User



# Job Posting Model
from django.contrib.auth.models import User

class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    required_skills = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    employer = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Add default=1

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
    

class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    applied_date = models.DateTimeField(auto_now_add=True)
    similarity_score = models.FloatField(default=0.0)  # Add this line

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"