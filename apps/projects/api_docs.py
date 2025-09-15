from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import permission_classes

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_overview(request):
    """Complete API endpoints overview for frontend developers"""
    return Response({
        'base_url': 'http://localhost:8000',
        'authentication': {
            'register': 'POST /api/users/auth/register/',
            'verify_otp': 'POST /api/users/auth/verify-otp/',
            'complete-registration': '/api/users/auth/complete-registration/',
            'login': 'POST /api/users/auth/login/',
            'resend_otp': 'POST /api/users/auth/resend-otp/',
            'token_obtain': 'POST /api/token/',
            'token_refresh': 'POST /api/token/refresh/',
        },
        'users': {
            'list_users': 'GET /api/users/users/',
            'create_user': 'POST /api/users/users/',
            'get_user': 'GET /api/users/users/{id}/',
            'update_user': 'PUT /api/users/users/{id}/',
            'delete_user': 'DELETE /api/users/users/{id}/',
            'upload_avatar': 'POST /api/users/upload-avatar/',
            'delete_avatar': 'DELETE /api/users/delete-avatar/',
        },
        'skills': {
            'list_skills': 'GET /api/users/skills/',
            'create_skill': 'POST /api/users/skills/',
            'get_skill': 'GET /api/users/skills/{id}/',
            'user_skills': 'GET /api/users/user-skills/',
        },
        'badges': {
            'list_badges': 'GET /api/users/badges/',
            'user_badges': 'GET /api/users/user-badges/',
        },
        'projects': {
            'list_projects': 'GET /api/projects/projects/',
            'create_project': 'POST /api/projects/projects/',
            'get_project': 'GET /api/projects/projects/{id}/',
            'update_project': 'PUT /api/projects/projects/{id}/',
            'delete_project': 'DELETE /api/projects/projects/{id}/',
            'search_projects': 'GET /api/projects/projects/?search=keyword',
            'filter_projects': 'GET /api/projects/projects/?status=ongoing&location=kigali',
            'upload_image': 'POST /api/projects/projects/{id}/upload-image/',
            'delete_image': 'DELETE /api/projects/projects/{id}/delete-image/',
        },
        'project_skills': {
            'list': 'GET /api/projects/project-skills/',
            'create': 'POST /api/projects/project-skills/',
        },
        'attendance': {
            'list_attendance': 'GET /api/projects/attendances/',
            'create_attendance': 'POST /api/projects/attendances/',
            'project_attendance': 'GET /api/projects/projects/{id}/attendance/',
            'checkin': 'POST /api/projects/checkin/',
            'checkout': 'POST /api/projects/checkout/',
        },
        'qr_codes': {
            'generate_qr': 'POST /api/projects/projects/{id}/generate_qr_code/',
        },
        'certificates': {
            'list_certificates': 'GET /api/projects/certificates/',
            'generate_certificate': 'POST /api/projects/certificates/generate/{project_id}/',
        },
        'community': {
            'list_posts': 'GET /api/community/posts/',
            'create_post': 'POST /api/community/posts/',
            'get_post': 'GET /api/community/posts/{id}/',
            'update_post': 'PUT /api/community/posts/{id}/',
            'delete_post': 'DELETE /api/community/posts/{id}/',
            'upvote_post': 'POST /api/community/posts/{id}/upvote/',
            'post_comments': 'GET /api/community/posts/{id}/comments/',
            'add_comment': 'POST /api/community/posts/{id}/comments/',
            'list_comments': 'GET /api/community/comments/',
            'create_comment': 'POST /api/community/comments/',
        },
        'notifications': {
            'list_notifications': 'GET /api/notifications/notifications/',
            'mark_as_read': 'POST /api/notifications/notifications/{id}/mark_as_read/',
            'mark_all_read': 'POST /api/notifications/notifications/mark_all_as_read/',
            'notification_logs': 'GET /api/notifications/logs/',
        },
        'search':{
            'Basic Search': 'GET /api/projects/projects/?search={title}',
            'Status Filter': 'GET /api/projects/projects/?status={status}',
            'Location Filter': 'GET /api/projects/projects/?location={location}',
            'Date Range': 'GET /api/projects/projects/?date_from={date_from} &date_to={date_to}',
            'Combined Filters': 'GET /api/projects/projects/?search={title}&status={status}&location={location}',
            'Smart Discovery Features': 'GET /api/projects/projects/discover/',
            'Search Suggestions (Autocomplete)': 'GET /api/projects/projects/search_suggestions/?q=ki',
            ' Advanced Sorting & Pagination': 'GET /api/projects/projects/sorted_projects/',
        },
        'admin': {
            'admin_panel': 'GET /admin/',
        },
        'media': {
            'media_files': 'GET /media/{file_path}',
        }
    })