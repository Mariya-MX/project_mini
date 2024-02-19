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
   path('approve_technician/<int:technician_profile_id>/', views.approve_technician, name='approve_technician'),
   path('reject_technician/<int:technician_profile_id>/', views.reject_technician, name='reject_technician'),
   path('approved/', views.approved, name='approved'),
   path('technician_availability/', views.technician_availability, name='technician_availability'),
   path('cancel_availability/<int:availability_id>/', views.cancel_availability, name='cancel_availability'),
   path('booking/', views.booking, name='booking'),
#    path('clear_notification/<int:notification_id>/', views.clear_notification, name='clear_notification'),
   path('notifications_page/', views.notifications_page, name='notifications_page'),
   path('notification_customer/', views.notification_customer, name='notification_customer'),
#    path('view_booking/<int:booking_id>/', views.view_booking, name='view_booking'),
   path('order-details/', views.order_details, name='order_details'),
   path('mark-work-completed/<int:booking_id>/', views.mark_work_completed, name='mark_work_completed'),
   path('enter_fee/', views.enter_fee, name='enter_fee'),
   path('process_payment/',views.ProcessPaymentView.as_view(), name='process_payment'),

   path('booking_graph/', views.booking_graph, name='booking_graph'),
#    path('deactivate_confirmation/', views.deactivate_confirmation, name='deactivate_confirmation'),
#    path('deactivate/', views.deactivate, name='deactivate'),
   path('feedback/', views.feedback, name='feedback'),
   path('admin_feedback/', views.admin_feedback, name='admin_feedback'),
   path('admin_delivery/', views.admin_delivery, name='admin_delivery'),
   path('delivery/', views.delivery, name='delivery'),
   path('sell/', views.sellproducts, name='sell'),
   path('appliances/', views.appliances, name='appliances'),
   
   path('sell_product_status/', views.product_status, name='sell_product_status'),
   path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
   path('appliance_sub/<int:product_id>/', views.appliance_details, name='appliance_sub'),
   path('chat/', views.chat, name='chat'),
   
   

  
  

    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
  
]



