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
            elif user.user_type == 'Delivery':
                request.session['user_type'] = 'Delivery'
                return redirect('delivery')
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






from django.core.validators import RegexValidator
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






import datetime 

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
            messages.error(request, 'Sorry,the service is not available on this date.choose another date')

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
# from django.shortcuts import render
# from django.views import View
# from .models import Payment

# class ProcessPaymentView(View):
#     def post(self, request, *args, **kwargs):
#         amount = float(request.POST.get('repair_fee'))

#         # Create a new Payment instance
#         payment = Payment.objects.create(
#             user=request.user,
#             amount=amount,
#         )

#         # You should implement logic here to verify the payment with Razorpay
#         # Update payment status or perform any additional processing

#         return render(request, 'payment_success.html', {'payment': payment})


from django.shortcuts import render
from django.views import View
from .models import Payment

class ProcessPaymentView(View):
    template_name = 'payment_success.html'  # Create a template for displaying success message

    def post(self, request, *args, **kwargs):
        amount = float(request.POST.get('repair_fee'))

        # Create a new Payment instance
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
        )

        # You should implement logic here to verify the payment with Razorpay
        # Update payment status or perform any additional processing

        # Render the template with the success message
        return render(request, self.template_name, {'payment': payment, 'success_message': 'Your payment successfully completed!'})


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

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages

def admin_delivery(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        user_type = request.POST.get('user_type')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('admin_delivery')
        

        User = get_user_model()
        

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
            return redirect('admin_delivery')

        # Create a new CustomUser object
        User = get_user_model()
        try:
            new_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type
            )

            # Send email to the user
            subject = 'Welcome to Our Site!'
            message = f'Hi {username},\n\nWelcome to our site. Your username is: {username} and your password is: {password}.'
            from_email = "mariyaxavier2024b@mca.ajce.in"
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            messages.success(request, 'User registered successfully')
        except IntegrityError as e:
            if 'UNIQUE constraint failed: app1_customuser.username' in str(e):
                messages.error(request, 'Username is already registered')
            elif 'UNIQUE constraint failed: app1_customuser.email' in str(e):
                messages.error(request, 'Email is already registered')
            else:
                messages.error(request, f'Error occurred: {str(e)}')
        
        return redirect('admin_delivery')

    return render(request, 'admin_delivery.html')


   



def delivery(request):
    return render(request,'delivery_profile.html')


# correct

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Product, UserProfile

@login_required(login_url='login')
def sellproducts(request):
    user = request.user

    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        brand_name = request.POST.get('brandName')
        category = request.POST.get('category')
        ad_title = request.POST.get('adtitle')
        price = request.POST.get('price')
        description = request.POST.get('description')
        contact = request.POST.get('contact')

        # Assuming you have already handled file uploads and stored file paths in variables like image1, image2, etc.
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')

        # Create and save the product object
        product = Product.objects.create(
            owner=user,  # Assign the current user as the owner of the product
            brand_name=brand_name,
            category=category,
            ad_title=ad_title,
            price=price,
            description=description,
            contact=contact,
            image1=image1,
            image2=image2,
            image3=image3,
            image4=image4
        )


        # Show a success message
        messages.success(request, 'Product added successfully!')

        # Redirect to the same page after successful submission
        return redirect('sell')  

    return render(request, 'sell.html', {'user_profile': user_profile})







# from django.shortcuts import render
# from .models import UserProfile, Product

# def appliances(request):
#     user = request.user
#     try:
#         # Attempt to retrieve the user's profile
#         user_profile = UserProfile.objects.get(user=user)
#     except UserProfile.DoesNotExist:
#         # If the profile does not exist, create a new one
#         user_profile = UserProfile.objects.create(user=user)

#     # Retrieve all products from the database
#     all_products = Product.objects.all()

#     return render(request, 'appliances.html', {'user_profile': user_profile, 'products': all_products})



# correct
from django.shortcuts import render
from .models import UserProfile, Product

def appliances(request):
    user = request.user
    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)

    # Retrieve all products from the database
    all_products = Product.objects.all()

    # Check if any category filter is applied
    category_filter = request.GET.get('category')
    if category_filter:
        # If a category is selected, filter products based on that category
        if category_filter != 'all':
            all_products = all_products.filter(category=category_filter)

    return render(request, 'appliances.html', {'user_profile': user_profile, 'products': all_products})



# def appliances(request):
#     user = request.user
#     try:
#         # Attempt to retrieve the user's profile
#         user_profile = UserProfile.objects.get(user=user)
#     except UserProfile.DoesNotExist:
#         # If the profile does not exist, create a new one
#         user_profile = UserProfile.objects.create(user=user)

#     return render(request,'appliances.html',{'user_profile': user_profile})



# correct
from .models import Product

def product_status(request):
    user = request.user
    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)

    # Fetch products posted by the user
    user_products = Product.objects.filter(owner=user)

    return render(request, 'sell_product_status.html', {'user_profile': user_profile, 'user_products': user_products})




# correct
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('sell_product_status')

    return redirect('sell_product_status')  


def appliance_details(request):
    user = request.user
    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)
    return render(request,'appliance_sub.html',{'user_profile': user_profile})



# def appliance_details(request):
#     user = request.user
#     try:
#         # Attempt to retrieve the user's profile
#         user_profile = UserProfile.objects.get(user=user)
#     except UserProfile.DoesNotExist:
#         # If the profile does not exist, create a new one
#         user_profile = UserProfile.objects.create(user=user)

#     return render(request,'appliance_sub.html',{'user_profile': user_profile})


from django.shortcuts import render, get_object_or_404
from .models import Product

def appliance_details(request, product_id):
    user = request.user
    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)

    # Retrieve the product based on the provided product_id
    product = get_object_or_404(Product, pk=product_id)

    return render(request, 'appliance_sub.html', {'user_profile': user_profile, 'product': product})





def messages_page(request):
    return render(request,'messages.html')


# correct

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from .models import Product, UserProfile, UserAddress, CustomUser

# def checkout(request):
#     user = request.user
#     try:
#         # Attempt to retrieve the user's profile
#         user_profile = UserProfile.objects.get(user=user)
#     except UserProfile.DoesNotExist:
#         # If the profile does not exist, create a new one
#         user_profile = UserProfile.objects.create(user=user)

#     if request.method == 'GET':
#         # Retrieve product information from query parameters
#         product_id = request.GET.get('product_id')
#         price = request.GET.get('price')
#         product_name = request.GET.get('product_name')
#         owner_id = request.GET.get('owner_id')
        
#         # Validate if all necessary parameters are provided
#         if product_id and price and product_name and owner_id:
#             # Retrieve the product object based on the product_id
#             product = get_object_or_404(Product, pk=product_id)
            
#             # Retrieve the CustomUser instance associated with the owner
#             owner = get_object_or_404(CustomUser, pk=owner_id)
            
#             # Retrieve the UserAddress associated with the owner
#             try:
#                 owner_address = UserAddress.objects.get(user=owner)
#             except UserAddress.DoesNotExist:
#                 owner_address = None

#             # Pass user_profile, product, owner_address, and other necessary parameters to the template
#             context = {
#                 'user_profile': user_profile,
#                 'product': product,
#                 'price': price,
#                 'product_name': product_name,
#                 'owner_id': owner_id,
#                 'product_id': product_id,
#                 'owner_address': owner_address,
#                 'image1_url': product.image1.url if product.image1 else None,
#             }
#             return render(request, 'checkout.html', context)
#         else:
#             # Redirect to some error page or display an error message
#             messages.error(request, 'Invalid parameters provided for checkout.')
#             return redirect('checkout')  # Update with appropriate URL
#     else:
#         # Handle POST requests if needed
#         pass  # Add your POST request handling logic here if necessary

from .models import UserProfile, UserAddress

def checkout(request):
    user = request.user
    try:
        # Attempt to retrieve the user's profile
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the profile does not exist, create a new one
        user_profile = UserProfile.objects.create(user=user)

    if request.method == 'GET':
        # Retrieve product information from query parameters
        product_id = request.GET.get('product_id')
        price = request.GET.get('price')
        product_name = request.GET.get('product_name')
        owner_id = request.GET.get('owner_id')
        
        # Validate if all necessary parameters are provided
        if product_id and price and product_name and owner_id:
            # Retrieve the product object based on the product_id
            product = get_object_or_404(Product, pk=product_id)
            
            # Retrieve the CustomUser instance associated with the owner
            owner = get_object_or_404(CustomUser, pk=owner_id)
            
            # Retrieve the UserProfile associated with the owner
            try:
                owner_profile = UserProfile.objects.get(user=owner)
                owner_name = f"{owner_profile.first_name} {owner_profile.last_name}"
                # Retrieve owner's address
                owner_address = UserAddress.objects.get(user=owner)
            except UserProfile.DoesNotExist:
                owner_name = "Unknown"
                owner_address = None

            # Retrieve logged-in user's address
            user_address = UserAddress.objects.get(user=user)

            # Pass user_profile, product, owner_name, owner_address, user_address, and other necessary parameters to the template
            context = {
                'user_profile': user_profile,
                'product': product,
                'price': price,
                'product_name': product_name,
                'owner_id': owner_id,
                'owner_name': owner_name,
                'product_id': product_id,
                'image1_url': product.image1.url if product.image1 else None,
                'owner_address': owner_address,
                'user_address': user_address,
            }
            return render(request, 'checkout.html', context)
        else:
            # Redirect to some error page or display an error message
            messages.error(request, 'Invalid parameters provided for checkout.')
            return redirect('checkout')  # Update with appropriate URL
    else:
        # Handle POST requests if needed
        pass  # Add your POST request handling logic here if necessary











# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserAddress

def save_address(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        state = request.POST.get('state')
        district = request.POST.get('district')
        pincode = request.POST.get('pincode')

        # Assuming the user is authenticated, retrieve the user object
        user = request.user

        # Check if the user already has an address
        existing_address = UserAddress.objects.filter(user=user).first()

        if existing_address:
            # If an address already exists, update it
            existing_address.address = address
            existing_address.state = state
            existing_address.district = district
            existing_address.pincode = pincode
            existing_address.save()
            messages.success(request, 'Your address has been successfully updated!')
        else:
            # If no address exists, create a new one
            UserAddress.objects.create(user=user, address=address, state=state, district=district, pincode=pincode)
            messages.success(request, 'Your address has been successfully saved!')

        # Fetch user's address to pass to the template
        user_address = UserAddress.objects.filter(user=user).first()

        # Redirect to the appliances.html page
        return redirect('appliances')  # Replace 'appliances' with the name of your appliances page URL pattern

    else:
        # Fetch user's address to pass to the template
        user_address = UserAddress.objects.filter(user=request.user).first()

        # Render the template with the user_address object
        return render(request, 'appliances.html', {'user_address': user_address})
    

    # correct one

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import FavoriteProduct

@csrf_exempt
def add_favorite(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        user = request.user  # Assuming user is authenticated
        
        # Check if the product is already favorited by the user
        favorite_product = FavoriteProduct.objects.filter(user=user, product_id=product_id).first()
        if favorite_product:
            # If the product is already favorited, remove it from favorites
            favorite_product.delete()
            return JsonResponse({'success': False})  # Product removed from favorites
        else:
            # If the product is not favorited, add it to favorites
            FavoriteProduct.objects.create(user=user, product_id=product_id)
            return JsonResponse({'success': True})  # Product added to favorites
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)



    # correct

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import FavoriteProduct

def wishlist(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            favorite_item = FavoriteProduct.objects.get(id=item_id)
            favorite_item.delete()
            return JsonResponse({'success': True})
        except FavoriteProduct.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item does not exist.'})
    else:
        # Retrieve favorite items for the current user
        favorite_items = FavoriteProduct.objects.filter(user=request.user)
        return render(request, 'wishlist.html', {'favorite_items': favorite_items})



from django.shortcuts import render
from .models import UserProfile

def success_page(request):
   
    # Pass user_profile and payment_id to the template
    return render(request, 'success_page.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Transaction, CustomUser, Product
import json

@csrf_exempt
def store_transaction(request):
    if request.method == 'POST':
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        
        # Extract data from the JSON object
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        price = data.get('price')

        # Retrieve user and product objects from the database
        user = get_object_or_404(CustomUser, pk=user_id)
        product = get_object_or_404(Product, pk=product_id)

        # Create a new Transaction object and save it to the database
        transaction = Transaction.objects.create(user=user, product=product, price=price)


       # Update the product status to ordered
        product.ordered = True
        product.save()


         # Check if the product is ordered and update its status to "Sold Out"
        if product.ordered:
            product.status = "Sold Out"
            product.save()
        
        # You can return a success response if needed
        return JsonResponse({'success': True}) 
    else:
        # Handle other types of requests if needed
        pass



# from django.shortcuts import render
# from .models import Transaction

# def history(request):
#     # Retrieve all transactions for the logged-in user
#     transactions = Transaction.objects.filter(user=request.user)

#     # Pass the transactions to the template
#     return render(request, 'history.html', {'transactions': transactions})


# ................................................correct one..............................................................
# from django.shortcuts import render
# from .models import Transaction, UserAddress

# def history(request):
#     # Retrieve all transactions for the logged-in user
#     transactions = Transaction.objects.filter(user=request.user)

#     # Retrieve the user's address
#     user_address = UserAddress.objects.get(user=request.user)

#     # Pass the transactions and user's address to the template
#     return render(request, 'history.html', {'transactions': transactions, 'user_address': user_address})



from django.shortcuts import render
from .models import Transaction, UserAddress

def history(request):
    # Retrieve all transactions for the logged-in user
    transactions = Transaction.objects.filter(user=request.user)

    # Retrieve the user's address
    user_address = UserAddress.objects.get(user=request.user)

    # Pass the transactions and user's address to the template
    return render(request, 'history.html', {'transactions': transactions, 'user_address': user_address})



from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.utils import timezone

def generate_pdf(request, product_id):
    # Fetch the product based on the product_id
    product = Product.objects.get(pk=product_id)

    # Retrieve transactions for the product
    transactions = Transaction.objects.filter(product=product)

    # Fetch the logged-in user
    user = request.user

    # Fetch the user's address
    user_address = user.user_address if hasattr(user, 'user_address') else None

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{product.brand_name}_receipt.pdf"'

    # Create a PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Define styles
    styles = getSampleStyleSheet()
    style_heading = styles['Heading1']
    style_body = styles['BodyText']
    style_table_heading = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black), 
    ]

    # Define data for the table
    data = [
        [Paragraph('<b>Name</b>', style_body),
         Paragraph('<b>Category</b>', style_body),
         Paragraph('<b>Paid</b>', style_body),
         Paragraph('<b>Date</b>', style_body)]
    ]

    # Add transaction details to the data
    for transaction in transactions:
        data.append([
            transaction.product.brand_name,
            transaction.product.category,
            f'{transaction.price}',
            transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ])

    # Create the table
    table = Table(data)
    table.setStyle(TableStyle(style_table_heading))

    # Create elements list and add headings
    elements = [
        Paragraph("<b>EasyTech Repairs</b>", style_heading),
        Paragraph("<b>Receipt</b>", style_heading)  # Add both headings
    ]

    # Add space between headings and table
    elements.append(Paragraph("<br/><br/>", style_body))

    
    
    # Add user name on the right side
    if user.is_authenticated:
        elements.append(Paragraph(f"<p>Name: {user.username}</p>", style_body)),
        elements.append(Paragraph("<br/>", style_body))
                        
        

    # Add table to elements
    elements.append(table)

    # Add sentence below the table
    elements.append(Paragraph("<br/>", style_body))
    elements.append(Paragraph("<br/>", style_body))
    elements.append(Paragraph("<br/>", style_body))
    elements.append(Paragraph("This is a computer system generated receipt. Hence there is no need for a physical signature.", style_body))

    # Build the PDF document
    doc.build(elements)

    return response




# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Transaction

# @csrf_exempt
# def cancel_transaction(request, transaction_id):
#     if request.method == 'POST':
#         # Retrieve the Transaction object from the database
#         transaction = get_object_or_404(Transaction, pk=transaction_id)

#         # Update the refunded field of the transaction
#         transaction.refunded = True
#         transaction.save()

#         # Return a success response
#         return JsonResponse({'success': True}) 
#     else:
#         # Handle other types of requests if needed
#         pass

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Transaction, Product

@csrf_exempt
def cancel_transaction(request, transaction_id):
    if request.method == 'POST':
        # Retrieve the Transaction object from the database
        transaction = get_object_or_404(Transaction, pk=transaction_id)

        # Update the refunded field of the transaction
        transaction.refunded = True
        transaction.save()

        # Update the ordered field of the product associated with the cancelled transaction
        product = transaction.product
        product.ordered = False
        product.save()

        # Return a success response
        return JsonResponse({'success': True}) 
    else:
        # Handle other types of requests if needed
        pass


