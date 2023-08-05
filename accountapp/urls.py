from django.urls import path,include

from accountapp.views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('otp/verify/', OTPVerificationCheckView.as_view(),name='verify_otp'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('profile/', UserProfileView.as_view(),name='profile'),
    path('forget-password/',SendPasswordResetEmailView.as_view(),name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/',UserPasswordResetView.as_view(), name="reset-password"),
    
    path('changepassword/',UserChangePasswordView.as_view(),name='changepassword'),
    path('changepassword/otp/verify/',UserChangePasswordOTPView.as_view(),name='changepassword_otp_verify'),
    
    # this comes in play when we want token from the code provided by callback. hit this url and send code in body it will return the
    # path('auth/google/', GoogleLogin.as_view(), name='google_login'),

    # needed for google auth
    path("google/login/",GoogleHandle.as_view(), name="google"),
    path("google/login/callback/", CallbackHandleView.as_view(),name="callback"),
    path("google/additional-details/", AdditionalUserInfoView.as_view(), name='additonal'),

    
]



