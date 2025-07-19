from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser, OTPVerification, ShippingAddress
from .serializers import (
    RegisterSerializer, LoginSerializer, ProfileSerializer,
    ShippingAddressSerializer, OTPSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer
)
from .utils import send_otp_email
from django.utils import timezone

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user, 'email_verification')
            return Response({'message': 'User registered. Check email for OTP.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            otp = OTPVerification.objects.get(
                user__email=request.data.get('email'),
                purpose='email_verification',
                expires_at__gt=timezone.now()
            )
            serializer = OTPSerializer(otp, data=request.data)
            if serializer.is_valid():
                otp.user.is_verified = True
                otp.user.save()
                otp.delete()  # OTP is single-use
                return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except OTPVerification.DoesNotExist:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user and user.is_verified:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials or unverified email.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
            send_otp_email(user, 'password_reset')
            return Response({'message': 'OTP sent to email for password reset.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyResetOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            otp = OTPVerification.objects.get(
                user__email=request.data.get('email'),
                purpose='password_reset',
                expires_at__gt=timezone.now()
            )
            serializer = OTPSerializer(otp, data=request.data)
            if serializer.is_valid():
                return Response({'message': 'OTP verified. Proceed to reset password.'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except OTPVerification.DoesNotExist:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email=serializer.validated_data['email'])
                otp = OTPVerification.objects.filter(
                    user=user,
                    purpose='password_reset',
                    expires_at__gt=timezone.now()
                ).exists()
                if otp:
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    OTPVerification.objects.filter(user=user, purpose='password_reset').delete()
                    return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
                return Response({'error': 'No valid OTP found.'}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)