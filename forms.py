# yourapp/forms.py
from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image', 'first_name', 'last_name', 'mobile', 'address']

    image = forms.ImageField(label='Upload Profile Image', required=False)
