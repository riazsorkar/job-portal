from django.db import models

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
    name = models.CharField(max_length=100)  # User's name
    email = models.EmailField(unique=True)  # User's email
    skills = models.TextField()  # User's skills (comma-separated)

    def __str__(self):
        return self.name  # Display user's name in the admin panel