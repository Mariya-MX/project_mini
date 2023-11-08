from django.urls import path
from.import views
from django.contrib.auth import views as auth_views


urlpatterns = [
   path('',views.index,name="index"),
   path('register/',views.register,name="register"),
   path('login/',views.user_login,name="login"),
   path('technician_profile/',views.technician_profile,name="technician_profile"),
   path('customer_profile/',views.customer_profile,name="customer_profile"),
   path('logout/',views.userLogout,name="logout"),
   path('services/',views.services,name="services"),
   path('profile/',views.profile,name="profile"),
   path('custom_admin_panel/', views.custom_admin_panel, name="custom_admin_panel"),
   path('userlist/',views.userlist,name="userlist"),
   path('home/',views.home,name="home"),
   path('technician/',views.technician,name="technician"),
   path('technician_info/', views.technician_info, name='technician_info'),
   path('application/', views.application, name='application'),
   path('change_password/', views.change_password, name='change_password'),
   path('approval/', views.approval, name='approval'),
   path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),

  



    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
  
]