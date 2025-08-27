# users/apple_auth.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import jwt  # pip install pyjwt

class AppleAuthView(APIView):
    """
    Apple Sign-In API View
    POST request expects:
    {
        "identity_token": "<Apple identity token here>"
    }
    """

    def post(self, request):
        identity_token = request.data.get("identity_token")

        if not identity_token:
            return Response({"error": "Identity token missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Apple token decode karo (signature verify nahi kiya development mein)
            payload = jwt.decode(identity_token, options={"verify_signature": False})
            email = payload.get("email")
        except Exception as e:
            return Response({"error": "Invalid identity token", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({"error": "Email not found in token"}, status=status.HTTP_400_BAD_REQUEST)

        # User ko get ya create karo
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.username = email.split("@")[0]  # optional
            user.set_unusable_password()  # Apple login, password nahi chahiye
            user.save()

        # JWT token generate karo
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)
