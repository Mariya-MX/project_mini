from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import UserProfile


User = get_user_model()

class SuperuserAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return User.objects.filter(is_superuser=False)
    list_display=('username','email','user_type')

# Register the custom admin class
admin.site.register(User, SuperuserAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'first_name', 'last_name', 'mobile', 'address')  # Customize this according to your UserProfile model

# Register the custom admin class for UserProfile
admin.site.register(UserProfile, UserProfileAdmin)