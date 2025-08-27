# users/urls.py
from django.urls import path
from .views import RegisterView, ResendOTPView, VerifyOTPView
from rest_framework_simplejwt.views import TokenRefreshView
from .google_auth import GoogleLoginView  # correct import
from .apple_auth import AppleAuthView
from .token_views import EmailTokenObtainPairView  # optional if created

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),

    # Email/password JWT login
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Social / provider login
    path('google/', GoogleLoginView.as_view(), name='google_create'),
    path("apple/", AppleAuthView.as_view(), name="apple_auth"),
]
