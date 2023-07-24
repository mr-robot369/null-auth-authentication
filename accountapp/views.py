from accountapp.utils import *
import requests
from django.conf import settings
# from django.urls import reverse
import urllib.parse
# from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from accountapp.models import *
# from accountapp.serializers import UserRegistrationSerializer, UserLoginSerializer
from accountapp.serializers import *
from django.contrib.auth import authenticate
from accountapp.renderers import UserRenderer

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated

#google auth
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

#Generate token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Registering the user with otp verification and directly log in the user
class UserRegistrationView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request, format=None):
        serializer=UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("Serializer is",serializer)
        email=serializer.save()
        
        user = User.objects.get(email=email)
        otp,secret=OTP.generate_otp()
        user.otp=otp
        user.otp_secret=secret
        user.save()

        # Send Email
        body=f'''OTP to verify your account {otp}
This otp is valid only for 5 minutes
'''
        data={
            'subject':'Verify your account',
            'body': body,
            'to_email':user.email
        }
        Util.send_email(data)

        return Response({'msg':'OTP Sent Successfully. Please Check your Email'},
        status=status.HTTP_200_OK)

# class OTPVerificationView(APIView):
#     renderer_classes=[UserRenderer]
#     def post(self,request,format=None):
#         serializer=OTPVerificationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response({'msg':'OTP Sent Successfully. Please Check your Email'},status=status.HTTP_200_OK)    

class OTPVerificationCheckView(APIView):
    renderer_classes=[UserRenderer]
    def post(self, request,format=None):
        serializer=OTPVerificationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        token=get_tokens_for_user(user)
        return Response({'msg':'OTP Verified Successfully! Registration Completed',"token":token},status=status.HTTP_201_CREATED)
    
# Login the user and generate JWT token
class UserLoginView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request, format=None):
        serializer=UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.data.get('email')
        password=serializer.data.get('password')
        user= authenticate(email=email,password=password)
        if user is not None:
            token=get_tokens_for_user(user)
            return Response({'token':token,'msg':'Login Success'},status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not valid']}},
            status=status.HTTP_404_NOT_FOUND)


# Show profile of logged in user
class UserProfileView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def get(self,request,format=None):
        serializer=UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Password Reset functionality (forget password)
class SendPasswordResetEmailView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer=SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset link send. Please Check your Email'},status=status.HTTP_200_OK)
        
class UserPasswordResetView(APIView):
    renderer_classes=[UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer=UserPasswordResetSerializer(data=request.data,context={'uid':uid,'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Successfully'},status=status.HTTP_200_OK)
    

# Password Changed functionality with otp verification
class UserChangePasswordView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        serializer=UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'OTP Sent Successfully. Please Check your Email'},status=status.HTTP_200_OK)    
    
class UserChangePasswordOTPView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def post(self, request,format=None):
        serializer=UserChangePasswordOTPSerializer(data=request.data,context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        
        return Response({'msg':'Password Changed Successfully'},status=status.HTTP_200_OK)
    
# # this comes in play when we want token from the code provided by callback
# class GoogleLogin(SocialLoginView):
#     class GoogleAdapter(GoogleOAuth2Adapter):
#         access_token_url = "https://oauth2.googleapis.com/token"
#         authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
#         profile_url= "https://www.googleapis.com/auth/userinfo/profile"
#         email_url = "https://www.googleapis.com/auth/userinfo/email"
#     adapter_class = GoogleAdapter
#     # adapter_class = GoogleOAuth2Adapter
#     # callback_url = 'http://localhost:8000/'  # Replace with your callback URL
#     callback_url = 'http://localhost:8000/api/user/google/login/callback/'  # Replace with your callback URL
#     client_class = OAuth2Client
 




# Hit on that url to get the callback
# https://accounts.google.com/o/oauth2/v2/auth?client_id=<google-client-id>&response_type=code&scope=https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile&access_type=offline&redirect_uri=http://localhost:8000/api/user/google/login/callback/

class CallbackHandleView(APIView):
    renderer_classes=[UserRenderer]
    def get(self,request):
        # print(type(request))
        code=request.query_params.get('code')
        data = {
            'code': code,
            'client_id': os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
            'client_secret': os.environ.get("GOOGLE_OAUTH_SECRET"),
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }

        token_response = requests.post('https://oauth2.googleapis.com/token', data=data)
        token_data = token_response.json()

        if 'error' in token_data:
            return Response({"error": "Failed to get access token from Google."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the access token from the response
        access_token = token_data.get('access_token', None)
        # print(access_token)
        if not access_token:
            return Response({"error": "Failed to get access token from Google response."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the access token to retrieve user information from Google
        user_info_response = requests.get(f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}')
        user_info = user_info_response.json()

        # Extract the email from the user information
        email = user_info.get('email', None)
        if not email:
            return Response({"error": "Failed to get email from Google user info."}, status=status.HTTP_400_BAD_REQUEST)

        try:
        # Login the user
            user = User.objects.get(email=email)
            jwt_token=get_tokens_for_user(user)
            return Response({'token':jwt_token,'msg':'Login Success'},status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
        # If Email does not exist, we have to redirect the user to additional details page
            redirect_url = settings.ADDITIONAL_DETAILS_URL
            redirect_url += f'?access_token={urllib.parse.quote(access_token)}'
            return Response({"redirect_url": redirect_url,"email":email}, status=status.HTTP_200_OK)
        
        except:
            return Response({"errors":"Invalid user"}, status=status.HTTP_400_BAD_REQUEST)

# get additional details and do the registartion part
class AdditionalUserInfoView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request, format=None):
        serializer=AdditionalUserInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # print("Serializer is",serializer)
        user=serializer.save()
        user.is_verified=True
        user.save()
        token=get_tokens_for_user(user)
        return Response({"msg":'Registration Completed',"token":token},status=status.HTTP_201_CREATED)