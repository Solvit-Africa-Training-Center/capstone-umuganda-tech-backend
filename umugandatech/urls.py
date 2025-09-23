from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger setup
schema_view = get_schema_view(
   openapi.Info(
      title="Umuganda Tech API",
      default_version='v1',
      description="""
      # Umuganda Community Platform API
      
      This API provides endpoints for managing community projects, user participation, 
      and generating reports for the Umuganda platform.
      
      ## Authentication
      Use JWT tokens for authentication. Get your token from `/api/users/auth/login/`
      
      ## User Roles
      - **Admin**: Full system access
      - **Leader**: Can manage projects and view reports
      - **Volunteer**: Can participate in projects

      ## Quick Start
      1. Register: `POST /api/users/auth/register/`
      2. Verify OTP: `POST /api/users/auth/verify-otp/`
      3. Complete Registration as volunteer: `POST /api/users/auth/complete-registration/`
      4. Complete Registration as Leader: `POST /api/users/auth/complete-leader-registration/`
      5. Login: `POST /api/users/auth/login/`
      6. Use token in Authorization header: `Bearer {your_token}`
      """,
      #terms_of_service="https://www.umuganda.com/terms/",
      contact=openapi.Contact(email="admin@umuganda.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Root redirect to swagger
def redirect_to_swagger(request):
    return redirect('/swagger/')

urlpatterns = [
    # Root URL redirects to Swagger
    path('', redirect_to_swagger, name='root-redirect'),
    
    # API Documentation (Primary)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),  # Alternative URL
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Admin & API endpoints
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/community/', include('apps.community.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
# Serve static and media files (works in both development and production with whiteNoise)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
