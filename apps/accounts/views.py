import datetime

# from django.urls import reverse
import urllib.parse

import requests
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts.models import *
from apps.accounts.renderers import UserRenderer
from apps.accounts.serializers import *
from apps.accounts.utils import *

# from django.shortcuts import render


# #google auth
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from dj_rest_auth.registration.views import SocialLoginView


# Generate token Manually
class GenerateToken:
    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        # custom_payload={"name":user.name,"email":user.email}
        # refresh.payload.update(custom_payload)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    def generate_dummy_jwt_token(Cpayload):
        # creating custom payload with 5 minutes expiration time
        custom_payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }
        custom_payload.update(Cpayload)
        # Create a new AccessToken with the custom payload
        access_token = AccessToken()
        access_token.payload.update(custom_payload)
        return str(access_token)

    @staticmethod
    def add_payload(token, payload):
        access_token = AccessToken(token)
        access_token.payload.update(payload)
        return str(access_token)

    @staticmethod
    def verify_and_get_payload(token):
        try:
            # Decode the token and verify its validity
            access_token = AccessToken(token)
            # Getting payload
            payload = access_token.payload
            return payload
        except InvalidToken:
            # Token is invalid
            raise InvalidToken("Invalid token")
        except TokenError:
            # Some other token-related error
            raise TokenError("Token expired")

    # @staticmethod
    # def delete_token(mytoken):
    #     try:
    #         access_token = RefreshToken(mytoken)
    #         access_token.blacklist()
    #         # BlacklistedToken.objects.create(token=mytoken)
    #     except Exception as e:
    #         raise TokenError(e)


def OTP_DummyToken(user):
    payload = {"email": user.email}
    token = GenerateToken.generate_dummy_jwt_token(payload)
    otp, secret = OTP.generate_otp()
    user.otp = otp
    user.otp_secret = secret
    user.save()
    # Send Email
    body = f"""OTP to verify your account {otp}
    This otp is valid only for 5 minutes
    """
    data = {"subject": "Verify your account", "body": body, "to_email": user.email}
    Util.send_email(data)
    return token


# Registering the user with otp verification and directly log in the user
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.save()

        user = User.objects.get(email=email)
        user.provider = "local"
        token = OTP_DummyToken(user)
        return Response(
            {
                "msg": "OTP Sent Successfully. Please Check your Email",
                "url": "otp/verify/",
                "token": token,
            },
            status=status.HTTP_200_OK,
        )


class OTPVerificationCheckView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        dummy_token = request.query_params.get("token")
        try:
            payload = GenerateToken.verify_and_get_payload(dummy_token)
            # print(payload)
        except InvalidToken as e:
            return Response({"error": str(e)}, status=401)
        except TokenError as e:
            return Response({"error": str(e)}, status=400)

        serializer = OTPVerificationCheckSerializer(
            data=request.data, context={"email": payload.get("email")}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = GenerateToken.get_tokens_for_user(user)
        return Response(
            {"msg": "OTP Verified Successfully!", "token": token},
            status=status.HTTP_201_CREATED,
        )


# Login the user and generate JWT token
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        password = serializer.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_verified:
                token = GenerateToken.get_tokens_for_user(user)
                return Response(
                    {"token": token, "msg": "Login Success"}, status=status.HTTP_200_OK
                )
            else:
                token = OTP_DummyToken(user)
                return Response(
                    {"msg": "User not verified", "token": token},
                    status=status.HTTP_409_CONFLICT,
                )
        else:
            return Response(
                {"errors": {"non_field_errors": ["Email or Password is not valid"]}},
                status=status.HTTP_404_NOT_FOUND,
            )


# Show profile of logged in user
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Password Reset functionality (forget password)
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password Reset link send. Please Check your Email"},
            status=status.HTTP_200_OK,
        )


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password Reset Successfully"}, status=status.HTTP_200_OK
        )


# Password Changed functionality with otp verification
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "OTP Sent Successfully. Please Check your Email"},
            status=status.HTTP_200_OK,
        )


class UserChangePasswordOTPView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordOTPSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            {"msg": "Password Changed Successfully"}, status=status.HTTP_200_OK
        )


# Hit on that url to get the callback
# https://accounts.google.com/o/oauth2/v2/auth?client_id=<google-client-id>&response_type=code&scope=https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile&access_type=offline&redirect_uri=http://localhost:8000/api/user/google/login/callback/


class GoogleHandle(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request):
        client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
        response_type = "code"
        scope = f"https://www.googleapis.com/auth/userinfo.email "
        scope += f"https://www.googleapis.com/auth/userinfo.profile"
        access_type = "offline"
        redirect_uri = settings.GOOGLE_REDIRECT_URI

        google_redirect_url = "https://accounts.google.com/o/oauth2/v2/auth"
        google_redirect_url += f"?client_id={urllib.parse.quote(client_id)}"
        google_redirect_url += f"&response_type={urllib.parse.quote(response_type)}"
        google_redirect_url += f"&scope={urllib.parse.quote(scope)}"
        google_redirect_url += f"&access_type={urllib.parse.quote(access_type)}"
        google_redirect_url += f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        return Response(
            {"google_redirect_url": google_redirect_url}, status=status.HTTP_200_OK
        )


class CallbackHandleView(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request):
        code = request.query_params.get("code")
        data = {
            "code": code,
            "client_id": os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_OAUTH_SECRET"),
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_response = requests.post("https://oauth2.googleapis.com/token", data=data)
        token_data = token_response.json()

        if "error" in token_data:
            return Response(
                {"error": "Failed to get access token from Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the access token from the response
        access_token = token_data.get("access_token", None)
        # print(access_token)
        if not access_token:
            return Response(
                {"error": "Failed to get access token from Google response."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use the access token to retrieve user information from Google
        user_info_response = requests.get(
            f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        )
        user_info = user_info_response.json()
        # print(user_info)
        # Extract the email and name from the user information
        email = user_info.get("email", None)
        name = user_info.get("name", None)
        if not email:
            return Response(
                {"error": "Failed to get email from Google user info."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not name:
            return Response(
                {"error": "Failed to get name from Google user info."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Login the user
            user = User.objects.get(email=email)
            jwt_token = GenerateToken.get_tokens_for_user(user)
            return Response(
                {"token": jwt_token, "msg": "Login Success"}, status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            userdata = {"email": email, "name": name}
            serializer = GoogleAuthSerializer(
                data=request.data, context={"userdata": userdata}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            user.provider = "google"
            user.is_verified = True
            user.save()
            token = GenerateToken.get_tokens_for_user(user)
            return Response(
                {"msg": "Registration Completed", "token": token},
                status=status.HTTP_201_CREATED,
            )

        except:
            return Response(
                {"errors": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )


class RestrictedPage(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated] if settings.ENABLE_AUTHENTICATION else []

    def get(self, request, format=None):
        return Response({"msg": "I am a restricted page"}, status=status.HTTP_200_OK)
