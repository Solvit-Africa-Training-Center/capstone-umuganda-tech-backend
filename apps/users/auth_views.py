from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, OTP
from .serializers import (
    RegisterSerializer,
    LoginSerializer, UserSerializer
)
from .sms_service import SMSService
from django.conf import settings
import logging 

# Add logger for debug
logger = logging.getLogger(__name__)    

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
     """Step 1: Send OTP to phone number"""
     serializer = RegisterSerializer(data=request.data)
     if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number'] #type: ignore
        
        # Generate and send OTP
        otp = OTP.generate_otp(phone_number)

        # Log OTP for debugging gusa
        logger.debug(f"OTP generated for {phone_number}: {otp.code}")
        logger.info(f"📱 OTP generated for {phone_number}: {otp.code}")

        # Send SMS
        sms_service = SMSService()
        sms_sent, sms_result = sms_service.send_otp(phone_number, otp.code) #type: ignore
        
        # Log SMS result
        if sms_sent:
            logger.info(f"SMS sent successfully to {phone_number}. SID: {sms_result}")
        else:
            logger.error(f"Failed to send SMS to {phone_number}: Error: {sms_result}")

        response_data = {
            "message": "OTP sent to phone number",
            "phone_number": phone_number,
            "sms_sent": sms_sent
            # "otp": otp.code  # for development only
        }

        # Include OTP in development mode only
        if settings.DEBUG:
            response_data["otp"] = otp.code
           
        return Response(response_data, status=status.HTTP_200_OK) 
     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """Step 2: Verify OTP code only (no user creation)"""
    phone_number = request.data.get('phone_number')
    otp_code = request.data.get('otp_code')
    
    if not phone_number or not otp_code:
        return Response({'error': 'Phone number and OTP code are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp = OTP.objects.filter(phone_number=phone_number, code=otp_code, is_verified=False).latest('created_at')
        if otp.is_expired():
            return Response({'error': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark OTP as verified
        otp.is_verified = True
        otp.save()
        
        return Response({
            'message': 'OTP verified successfully',
            'phone_number': phone_number,
            'verified': True
        }, status=status.HTTP_200_OK)
        
    except OTP.DoesNotExist:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
@permission_classes([AllowAny])
def complete_registration(request):
    """Step 3: Complete user registration with verified phone"""
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    
    if not all([phone_number, password, first_name, last_name]):
        return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if OTP was verified
    verified_otp = OTP.objects.filter(phone_number=phone_number, is_verified=True).first()
    if not verified_otp:
        return Response({'error': 'Phone number not verified. Please verify OTP first.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already exists
    if User.objects.filter(phone_number=phone_number).exists():
        return Response({'error': 'User already exists with this phone number.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password
    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create user
    user = User.objects.create_user(  #type: ignore
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name
    )
    user.set_password(password)
    user.is_verified = True
    user.save()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'message': 'Registration completed successfully'
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def make_superuser(request):
    """ Make user  superuser - Will be removed in """
    phone_number = request.data.get('phone_number', '7880000000')

    try: 
        user = User.objects.get(phone_number=phone_number)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save()

        return Response({
            'message': 'User is now a superuser',
            'phone_number': phone_number,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser

        })
    except User.DoesNotExist:
        return Response({'error': 'User does not found.'}, status=404)

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

    # Log OTP for debugging
    logger.debug(f"OTP resent for {phone_number}: {otp.code}")
    logger.info(f"📱 OTP resent for {phone_number}: {otp.code}")

    # Send SMS
    sms_service = SMSService()
    sms_sent, sms_result = sms_service.send_otp(phone_number, otp.code) #type: ignore
    
    # Log SMS result
    if sms_sent:
        logger.info(f"SMS resent successfully to {phone_number}. SID: {sms_result}")
    else:
        logger.error(f"Failed to send SMS to {phone_number}: Error: {sms_result}")

    response_data = {
        "message": "OTP resent successfully",
        "sms_sent": sms_sent
    }

    # Include OTP in development mode only
    if settings.DEBUG:
        response_data["otp_code"] = otp.code

    return Response(response_data, status=status.HTTP_200_OK)
