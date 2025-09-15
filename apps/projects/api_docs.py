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
            'documentation_url': f'{base_url}/api/projects/api-overview/',
            'admin_panel': f'{base_url}/admin/',
        },
        
        'authentication': {
            'description': '3-step authentication process with OTP verification',
            'step_1_register': {
                'method': 'POST',
                'url': '/api/users/auth/register/',
                'description': 'Send OTP to phone number',
                'body': {
                    'phone_number': '788123456'
                },
                'response': {
                    'message': 'OTP sent to phone number',
                    'phone_number': '788123456',
                    'otp': '123456'  # Development only
                }
            },
            'step_2_verify_otp': {
                'method': 'POST',
                'url': '/api/users/auth/verify-otp/',
                'description': 'Verify OTP code only (no user creation)',
                'body': {
                    'phone_number': '788123456',
                    'otp_code': '123456'
                },
                'response': {
                    'message': 'OTP verified successfully',
                    'verified': True
                }
            },
            'step_3_complete_registration': {
                'method': 'POST',
                'url': '/api/users/auth/complete-registration/',
                'description': 'Complete user registration with verified phone',
                'body': {
                    'phone_number': '788123456',
                    'password': 'secure123',
                    'first_name': 'John',
                    'last_name': 'Doe'
                },
                'response': {
                    'access': 'jwt_access_token',
                    'refresh': 'jwt_refresh_token',
                    'user': 'user_object',
                    'message': 'Registration completed successfully'
                }
            },
            'login': {
                'method': 'POST',
                'url': '/api/users/auth/login/',
                'body': {
                    'phone_number': '788123456',
                    'password': 'secure123'
                }
            },
            'resend_otp': {
                'method': 'POST',
                'url': '/api/users/auth/resend-otp/',
                'body': {
                    'phone_number': '788123456'
                }
            },
            'token_refresh': {
                'method': 'POST',
                'url': '/api/token/refresh/',
                'body': {
                    'refresh': 'jwt_refresh_token'
                }
            }
        },
        
        'users': {
            'description': 'User management endpoints',
            'list_users': 'GET /api/users/users/',
            'get_user': 'GET /api/users/users/{id}/',
            'update_user': 'PUT /api/users/users/{id}/',
            'upload_avatar': 'POST /api/users/upload-avatar/',
            'delete_avatar': 'DELETE /api/users/delete-avatar/',
        },
        
        'skills_and_badges': {
            'list_skills': 'GET /api/users/skills/',
            'create_skill': 'POST /api/users/skills/',
            'user_skills': 'GET /api/users/user-skills/',
            'list_badges': 'GET /api/users/badges/',
            'user_badges': 'GET /api/users/user-badges/',
        },
        
        'projects': {
            'description': 'Project management with advanced search and discovery',
            'list_projects': 'GET /api/projects/projects/',
            'create_project': 'POST /api/projects/projects/',
            'get_project': 'GET /api/projects/projects/{id}/',
            'update_project': 'PUT /api/projects/projects/{id}/',
            'delete_project': 'DELETE /api/projects/projects/{id}/',
            'dashboard_stats': 'GET /api/projects/projects/dashboard/',
            'my_projects': 'GET /api/projects/projects/my_projects/',
            'upload_image': 'POST /api/projects/projects/{id}/upload-image/',
            'delete_image': 'DELETE /api/projects/projects/{id}/delete-image/',
        },
        
        'advanced_search': {
            'description': 'Advanced search and discovery features',
            'basic_search': {
                'url': 'GET /api/projects/projects/?search={keyword}',
                'example': '/api/projects/projects/?search=tree planting'
            },
            'filter_by_status': {
                'url': 'GET /api/projects/projects/?status={status}',
                'options': ['planned', 'ongoing', 'completed', 'cancelled'],
                'example': '/api/projects/projects/?status=ongoing'
            },
            'filter_by_location': {
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
        
        'discovery_features': {
            'description': 'Smart project discovery and recommendations',
            'discover_projects': {
                'method': 'GET',
                'url': '/api/projects/projects/discover/',
                'description': 'Get personalized project recommendations',
                'optional_params': {
                    'location': 'Override user location for nearby projects'
                },
                'response_categories': {
                    'nearby': 'Projects near user location',
                    'trending': 'Most attended projects (last 30 days)',
                    'urgent': 'Projects happening in next 7 days',
                    'recent': 'Newly created projects (last 7 days)'
                }
            },
            'search_suggestions': {
                'method': 'GET',
                'url': '/api/projects/projects/search_suggestions/?q={query}',
                'description': 'Autocomplete suggestions for search',
                'min_query_length': 2,
                'example': '/api/projects/projects/search_suggestions/?q=ki',
                'response': {
                    'suggestions': {
                        'locations': ['Kigali', 'Kimisagara'],
                        'titles': ['Kigali Clean-up'],
                        'sectors': ['Kicukiro']
                    }
                }
            }
        },
        
        'advanced_sorting': {
            'description': 'Advanced sorting and pagination',
            'sorted_projects': {
                'method': 'GET',
                'url': '/api/projects/projects/sorted_projects/',
                'parameters': {
                    'sort_by': {
                        'options': ['created_at', 'datetime', 'title', 'volunteer_count', 'required_volunteers', 'urgency'],
                        'default': 'created_at'
                    },
                    'order': {
                        'options': ['asc', 'desc'],
                        'default': 'desc'
                    },
                    'page': {
                        'description': 'Page number',
                        'default': 1
                    },
                    'page_size': {
                        'description': 'Items per page',
                        'default': 10
                    }
                },
                'examples': {
                    'sort_by_popularity': '/api/projects/projects/sorted_projects/?sort_by=volunteer_count&order=desc',
                    'sort_by_urgency': '/api/projects/projects/sorted_projects/?sort_by=datetime&order=asc',
                    'with_pagination': '/api/projects/projects/sorted_projects/?page=1&page_size=5'
                }
            }
        },
        
        'attendance_and_qr': {
            'description': 'QR code check-in system and attendance tracking',
            'generate_qr_code': {
                'method': 'POST',
                'url': '/api/projects/projects/{id}/generate_qr_code/',
                'description': 'Generate QR code for project (Leaders only)',
                'auth_required': True
            },
            'checkin': {
                'method': 'POST',
                'url': '/api/projects/checkin/',
                'body': {
                    'qr_code': 'umuganda_checkin:1:abc123'
                }
            },
            'checkout': {
                'method': 'POST',
                'url': '/api/projects/checkout/',
                'body': {
                    'qr_code': 'umuganda_checkin:1:abc123'
                }
            },
            'project_attendance': 'GET /api/projects/projects/{id}/attendance/',
            'list_attendances': 'GET /api/projects/attendances/'
        },
        
        'certificates': {
            'description': 'Certificate generation for completed projects',
            'list_certificates': 'GET /api/projects/certificates/',
            'generate_certificate': 'POST /api/projects/certificates/generate/{project_id}/',
        },
        
        'community': {
            'description': 'Community posts and discussions',
            'list_posts': 'GET /api/community/posts/',
            'create_post': 'POST /api/community/posts/',
            'get_post': 'GET /api/community/posts/{id}/',
            'update_post': 'PUT /api/community/posts/{id}/',
            'delete_post': 'DELETE /api/community/posts/{id}/',
        },
        
        'notifications': {
            'list_notifications': 'GET /api/notifications/user-badges/',
        },
        
        'data_models': {
            'user_object': {
                'id': 1,
                'phone_number': '788123456',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'sector': 'Kigali',
                'role': 'volunteer',
                'avatar_url': 'http://example.com/media/avatars/user1.jpg',
                'skills': [],
                'badges': [],
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
                'created_at': '2024-01-01T00:00:00Z',
                'volunteer_count': 25,
                'is_user_registered': True,
                'skills': []
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
                'response': {
                    'detail': 'Authentication credentials were not provided.'
                }
            },
            'bad_request': {
                'status': 400,
                'response': {
                    'field_name': ['This field is required.']
                }
            },
            'not_found': {
                'status': 404,
                'response': {
                    'detail': 'Not found.'
                }
            }
        }
    })
