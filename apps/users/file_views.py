from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from django.shortcuts import get_object_or_404
from PIL import Image
import os
from .models import User
from .serializers import UserSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """ Upload user avatar """
    if 'avatar' not in request.FILES:
        return Response({"error": "No avatar file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    avatar_file = request.FILES['avatar']

    # Validate image file
    if not avatar_file.content_type.startswith('image/'):
        return Response({"error": "File must be an image."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size(max 5mb)
    if avatar_file.size > 5 * 1024 * 1024:
        return Response({"error": "Image size must be less than 5MB."}, status=status.HTTP_400_BAD_REQUEST)
    
    # delete old avatar if exists
    user = request.user
    if user.avatar:
        if os.path.isfile(user.avatar.path):
            os.remove(user.avatar.path)

    # Save new avatar
    user.avatar = avatar_file
    user.save()

    return Response({
        'message': 'Avatar uploaded successfully.',
        'avatar_url': request.build_absolute_uri(user.avatar.url) if user.avatar else None,
        'user': UserSerializer(user, context={'request': request}).data
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """ Delete user avatar """
    user = request.user

    if not user.avatar:
        return Response({"error": "No avatar to delete."}, status=status.HTTP_400_BAD_REQUEST)
    
    # delete avatar file fffrom storage
    if os.path.isfile(user.avatar.path):
        os.remove(user.avatar.path)

    # Remove fro database
    user.avatar = None
    user.save()

    return Response({
        'message': 'Avatar deleted successfully.',
        'user': UserSerializer(user, context={'request': request}).data
        }, status=status.HTTP_200_OK)