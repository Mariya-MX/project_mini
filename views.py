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

from django.shortcuts import get_object_or_404, redirect
from .models import CustomUser

def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Toggle between activation and deactivation
    user.is_active = not user.is_active
    user.save()

    # Redirect back to the user list page or any other page you prefer
    return redirect('userlist')






from .models import TechnicianProfile, ApprovedTechnician

@login_required(login_url='login')
def approve_technician(request, technician_profile_id):
    technician_profile = get_object_or_404(TechnicianProfile, id=technician_profile_id)

    
    # Check if the technician is already approved
    if not ApprovedTechnician.objects.filter(technician_profile=technician_profile).exists():
        # Create an ApprovedTechnician entry for the approved technician
        ApprovedTechnician.objects.create(technician_profile=technician_profile)

    # Set the is_approved field in the TechnicianProfile model to True
    technician_profile.is_approved = True
    technician_profile.save()

    # Redirect back to the approval page or any other page you prefer
    return redirect('approval')


from .models import TechnicianProfile, ApprovedTechnician
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def reject_technician(request, technician_profile_id):
    technician_profile = get_object_or_404(TechnicianProfile, id=technician_profile_id)

   
    # Delete the TechnicianProfile entry for the rejected technician
    technician_profile.delete()

    # Redirect back to the approval page or any other page you prefer
    return redirect('approval')


# def approved(request):
#     return render(request,'approved.html')
from django.shortcuts import render
from .models import ApprovedTechnician

def approved(request):
    # Fetch all ApprovedTechnician objects
    approved_technicians = ApprovedTechnician.objects.all()

    return render(request, 'approved.html', {'approved_technicians': approved_technicians})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TechnicianAvailability, ApprovedTechnician

def technician_availability(request):
    # Assuming you have a user profile associated with the logged-in user
    user_profile = request.user.userprofile

    # Assuming you have a TechnicianProfile associated with the user profile
    technician_profile = user_profile.technicianprofile

    # Assuming you have an ApprovedTechnician associated with the TechnicianProfile
    approved_technician = ApprovedTechnician.objects.get(technician_profile=technician_profile)

    # Fetch the availability data for the logged-in technician
    availability_data = TechnicianAvailability.objects.filter(approved_technician=approved_technician)

    if request.method == 'POST':
        date = request.POST.get('date')
        availability = request.POST.get('availability')

        # Check if availability already exists for the given date
        if TechnicianAvailability.objects.filter(approved_technician=approved_technician, date=date).exists():
            messages.error(request, 'Availability for the selected date already submitted.')
        else:
            # Create a new TechnicianAvailability object
            TechnicianAvailability.objects.create(
                technician_profile=technician_profile,
                approved_technician=approved_technician,
                date=date,
                availability=availability,
            )
            messages.success(request, 'Availability submitted successfully.')

        # Redirect back to the technician_availability page
        return redirect('technician_availability')

    return render(request, 'technician_availability.html', {'availability_data': availability_data})


from django.shortcuts import get_object_or_404

def cancel_availability(request, availability_id):
    # Retrieve the availability object
    availability = get_object_or_404(TechnicianAvailability, pk=availability_id)

    # Assuming you have permission checks here if the user is allowed to cancel this entry

    # Delete the availability entry
    availability.delete()

    # Redirect back to the technician_availability page or any other page
    return redirect('technician_availability')





# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Booking, TechnicianProfile, TechnicianAvailability,Notification
 

# @login_required(login_url='login')
# def booking(request):
    
#     if request.method == 'POST':
#         # Get form data
#         fullname = request.POST.get('fullname')
#         email = request.POST.get('email')
#         service = request.POST.get('service')
#         phone = request.POST.get('phone')
#         district = request.POST.get('district')
#         preferred_date = request.POST.get('date')
#         description = request.POST.get('description')

#         # Assuming the user is logged in
#         user = request.user

        

#         # Check technician availability for the selected date
#         available_technicians = TechnicianProfile.objects.filter(
#             district=district,
#             service=service,
#             is_approved=True,
#             technicianavailability__date=preferred_date,
#         )


        
#         if available_technicians.exists():
#             # Technician is available, create a new booking instance
#             booking = Booking.objects.create(
#                 user=user,
#                 fullname=fullname,
#                 email=email,
#                 service=service,
#                 phone=phone,
#                 district=district,
#                 preferred_date=preferred_date,
#                 description=description
#             )


#               # Create a notification for the user with booking details
#             notification_message = f'Booking details: {fullname}, {preferred_date}, {description}'
#             Notification.objects.create(user=user, message=notification_message)



             
            
#             # Optionally, you can add a success message
#             messages.success(request, 'Booking submitted successfully.')

            

            
#         else:
#             # Technician is not available, add an error message
#             messages.error(request, 'Sorry, no available technician for the selected service, district, and date.')

#         # Redirect to the booking form page
#         return redirect('booking')

#     return render(request, 'booking.html')



from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking, TechnicianProfile, TechnicianAvailability, Notification, CustomerNotification

@login_required(login_url='login')
def booking(request):
    
    if request.method == 'POST':
        # Get form data
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        service = request.POST.get('service')
        phone = request.POST.get('phone')
        district = request.POST.get('district')
        preferred_date = request.POST.get('date')
        description = request.POST.get('description')

        # Assuming the user is logged in
        user = request.user

        # Check technician availability for the selected date
        available_technicians = TechnicianProfile.objects.filter(
            district=district,
            service=service,
            is_approved=True,
            technicianavailability__date=preferred_date,
        )

        if available_technicians.exists():
            # Technician is available, assign the first available technician
            assigned_technician = available_technicians.first()

            # Create a new booking instance with the assigned technician
            booking = Booking.objects.create(
                user=user,
                fullname=fullname,
                email=email,
                service=service,
                phone=phone,
                district=district,
                preferred_date=preferred_date,
                description=description,
                technician=assigned_technician  # Assign the technician to the booking
            )


            # Create a notification for the assigned technician with booking details
            notification_message = f'Booking details: {fullname}, {preferred_date}, {description}'
            Notification.objects.create(user=assigned_technician.user, message=notification_message)

            # Create a notification for the user who made the booking with a specific message
            user_notification_message = f'Your booking for the repair service is successfully completed on {preferred_date}.'
            CustomerNotification.objects.create(user=user, message=user_notification_message)

            # Optionally, you can add a success message
            messages.success(request, 'Booking submitted successfully.')

        else:
            # Technician is not available, add an error message
            messages.error(request, 'Sorry, no available technician for the selected service, district, and date.')

        # Redirect to the booking form page
        return redirect('booking')

    return render(request, 'booking.html')







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

    return render(request, 'technician_profile.html', {'user_profile': user_profile,'other_context_data': '...'})




from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification, TechnicianProfile

@login_required(login_url='login')
def notifications_page(request):
    # Assuming the user is logged in
    user = request.user

    try:
        # Try to get the technician profile for the logged-in user
        technician_profile = TechnicianProfile.objects.get(user=user)
        
        # Retrieve notifications for the specific technician
        notifications = Notification.objects.filter(
            user=technician_profile.user
        ).order_by('-created_at')

        return render(request, 'notification.html', {'notifications': notifications})
    except TechnicianProfile.DoesNotExist:
        # Handle the case where the user is not associated with a TechnicianProfile
        return render(request, 'notification.html', {'notifications': []})






def notification_customer(request):
    return render(request,'notification_customer.html')


from django.shortcuts import render
from .models import CustomerNotification

def notification_customer(request):
    # Assuming the user is logged in
    user = request.user

    # Fetch user notifications
    user_notifications = CustomerNotification.objects.filter(user=user)

    return render(request, 'notification_customer.html', {'user_notifications': user_notifications})



from django.shortcuts import render
from .models import Booking

def order_details(request):
    technician = request.user.technicianprofile  # Assuming the technician is logged in
    bookings = Booking.objects.filter(technician=technician)

    context = {'bookings': bookings}
    return render(request, 'order_details.html', context)


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Booking

def mark_work_completed(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.work_completed = True
    booking.save()
    return HttpResponseRedirect(reverse('order_details'))



def enter_fee(request):
    return render(request,'enter_fee.html')


# views.py
from django.shortcuts import render
from django.views import View
from .models import Payment

class ProcessPaymentView(View):
    def post(self, request, *args, **kwargs):
        amount = float(request.POST.get('repair_fee'))

        # Create a new Payment instance
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
        )

        # You should implement logic here to verify the payment with Razorpay
        # Update payment status or perform any additional processing

        return render(request, 'payment_success.html', {'payment': payment})


from django.shortcuts import render
from django.db.models import Count
import matplotlib
matplotlib.use('agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def booking_graph(request):
    # Get the count of bookings for each service
    service_counts = Booking.objects.values('service').annotate(count=Count('id'))

    # Extract data for plotting
    services = [entry['service'] for entry in service_counts]
    counts = [entry['count'] for entry in service_counts]

    # Plot the data
    plt.bar(services, counts)
    plt.xlabel('Service')
    plt.ylabel('Number of Bookings')
    plt.title('Booking Statistics by Service')
    
    # Save the plot to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Convert the BytesIO object to base64 for embedding in HTML
    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    # Pass the base64 encoded image to the template
    return render(request, 'booking_graph.html', {'image_base64': image_base64})


# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import logout
# from django.db import IntegrityError
# from .models import DeactivatedUser

# @login_required
# def deactivate_confirmation(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')

#         try:
#             # Try to create a new DeactivatedUser instance
#             deactivated_user, created = DeactivatedUser.objects.get_or_create(user=request.user)
#         except IntegrityError:
#             # If a UNIQUE constraint error occurs, update the existing instance
#             deactivated_user = DeactivatedUser.objects.filter(user=request.user).first()
#             if deactivated_user:
#                 deactivated_user.save()

#         # Logout the user
#         logout(request)

#         # Redirect to the index page (replace 'index' with your desired page)
#         return redirect('index')

#     return render(request, 'deactivate_confirmation.html', {'user': request.user})

# from django.shortcuts import render
# from .models import DeactivatedUser

# def deactivate(request):
#     deactivated_users = DeactivatedUser.objects.all()
#     return render(request, 'deactivate.html', {'deactivated_users': deactivated_users})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Feedback
from django.utils import timezone

@login_required
def feedback(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback', '')
        # Assuming you have a CustomUser associated with the feedback
        feedback_user = request.user

        # Create and save the feedback object
        feedback = Feedback.objects.create(user=feedback_user, text=feedback_text)

        # You can do additional processing or redirect to a success page
        # return redirect('feedback')

    return render(request, 'feedback.html')

# views.py
from django.shortcuts import render
from .models import Feedback

def admin_feedback(request):
    feedback_list = Feedback.objects.all().order_by('-created_at')  # Fetch all feedbacks, order by creation time
    return render(request, 'admin_feedback.html', {'feedback_list': feedback_list})
