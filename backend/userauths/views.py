from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str

import logging
import requests

# Restframework
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone

# Others
import json
import random

# Schema
from drf_spectacular.utils import extend_schema, inline_serializer

# Serializers
from userauths.serializer import MyTokenObtainPairSerializer, ProfileSerializer, RegisterSerializer, UserSerializer


# Models
from userauths.models import Profile, User

logger = logging.getLogger(__name__)


def send_email_brevo(*, to_email: str, to_name: str, subject: str, html_content: str, text_content: str) -> None:
    api_key = getattr(settings, "BREVO_API_KEY", "")
    if not api_key:
        raise RuntimeError("Brevo API key not configured")

    sender_email = getattr(settings, "BREVO_SENDER_EMAIL", "")
    sender_name = getattr(settings, "BREVO_SENDER_NAME", "")
    if not sender_email:
        raise RuntimeError("Brevo sender email not configured")

    html_content = "" if html_content is None else str(html_content)
    text_content = "" if text_content is None else str(text_content)
    if not text_content.strip():
        text_content = subject or " "

    payload = {
        "sender": {"email": sender_email, "name": sender_name},
        "to": [{"email": to_email, "name": to_name or ""}],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
    }

    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers={
            "api-key": api_key,
            "accept": "application/json",
            "content-type": "application/json",
        },
        timeout=getattr(settings, "BREVO_TIMEOUT", 15),
    )
    if not resp.ok:
        raise RuntimeError(f"Brevo API error {resp.status_code}: {resp.text}")


# This code defines a DRF View class called MyTokenObtainPairView, which inherits from TokenObtainPairView.
class MyTokenObtainPairView(TokenObtainPairView):
    # Here, it specifies the serializer class to be used with this view.
    serializer_class = MyTokenObtainPairSerializer

# This code defines another DRF View class called RegisterView, which inherits from generics.CreateAPIView.
class RegisterView(generics.CreateAPIView):
    # It sets the queryset for this view to retrieve all User objects.
    queryset = User.objects.all()
    # It specifies that the view allows any user (no authentication required).
    permission_classes = (AllowAny,)
    # It sets the serializer class to be used with this view.
    serializer_class = RegisterSerializer



# This is a DRF view defined as a Python function using the @api_view decorator.
@api_view(['GET'])
@extend_schema(
    responses=inline_serializer(
        name="RoutesResponse",
        fields={
            "routes": inline_serializer(name="Routes", fields={}),
        },
    ),
)
def getRoutes(request):
    # It defines a list of API routes that can be accessed.
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/test/'
    ]
    # It returns a DRF Response object containing the list of routes.
    return Response(routes)


# This is another DRF view defined as a Python function using the @api_view decorator.
# It is decorated with the @permission_classes decorator specifying that only authenticated users can access this view.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    request=inline_serializer(
        name="TestEndPointRequest",
        fields={
            "text": inline_serializer(name="TestEndPointText", fields={}),
        },
    ),
    responses=inline_serializer(
        name="TestEndPointResponse",
        fields={
            "response": inline_serializer(name="TestEndPointResponseValue", fields={}),
        },
    ),
)
def testEndPoint(request):
    # Check if the HTTP request method is GET.
    if request.method == 'GET':
        # If it is a GET request, it constructs a response message including the username.
        data = f"Congratulations {request.user}, your API just responded to a GET request."
        # It returns a DRF Response object with the response data and an HTTP status code of 200 (OK).
        return Response({'response': data}, status=status.HTTP_200_OK)
    # Check if the HTTP request method is POST.
    elif request.method == 'POST':
        try:
            # If it's a POST request, it attempts to decode the request body from UTF-8 and load it as JSON.
            body = request.body.decode('utf-8')
            data = json.loads(body)
            # Check if the 'text' key exists in the JSON data.
            if 'text' not in data:
                # If 'text' is not present, it returns a response with an error message and an HTTP status of 400 (Bad Request).
                return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
            text = data.get('text')
            # If 'text' exists, it constructs a response message including the received text.
            data = f'Congratulations, your API just responded to a POST request with text: {text}'
            # It returns a DRF Response object with the response data and an HTTP status code of 200 (OK).
            return Response({'response': data}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            # If there's an error decoding the JSON data, it returns a response with an error message and an HTTP status of 400 (Bad Request).
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
    # If the request method is neither GET nor POST, it returns a response with an error message and an HTTP status of 400 (Bad Request).
    return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)


# This code defines another DRF View class called ProfileView, which inherits from generics.RetrieveAPIView and used to show user profile view.
class ProfileView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']

        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        return profile
    

def generate_numeric_otp(length=7):
        # Generate a random 7-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        return otp

class PasswordEmailVerify(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        email = self.kwargs['email']
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"message": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        link = f"{settings.SITE_URL}/create-new-password?uidb64={uidb64}&token={token}"

        merge_data = {
            'link': link,
            'username': user.username,
        }
        subject = f"Password Reset Request"
        text_body = render_to_string("email/password_reset.txt", merge_data)
        html_body = render_to_string("email/password_reset.html", merge_data)

        try:
            send_email_brevo(
                to_email=user.email,
                to_name=user.username,
                subject=subject,
                html_content=html_body,
                text_content=text_body,
            )
        except Exception as e:
            logger.exception("Password reset email send failed")
            message = "Unable to send reset email"
            if getattr(settings, "DEBUG", False):
                message = f"Unable to send reset email: {e}"
            return Response({"message": message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
    

class PasswordChangeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        payload = request.data

        uidb64 = payload.get('uidb64')
        token = payload.get('token')
        password = payload.get('password')

        if not uidb64 or not token or not password:
            return Response({"message": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"message": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"message": "Invalid or expired reset token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.otp = ""
        user.reset_token = ""
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_at = None
        user.last_login = timezone.now()
        user.save(update_fields=[
            "password",
            "otp",
            "reset_token",
            "failed_login_attempts",
            "is_locked",
            "locked_at",
            "last_login",
        ])

        return Response({"message": "Password Changed Successfully"}, status=status.HTTP_201_CREATED)
