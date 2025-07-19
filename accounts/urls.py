from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-reset-otp/', views.VerifyResetOTPView.as_view(), name='verify_reset_otp'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('addresses/', views.AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
]