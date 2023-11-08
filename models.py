from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20)  # Add any additional fields you need



class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    education_field = models.CharField(max_length=50, blank=True, null=True)
    

    # def __str__(self):
    #     return self.username
    
    def __str__(self):
        return self.user.username if self.user else 'No User'
    


class TechnicianProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    service = models.CharField(max_length=50)  # electrician, plumber, repairer, etc.
    resume = models.FileField(upload_to='technician_resumes/', blank=True, null=True, help_text='Upload a PDF file')
    id_proof = models.ImageField(upload_to='id_proofs/', blank=True, null=True, help_text='Upload an image for ID proof')
    experience = models.PositiveIntegerField(null=True, blank=True)
    district = models.CharField(max_length=50, blank=True, null=True)


    # Additional fields for job application
    tech_first_name = models.CharField(max_length=255, blank=True, null=True)
    tech_last_name = models.CharField(max_length=255, blank=True, null=True)
    tech_email = models.EmailField(blank=True, null=True)
    tech_number = models.CharField(max_length=15, blank=True, null=True)
    # Image field for technician's profile
    tech_image = models.ImageField(upload_to='technician_profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.service}"
    


    


    




