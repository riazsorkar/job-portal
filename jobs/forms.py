from django import forms
from .models import UserProfile
from .models import JobPosting
from .models import JobApplication

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'skills']


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'location', 'required_skills']



class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'skills']


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'resume']

from .models import JobApplication

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status']