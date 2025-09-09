from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, OTP
from .serializers import (
    RegisterSerializer, VerifyOTPSerializer,
    LoginSerializer, UserSerializer
)

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']  #type: ignore

        # Generate  and send OTP kuri phone number
        otp = OTP.generate_otp(phone_number)
        # send_otp_via_sms(phone_number, otp)  # Implement this function to
        
        # TODO: Send SMS with OTP code
        # for development, return the OTP in the response
        return Response({
            "message": "OTP sent to phone number",
            "phone_number": phone_number,
            "otp": otp.code  # for development only, will be removed in production
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    # print("Request data:", request.data)
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number'] #type: ignore
        password = serializer.validated_data['password']  #type: ignore
        otp = serializer.validated_data['otp']  #type: ignore

        #Mark OTP  as verified
        otp.is_verified = True
        otp.save()

        # Create or get user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'first_name': serializer.validated_data.get('first_name', ''),
                'last_name': serializer.validated_data.get('last_name', ''),
            }
        )

        # Set password if  provided
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(password)
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    # print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']  #type: ignore

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({'error': 'Phone_number is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate new OTP
    otp = OTP.generate_otp(phone_number)

    # TODO:  Send SMS with OTP code
    return Response({
        'message': 'OTP resent successfully.',
        'otp_code': otp.code  # for development only, will be removed in production
    }, status=status.HTTP_200_OK)