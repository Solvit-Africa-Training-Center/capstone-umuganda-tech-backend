from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import os
from .models import Project
from .serializers import ProjectSerializer
from django.conf import settings

def is_safe_path(path):
    """ Validate that the path is within the media directory """
    try:
        # get absolute paths
        abs_path = os.path.abspath(path)
        media_root = os.path.abspath(settings.MEDIA_ROOT)

        # check if the path starts with media root
        return abs_path.startswith(media_root)
    except (OSError, ValueError):
        return False

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_project_image(request, project_id):
    """ Upload project image (Leaders only) """
    project = get_object_or_404(Project, id=project_id)

    #Check if user is project admin (Leader)
    if project.admin != request.user:
        return Response({"error": "Only project admin(leader) can upload project image."}, status=status.HTTP_403_FORBIDDEN)
    
    if 'image' not in request.FILES:
        return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    image_file = request.FILES['image']

    # Validate file type
    if not image_file.content_type.startswith('image/'):
        return Response({"error": "File must be an image."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (max 10mb) kuri project images
    if image_file.size > 10 * 1024 * 1024:
        return Response({"error": "File size must be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete old image if exists
    if project.image:
        if is_safe_path(project.image.path) and os.path.exists(project.image.path):
            os.remove(project.image.path)

    # Save new image
    project.image = image_file
    project.save()

    return Response({
        'message': 'Project image uploaded successfully.',
        'image_url': request.build_absolute_uri(project.image.url) if project.image else None,
        'project': ProjectSerializer(project, context={'request': request}).data
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project_image(request, project_id):
    """ Delete project image (Leaders only) """
    project = get_object_or_404(Project, id=project_id)

    # Check if user is project admin (Leader)
    if project.admin != request.user:
        return Response({'error': 'Only project admin(leader) can delete project image.'}, status=status.HTTP_403_FORBIDDEN)
    
    if not project.image:
        return Response({'error': 'No project image to delete.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete file from storage
    if is_safe_path(project.image.path) and os.path.exists(project.image.path):
        os.remove(project.image.path)

    # Remove from database
    project.image = None #type: ignore
    project.save()

    return Response({
        'message': 'Project image deleted successfully.',
        'project': ProjectSerializer(project, context={'request': request}).data
    }, status=status.HTTP_200_OK)