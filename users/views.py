from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import User, EmailOTP
from .serializers import UserSerializer, RegisterSerializer, VerifyOTPSerializer, ResendOTPSerializer
from .utils import create_and_send_otp

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: "User created. OTP sent to email."},
        operation_description="Register a user (email + optional password)."
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = False
        user.save()

        create_and_send_otp(user)  # async email

        return Response({"detail": "User created. OTP sent to email."}, status=status.HTTP_201_CREATED)


class ResendOTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=ResendOTPSerializer,
        responses={200: "OTP resent", 404: "user not found"},
        operation_description="Resend OTP to registered email."
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "email required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)

        create_and_send_otp(user)  # async resend
        return Response({"detail": "OTP resent"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=VerifyOTPSerializer,
        responses={200: UserSerializer},
        operation_description="Verify OTP and activate user. Returns JWT tokens."
    )
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        if not email or not code:
            return Response({"detail": "email and code required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)

        otp_qs = EmailOTP.objects.filter(
            user=user, code=code, used=False, expires_at__gt=timezone.now()
        ).order_by("-created_at")

        if not otp_qs.exists():
            return Response({"detail": "invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)

        otp = otp_qs.first()
        otp.used = True
        otp.save()

        user.is_active = True
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        })


from google.auth.transport import requests
from google.oauth2 import id_token
from drf_yasg import openapi


class GoogleLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id_token"],
            properties={
                "id_token": openapi.Schema(type=openapi.TYPE_STRING, description="Google ID Token"),
            },
        ),
        responses={200: UserSerializer},
        operation_description="Login/Register using Google ID token. Returns JWT tokens."
    )
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"detail": "id_token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Google se token verify karo
            idinfo = id_token.verify_oauth2_token(token, requests.Request())

            email = idinfo.get("email")
            if not email:
                return Response({"detail": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)

            # User ko fetch ya create karo
            user, created = User.objects.get_or_create(email=email)
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            })

        except Exception as e:
            return Response({"detail": f"invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
import requests

class AppleLoginView(APIView):
    def post(self, request):
        id_token = request.data.get("id_token")
        if not id_token:
            return Response({"error": "id_token missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify token with Apple's public keys
        apple_keys = requests.get("https://appleid.apple.com/auth/keys").json()
        # (yahan par jwt.decode use hota hai with Apple public key)

        # Agar valid hua to user create/login
        return Response({"msg": "Apple login success"})