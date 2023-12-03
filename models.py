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
    is_approved = models.BooleanField(default=False)  # New field for approval status

    def __str__(self):
        return f"{self.user.username} - {self.service}"
    


    
class ApprovedTechnician(models.Model):
    technician_profile = models.OneToOneField(TechnicianProfile, on_delete=models.CASCADE)
    approved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Approved Technician: {self.technician_profile.tech_first_name} {self.technician_profile.tech_last_name}"



from django.utils import timezone

class TechnicianAvailability(models.Model):
    approved_technician = models.ForeignKey(ApprovedTechnician, on_delete=models.CASCADE)
    technician_profile = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE)
    date = models.DateField()
    availability_choices = [
        ('FN', 'Before Noon'),
        ('AN', 'After Noon'),
        ('FullDay', 'Full Day'),
    ]
    availability = models.CharField(max_length=10, choices=availability_choices)

    def save(self, *args, **kwargs):
        if self.availability == 'FN':
            # Convert date to datetime.date object
            date_obj = timezone.datetime.strptime(self.date, '%Y-%m-%d').date()
            # Set the time range for 'Before Noon' (7:00 AM to 12:00 PM)
            self.date = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.min.time()) + timezone.timedelta(hours=7))
        elif self.availability == 'AN':
            # Convert date to datetime.date object
            date_obj = timezone.datetime.strptime(self.date, '%Y-%m-%d').date()
            # Set the time range for 'After Noon' (12:00 PM to 7:00 PM)
            self.date = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.min.time()) + timezone.timedelta(hours=12))
        elif self.availability == 'FullDay':
            # Convert date to datetime.date object
            date_obj = timezone.datetime.strptime(self.date, '%Y-%m-%d').date()
            # Set the time range for 'Full Day' (7:00 AM to 7:00 PM)
            self.date = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.min.time()) + timezone.timedelta(hours=7))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.technician_profile.user.username} - {self.date} - {self.availability}"




class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    service = models.CharField(max_length=255,blank=True, null=True)
    phone = models.CharField(max_length=15,blank=True, null=True)
    district = models.CharField(max_length=50,blank=True, null=True)
    preferred_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE, blank=True, null=True)
    work_completed = models.BooleanField(default=False)  # New field for indicating work completion
    
    
    def __str__(self):
        return f"{self.user.username} - {self.fullname} - {self.preferred_date}"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} -  {self.message}'
    

class CustomerNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.message}'
    


# models.py
from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"


# models.py
from django.db import models
class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

