from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
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
        print(f"🔥 DEBUG: OTP generated for {phone_number}: {otp.code}")
        # logger.debug(f"OTP generated for {phone_number}: {otp.code}")
        logger.info(f"📱 OTP generated for {phone_number}: {otp.code}")
                # Send SMS
        # sms_service = SMSService()
        sms_sent = True
        sms_result =  "SMS_DISABLED_LOGS_ONLY" 
        
        # Log that SMS is disabled
        print(f"📵 SMS DISABLED - Check logs for OTP: {otp.code}")
        logger.info(f"SMS sending disabled - OTP available in logs only")

        response_data = {
            "message": "OTP sent to phone number",
            "phone_number": phone_number,
            "sms_sent": sms_sent,
            "otp": otp.code  # for development only
        }

        # Include OTP in development mode only
        # if settings.DEBUG:
        #     response_data["otp"] = otp.code
           
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

# Complete registration of leader
@api_view(['POST'])
@permission_classes([AllowAny])
def complete_leader_registration(request):
    """" Step 3: Complete LEADER registration with verified phone """
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    sector = request.data.get('sector')
    experience = request.data.get('experience', '')

    if not all([phone_number, password, first_name, last_name, sector]):
        return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if OTP was verified
    verified_otp = OTP.objects.filter(phone_number=phone_number, is_verified=True).first()
    if not verified_otp:
        return Response({'error': 'Phone number not verified. Please verify OTP first.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate password
    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create user with LEader role
    user = User.objects.create_user(  #type: ignore
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name,
        role='leader'
    )
    user.set_password(password)
    user.is_verified = True
    user.sector = sector
    user.save()

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'message': 'Leader registration completed successfully'
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
    print(f"🔥 DEBUG: OTP resent for {phone_number}: {otp.code}")
    # logger.debug(f"OTP resent for {phone_number}: {otp.code}")
    logger.info(f"📱 OTP resent for {phone_number}: {otp.code}")
    # Send SMS
    # sms_service = SMSService()

    sms_sent = True
    sms_result = "SMS_DISABLED_LOGS_ONLY"
    
    # Log SMS result
    print(f"📵 SMS DISABLED - Check logs for OTP: {otp.code}")
    logger.info(f"SMS sending disabled - OTP available in logs only")

    response_data = {
        "message": "OTP resent successfully",
        "sms_sent": sms_sent,
        'otp_code': otp.code
    }

    # Include OTP in development mode only
    # if settings.DEBUG:
    #     response_data["otp_code"] = otp.code

@api_view(['POST'])
@permission_classes([AllowAny])
def make_migrations(request):
    """TEMPORARY: Create and apply migrations"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        
        # Step 1: Create migrations with --noinput flag
        call_command('makemigrations', '--noinput', stdout=out)
        
        # Step 2: Apply migrations
        call_command('migrate', '--noinput', stdout=out)
        
        return Response({
            'message': 'Migrations created and applied successfully',
            'output': out.getvalue()
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Migration failed'
        }, status=500)



@api_view(['POST'])
@permission_classes([AllowAny])
def force_migrate(request):
    """TEMPORARY: Force run migrations (REMOVE IN PRODUCTION)"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capture output
        out = StringIO()
        
        # Try different migration approaches
        try:
            # First try regular migrate
            call_command('migrate', stdout=out)
        except Exception as e1:
            try:
                # Then try with --run-syncdb (note the correct spelling)
                call_command('migrate', '--run-syncdb', stdout=out)
            except Exception as e2:
                # Finally try makemigrations then migrate
                call_command('makemigrations', stdout=out)
                call_command('migrate', stdout=out)
        
        return Response({
            'message': 'Migrations completed successfully',
            'output': out.getvalue()
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Migration failed'
        }, status=500)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_database(request):
    """NUCLEAR OPTION: Reset all migrations and recreate database"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        
        # Step 1: Reset all app migrations to zero
        call_command('migrate', 'users', 'zero', '--noinput', stdout=out)
        call_command('migrate', 'projects', 'zero', '--noinput', stdout=out)
        call_command('migrate', 'community', 'zero', '--noinput', stdout=out)
        call_command('migrate', 'notifications', 'zero', '--noinput', stdout=out)
        
        # Step 2: Delete all migration files (simulate)
        # This will be handled by recreating migrations
        
        # Step 3: Create fresh migrations
        call_command('makemigrations', 'users', '--noinput', stdout=out)
        call_command('makemigrations', 'projects', '--noinput', stdout=out)
        call_command('makemigrations', 'community', '--noinput', stdout=out)
        call_command('makemigrations', 'notifications', '--noinput', stdout=out)
        
        # Step 4: Apply all migrations
        call_command('migrate', '--noinput', stdout=out)
        
        return Response({
            'message': 'Database reset and recreated successfully',
            'output': out.getvalue()
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Database reset failed'
        }, status=500)
