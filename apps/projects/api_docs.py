from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import permission_classes

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_overview(request):
    """Complete API endpoints overview for frontend developers"""
    
    # Dynamic base URL
    base_url = request.build_absolute_uri('/').rstrip('/')
    
    return Response({
        'api_info': {
            'title': 'UmugandaTech Backend API',
            'version': '1.0.0',
            'description': 'Complete API for Umuganda community service platform',
            'base_url': base_url,
            'documentation_url': f'{base_url}/swagger/',  # swagger
            'interactive_docs': f'{base_url}/swagger/',   # Primary docs
            'alternative_docs': f'{base_url}/redoc/',     # Alternative
            'admin_panel': f'{base_url}/admin/',
        },
        
        'authentication': {
            'description': 'JWT-based authentication with OTP verification',
            'register': {
                'method': 'POST',
                'url': '/api/users/auth/register/',
                'body': {'phone_number': '+250788123456'},
                'response': {'message': 'OTP sent', 'otp': '123456'}
            },
            'verify_otp': {
                'method': 'POST',
                'url': '/api/users/auth/verify-otp/',
                'body': {
                    'phone_number': '+250788123456',
                    'otp_code': '123456',
                    'password': 'secure123',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }
            },
            'complete_registration': {
                'method': 'POST',
                'url': '/api/users/auth/complete-registration/',
                'body': {
                    'phone_number': '+250788123456',
                    'password': 'secure123',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }
            },
            'complete_leader_registration': {
                'method': 'POST',
                'url': '/api/users/auth/complete-leader-registration/',
                'body': {
                    'phone_number': '+250788123456',
                    'password': 'secure123',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }
            },
            'login': {
                'method': 'POST',
                'url': '/api/users/auth/login/',
                'body': {'phone_number': '+250788123456', 'password': 'secure123'}
            },
            'resend_otp': {
                'method': 'POST',
                'url': '/api/users/auth/resend-otp/',
                'body': {'phone_number': '+250788123456'}
            },
            'token_refresh': {
                'method': 'POST',
                'url': '/api/token/refresh/',
                'body': {'refresh': 'jwt_refresh_token'}
            },
            'make_superuser': {
                'method': 'POST',
                'url': '/api/users/auth/make-superuser/',
                'description': 'Admin only endpoint'
            }
        },
        
        'users': {
            'description': 'User management and profiles',
            'list_users': 'GET /api/users/users/',
            'get_user': 'GET /api/users/users/{id}/',
            'update_user': 'PUT /api/users/users/{id}/',
            'delete_user': 'DELETE /api/users/users/{id}/',
            'upload_avatar': 'POST /api/users/upload-avatar/',
            'delete_avatar': 'DELETE /api/users/delete-avatar/',
        },
        
        'skills_and_badges': {
            'skills': {
                'list_skills': 'GET /api/users/skills/',
                'create_skill': 'POST /api/users/skills/',
                'get_skill': 'GET /api/users/skills/{id}/',
                'update_skill': 'PUT /api/users/skills/{id}/',
                'delete_skill': 'DELETE /api/users/skills/{id}/',
            },
            'user_skills': {
                'list_user_skills': 'GET /api/users/user-skills/',
                'add_user_skill': 'POST /api/users/user-skills/',
                'remove_user_skill': 'DELETE /api/users/user-skills/{id}/',
            },
            'badges': {
                'list_badges': 'GET /api/users/badges/',
                'create_badge': 'POST /api/users/badges/',
                'get_badge': 'GET /api/users/badges/{id}/',
                'update_badge': 'PUT /api/users/badges/{id}/',
                'delete_badge': 'DELETE /api/users/badges/{id}/',
            },
            'user_badges': {
                'list_user_badges': 'GET /api/users/user-badges/',
                'award_badge': 'POST /api/users/user-badges/',
                'get_user_badge': 'GET /api/users/user-badges/{id}/',
            }
        },
        
        'projects': {
            'description': 'Project management with advanced features',
            'crud_operations': {
                'list_projects': 'GET /api/projects/projects/',
                'create_project': 'POST /api/projects/projects/',
                'get_project': 'GET /api/projects/projects/{id}/ (PUBLIC)',
                'update_project': 'PUT /api/projects/projects/{id}/',
                'delete_project': 'DELETE /api/projects/projects/{id}/',
            },
            'discovery_and_search': {
                'discover_projects': {
                    'method': 'GET',
                    'url': '/api/projects/projects/discover/',
                    'description': 'Smart project recommendations',
                    'params': {'location': 'optional location filter'},
                    'returns': {
                        'nearby': 'Projects near user location',
                        'trending': 'Most attended projects (30 days)',
                        'urgent': 'Projects happening in 7 days',
                        'recent': 'Newly created projects (7 days)'
                    }
                },
                'search_suggestions': {
                    'method': 'GET',
                    'url': '/api/projects/projects/search_suggestions/?q={query}',
                    'description': 'Autocomplete suggestions',
                    'min_length': 2
                },
                'sorted_projects': {
                    'method': 'GET',
                    'url': '/api/projects/projects/sorted_projects/',
                    'params': {
                        'sort_by': ['created_at', 'datetime', 'title', 'volunteer_count', 'urgency'],
                        'order': ['asc', 'desc'],
                        'page': 'page number',
                        'page_size': 'items per page'
                    }
                }
            },
            'project_management': {
                'dashboard': 'GET /api/projects/projects/dashboard/',
                'my_projects': 'GET /api/projects/projects/my_projects/',
                'join_project': 'POST /api/projects/projects/{id}/join/',
                'leave_project': 'DELETE /api/projects/projects/{id}/leave/',
                'view_registrations': 'GET /api/projects/projects/{id}/registrations/ (Leaders only)',
            },
            'file_management': {
                'upload_image': 'POST /api/projects/projects/{id}/upload-image/',
                'delete_image': 'DELETE /api/projects/projects/{id}/delete-image/',
            }
        },
        
        'project_skills': {
            'list_project_skills': 'GET /api/projects/project-skills/',
            'add_project_skill': 'POST /api/projects/project-skills/',
            'get_project_skill': 'GET /api/projects/project-skills/{id}/',
            'update_project_skill': 'PUT /api/projects/project-skills/{id}/',
            'delete_project_skill': 'DELETE /api/projects/project-skills/{id}/',
        },
        
        'attendance_and_qr': {
            'description': 'QR code check-in system and attendance tracking',
            'qr_code_management': {
                'generate_qr': {
                    'method': 'POST',
                    'url': '/api/projects/projects/{id}/generate_qr_code/',
                    'description': 'Generate QR code (Leaders only)',
                    'auth': 'Required'
                },
                'get_qr': {
                    'method': 'GET',
                    'url': '/api/projects/projects/{id}/get_qr_code/',
                    'description': 'Get existing QR code (Leaders only)',
                    'auth': 'Required'
                }
            },
            'check_in_out': {
                'checkin': {
                    'method': 'POST',
                    'url': '/api/projects/checkin/',
                    'body': {'qr_code': 'umuganda_checkin:1:abc123'},
                    'description': 'Check-in to project using QR code'
                },
                'checkout': {
                    'method': 'POST',
                    'url': '/api/projects/checkout/',
                    'body': {'qr_code': 'umuganda_checkin:1:abc123'},
                    'description': 'Check-out from project using QR code'
                }
            },
            'attendance_records': {
                'list_attendances': 'GET /api/projects/attendances/',
                'create_attendance': 'POST /api/projects/attendances/',
                'get_attendance': 'GET /api/projects/attendances/{id}/',
                'update_attendance': 'PUT /api/projects/attendances/{id}/',
                'delete_attendance': 'DELETE /api/projects/attendances/{id}/',
                'project_attendance': 'GET /api/projects/projects/{id}/attendance/',
            }
        },
        
        'certificates': {
            'description': 'Certificate generation for completed projects',
            'list_certificates': 'GET /api/projects/certificates/',
            'get_certificate': 'GET /api/projects/certificates/{id}/',
            'generate_certificate': {
                'method': 'POST',
                'url': '/api/projects/certificates/generate/{project_id}/',
                'description': 'Generate certificate for completed project'
            }
        },
        
        'leader_following': {
            'description': 'Leader following system',
            'follow_leader': {
                'method': 'POST',
                'url': '/api/projects/leaders/{id}/follow/',
                'description': 'Follow a project leader'
            },
            'unfollow_leader': {
                'method': 'DELETE',
                'url': '/api/projects/leaders/{id}/unfollow/',
                'description': 'Unfollow a project leader'
            }
        },
        
        'community': {
            'description': 'Community posts and discussions',
            'posts': {
                'list_posts': 'GET /api/community/posts/',
                'create_post': 'POST /api/community/posts/',
                'get_post': 'GET /api/community/posts/{id}/',
                'update_post': 'PUT /api/community/posts/{id}/',
                'delete_post': 'DELETE /api/community/posts/{id}/',
                'upvote_post': 'POST /api/community/posts/{id}/upvote/',
            },
            'comments': {
                'list_comments': 'GET /api/community/comments/',
                'create_comment': 'POST /api/community/comments/',
                'get_comment': 'GET /api/community/comments/{id}/',
                'update_comment': 'PUT /api/community/comments/{id}/',
                'delete_comment': 'DELETE /api/community/comments/{id}/',
            }
        },
        
        'notifications': {
            'description': 'Real-time notification system',
            'notification_management': {
                'list_notifications': 'GET /api/notifications/notifications/',
                'create_notification': 'POST /api/notifications/notifications/',
                'get_notification': 'GET /api/notifications/notifications/{id}/',
                'update_notification': 'PUT /api/notifications/notifications/{id}/',
                'delete_notification': 'DELETE /api/notifications/notifications/{id}/',
            },
            'notification_actions': {
                'unread_notifications': 'GET /api/notifications/notifications/unread/',
                'mark_as_read': 'POST /api/notifications/notifications/{id}/mark_as_read/',
                'mark_all_as_read': 'POST /api/notifications/notifications/mark_all_as_read/',
                'mark_multiple_as_read': {
                    'method': 'POST',
                    'url': '/api/notifications/notifications/mark_multiple_as_read/',
                    'body': {'notification_ids': [1, 2, 3, 4]}
                }
            },
            'notification_logs': {
                'list_logs': 'GET /api/notifications/logs/',
                'get_log': 'GET /api/notifications/logs/{id}/',
            },
            'notification_types': [
                'project_update',
                'new_comment',
                'project_reminder',
                'upvote_received',
                'project_created',
                'project_registration',
                'leader_new_project'
            ]
        },
        
        'search_and_filters': {
            'description': 'Advanced search and filtering capabilities',
            'basic_search': {
                'url': 'GET /api/projects/projects/?search={keyword}',
                'example': '/api/projects/projects/?search=tree planting'
            },
            'status_filter': {
                'url': 'GET /api/projects/projects/?status={status}',
                'options': ['planned', 'ongoing', 'completed', 'cancelled'],
                'example': '/api/projects/projects/?status=ongoing'
            },
            'location_filter': {
                'url': 'GET /api/projects/projects/?location={location}',
                'example': '/api/projects/projects/?location=kigali'
            },
            'date_range_filter': {
                'url': 'GET /api/projects/projects/?date_from={date}&date_to={date}',
                'example': '/api/projects/projects/?date_from=2024-01-01&date_to=2024-12-31'
            },
            'combined_filters': {
                'url': 'GET /api/projects/projects/?search={keyword}&status={status}&location={location}',
                'example': '/api/projects/projects/?search=environment&status=planned&location=nyarugenge'
            }
        },
        
        'data_models': {
            'user_object': {
                'id': 1,
                'phone_number': '+250788123456',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'sector': 'Kigali',
                'role': 'volunteer',
                'avatar_url': 'http://example.com/media/avatars/user1.jpg',
                'skills': [],
                'badges': [],
                'achievement_stats': {
                    'completed_projects': 5,
                    'total_badges': 3,
                    'latest_badge': 'Community Champion'
                },
                'created_at': '2024-01-01T00:00:00Z'
            },
            'project_object': {
                'id': 1,
                'title': 'Tree Planting Initiative',
                'description': 'Community tree planting project',
                'sector': 'Kigali',
                'datetime': '2024-01-15T09:00:00Z',
                'location': 'Nyamirambo',
                'required_volunteers': 50,
                'image_url': 'http://example.com/media/project/tree.jpg',
                'admin': 1,
                'admin_name': 'John Doe',
                'status': 'ongoing',
                'volunteer_count': 25,
                'registered_count': 30,
                'is_user_registered': True,
                'skills': [],
                'created_at': '2024-01-01T00:00:00Z'
            },
            'notification_object': {
                'id': 1,
                'user': 'user_object',
                'title': 'New Registration',
                'message': 'John joined your project Tree Planting',
                'notification_type': 'project_registration',
                'project': 'project_object',
                'is_read': False,
                'created_at': '2024-01-01T00:00:00Z'
            }
        },
        
        'authentication_headers': {
            'description': 'Include JWT token in all authenticated requests',
            'header_format': 'Authorization: Bearer {access_token}',
            'example': 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
        },
        
        'error_responses': {
            'unauthorized': {
                'status': 401,
                'response': {'detail': 'Authentication credentials were not provided.'}
            },
            'forbidden': {
                'status': 403,
                'response': {'error': 'Only project admin can perform this action.'}
            },
            'bad_request': {
                'status': 400,
                'response': {'field_name': ['This field is required.']}
            },
            'not_found': {
                'status': 404,
                'response': {'detail': 'Not found.'}
            },
            'project_full': {
                'status': 400,
                'response': {'error': 'Project is full'}
            }
        },
        
        'special_features': {
            'public_endpoints': [
                'GET /api/projects/projects/{id}/ (Project details)',
                'GET /api/projects/api-overview/ (This documentation)'
            ],
            'automatic_notifications': {
                'project_join': 'Leader notified when someone joins their project',
                'new_comment': 'Post author notified of new comments',
                'post_upvote': 'Post author notified of upvotes',
                'project_created': 'All users notified of new projects',
                'leader_followers': 'Followers notified of leader activity'
            },
            'gamification': {
                'badges': 'Automatic badge awarding system',
                'certificates': 'PDF certificate generation',
                'achievement_stats': 'User progress tracking'
            }
        }
    })
