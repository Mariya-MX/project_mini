from django.shortcuts import render ,redirect
from django.contrib.auth import authenticate, login ,logout
from .models import CustomUser  # Assuming you have a CustomUser model
from django.db import IntegrityError
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
import re
from django.core.validators import validate_email
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import TechnicianProfile
from django.urls import reverse
from django.contrib import messages






# Create your views here.
@never_cache
def index(request):
    return render(request, 'index.html')





def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']  # Make sure this matches your form field name
        user_type = request.POST['user_type']



        # Perform server-side validation
        if not username:
            error_message = 'Username is required.'
            return render(request, 'register.html',{'error_message': error_message})

        if not username[0].isupper():
            error_message = 'Invalid username.'
            return render(request, 'register.html',{'error_message': error_message})

        if not re.match(r'^[A-Z][a-zA-Z0-9]{0,9}$', username):
            error_message = 'Invalid username'
            return render(request, 'register.html', {'error_message': error_message})

        if ' ' in username:
            error_message = 'Invalid username'
            return render(request, 'register.html', {'error_message': error_message})
        


        if not email:
            error_message = 'Email is required.'
            return render(request, 'register.html', {'error_message': error_message})

        if re.match(r'^[0-9]', email):
            error_message = 'Email cannot start with a number.'
            return render(request, 'register.html', {'error_message': error_message})

        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            error_message = 'Invalid email format.'
            return render(request, 'register.html', {'error_message': error_message})
        


        
        # Check if the email already exists in the database
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error_message': 'Email address is already in use.'})
        
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error_message': 'username already used'})

        if password != confirm_password:
            return render(request, 'register.html', {'error_message': 'Passwords do not match'})

        try:
            # Try to create a new user object
            user = CustomUser.objects.create_user(username=username, email=email, password=password, user_type=user_type)
            # You may want to do additional processing here if needed



            return render(request, 'register.html', {'registration_success': True})

        
            # return redirect('login')# Redirect to login page after successful registration
        except IntegrityError:
            # Handle the case where there is a database integrity error
            return render(request, 'register.html', {'error_message': 'An error occurred during registration.'})

    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)


        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('custom_admin_panel')  # Redirect to your custom admin panel
            elif user.user_type == 'technician':
                request.session['user_type'] = 'technician'
                return redirect('technician_profile')
            elif user.user_type == 'customer':
                request.session['user_type'] = 'customer'
                return redirect('customer_profile')
            else:
                return HttpResponse('Invalid user type')
            
        else:
            if not CustomUser.objects.filter(username=username).exists():
                error_message = 'Wrong username'
            else:
                error_message = 'Wrong password'

            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')



@login_required(login_url='login')
@never_cache
def technician_profile(request):
    user = request.user

    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)

    # The rest of your view logic goes here...

    return render(request, 'technician_profile.html', {'user_profile': user_profile, 'other_context_data': '...'})






@login_required(login_url='login')
@never_cache
def customer_profile(request):
    user = request.user

    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)

    # The rest of your view logic goes here...

    return render(request, 'customer_profile.html', {'user_profile': user_profile, 'other_context_data': '...'})




def userLogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')


def services(request):
    return render(request,'services.html')

def profile(request):
    return render(request,'profile.html')

# @user_passes_test(lambda u: u.is_staff, login_url='login')
# @never_cache
# def custom_admin_panel(request):
#      # Retrieve all users (excluding the admin)
#     users = CustomUser.objects.exclude(is_staff=True)

#     registered_users_count = CustomUser.objects.filter(is_staff=False).count()

#     # Pass user details as context data
#     context = {'users': users,'registered_users_count': registered_users_count}
    
#     # Add any logic or context data needed for your custom admin panel
#     return render(request, 'admin.html',context)



def home(request):
    return render(request,'home.html')





@user_passes_test(lambda u: u.is_staff, login_url='login')
@never_cache
def custom_admin_panel(request):
    # Get the list of all registered users (excluding the admin)
    all_registered_users = CustomUser.objects.exclude(is_staff=True)

    # Count total registered users, total registered technicians, and total regular users
    total_registered_users = all_registered_users.count()
    total_registered_technicians = all_registered_users.filter(user_type='technician').count()
    total_regular_users = total_registered_users - total_registered_technicians

    # Pass counts and the list of all registered users as context data
    context = {
        'total_registered_users': total_registered_users,
        'total_registered_technicians': total_registered_technicians,
        'total_regular_users': total_regular_users,
        'all_registered_users': all_registered_users,
    }

    # Add any logic or context data needed for your custom admin panel
    return render(request, 'admin.html', context)






# views.py

# @login_required(login_url='login')
# def profile(request):
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         # Process form data manually
#         user_profile.first_name = request.POST.get('first_name')
#         user_profile.last_name = request.POST.get('last_name')
#         user_profile.mobile = request.POST.get('mobile')
#         user_profile.address = request.POST.get('address')

#         # Handle image upload manually
#         if 'image' in request.FILES:
#             user_profile.image = request.FILES['image']

#         user_profile.save()

#         # Redirect to a success page or update the current page as needed
#         return redirect('profile')

#     return render(request, 'profile.html', {'user_profile': user_profile, 'created': created})


@login_required(login_url='login')
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Process form data manually
        user_profile.first_name = request.POST.get('first_name')
        user_profile.last_name = request.POST.get('last_name')
        user_profile.mobile = request.POST.get('mobile')
        user_profile.address = request.POST.get('address')

        # Handle image upload manually
        if 'image' in request.FILES:
            user_profile.image = request.FILES['image']

        user_profile.save()

        # Redirect to a success page or update the current page as needed
        
        return redirect('profile')

    # Check the user type and redirect accordingly
    if request.user.user_type == 'technician':
        return render(request, 'technician.html', {'user_profile': user_profile, 'created': created})
    else:
        return render(request, 'profile.html', {'user_profile': user_profile, 'created': created})
    

def technician(request):
    return render(request,"technician.html")

def technician_info(request):
    return render(request,"technician2.html")
    




# @login_required(login_url='login')
# def application(request):
#     # Fetch user details from CustomUser and UserProfile models
#     user = request.user

#     try:
#         # Try to get the UserProfile object for the current user
#         user_profile = UserProfile.objects.get(user=user)

#         # If the UserProfile exists, retrieve the data
#         first_name = user_profile.first_name
#         last_name = user_profile.last_name
#         phone_number = user_profile.mobile
#     except UserProfile.DoesNotExist:
#         # If the UserProfile does not exist, set the other fields to empty strings
#         first_name = ""
#         last_name = ""
#         phone_number = ""

#     # Pass the user details to the template
#     context = {
#         'first_name': first_name,
#         'last_name': last_name,
#         'email': user.email,
#         'phone_number': phone_number,
#         # Add more fields as needed
#     }

#     return render(request, 'application.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password= request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        # Check if old password matches the existing password
        if check_password(current_password, request.user.password) and new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Pass the user object as the second argument
            # Send email notification
            # messages.success(request, 'Password changed successfully!')
            # return redirect('login')  # Redirect to profile page or any other page you prefer

            messages.success(request, '')
            return render(request, 'change_password.html', {'success_message': 'Password changed successfully'})
        else:
            # messages.error(request, 'Password change failed. Please check your old password or new password confirmation.')
            messages.error(request, 'Password change failed. Please check your old password or new password confirmation.')

    return render(request, 'change_password.html')





from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import CustomUser, UserProfile, TechnicianProfile

@login_required(login_url='login')
def application(request):
    user = request.user



    # Fetch data from CustomUser and UserProfile models
    custom_user = get_object_or_404(CustomUser, id=user.id)
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    # Initialize variables with existing data
    first_name = user_profile.first_name
    last_name = user_profile.last_name
    email = custom_user.email
    phone_number = user_profile.mobile


    # Fetch all submitted TechnicianProfiles
    technician_profiles = TechnicianProfile.objects.all()


    

    if request.method == 'POST':
        # Process form data manually
        first_name = request.POST.get('first_name', first_name)
        last_name = request.POST.get('last_name', last_name)
        email = request.POST.get('email', email)
        phone_number = request.POST.get('number', phone_number)
        tech_image = request.FILES.get('tech_image')
        resume = request.FILES.get('resume')
        id_proof = request.FILES.get('idProof')
        # Check if 'experience' is provided, otherwise set it to zero
        experience = request.POST.get('experience')
        experience = int(experience) if experience else 0
        service = request.POST.get('service')
        district = request.POST.get('district')

        # Check if TechnicianProfile already exists
        technician_profile, created = TechnicianProfile.objects.get_or_create(
            user=user,
            user_profile=user_profile,
            defaults={
                'tech_first_name': first_name,
                'tech_last_name': last_name,
                'tech_email': email,
                'tech_number': phone_number,
                'tech_image': tech_image,
                'resume': resume,
                'id_proof': id_proof,
                'experience': experience,
                'service': service,
                'district': district,
            }
        )


        # Fetch all submitted TechnicianProfiles again after submission
        technician_profiles = TechnicianProfile.objects.all()




        # Redirect to a success page or update the current page as needed
        success_url = reverse('application') + '?success=true'
        return redirect(success_url)
    

        

    # Pass existing data to the template
    return render(request, 'application.html', {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone_number': phone_number,
    })



def userlist(request):
    # Retrieve all registered users (excluding the admin)
    registered_users = CustomUser.objects.filter(is_staff=False)

    # Pass the list of users to the template
    context = {'registered_users': registered_users}
    
    return render(request, 'users.html', context)



# def approval(request):
#     return render(request,'approval.html')


from django.shortcuts import render
from .models import TechnicianProfile
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def approval(request):
    # Fetch all TechnicianProfile objects
    technician_profiles = TechnicianProfile.objects.all()

    return render(request, 'approval.html', {'technician_profiles': technician_profiles})



from django.contrib.auth.decorators import user_passes_test

# @user_passes_test(lambda u: u.is_staff, login_url='login')  # Only allow staff to deactivate users
# def deactivate_user(request, user_id):
#     try:
#         user_to_deactivate = CustomUser.objects.get(id=user_id)
#         user_to_deactivate.is_active = False  # Deactivate the user
#         user_to_deactivate.save()
#         # Optionally, you can add a success message using Django messages framework
#         messages.success(request, 'User deactivated successfully!')
#     except CustomUser.DoesNotExist:
#         # Handle the case where the user is not found
#         messages.error(request, 'User not found.')
#     return redirect('userlist')  # Redirect to the user list page



from django.shortcuts import get_object_or_404, redirect
from .models import CustomUser

def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Toggle between activation and deactivation
    user.is_active = not user.is_active
    user.save()

    # Redirect back to the user list page or any other page you prefer
    return redirect('userlist')








