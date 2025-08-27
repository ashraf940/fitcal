import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import User
from .serializers import UserSerializer
GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"

class GoogleLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id_token'],
            properties={
                'id_token': openapi.Schema(type=openapi.TYPE_STRING, description='Google ID Token')
            }
        ),
        responses={200: UserSerializer},
        operation_description="Login/Register using Google ID token. Returns JWT tokens."
    )
    def post(self, request):
        token = request.data.get('id_token')
        if not token:
            return Response({"detail": "id_token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo.get("email")
            if not email:
                return Response({"detail": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)

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
