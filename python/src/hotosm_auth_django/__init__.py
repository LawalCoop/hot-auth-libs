"""
hotosm_auth_django: Django integration for HOTOSM authentication.

This package provides Django-specific functionality:
- Django app with ORM models and migrations
- Authentication middleware
- View decorators (@login_required, @osm_required)
- OSM OAuth views
- Admin routes for managing user mappings

Quick Start:
    1. Add to INSTALLED_APPS:

    INSTALLED_APPS = [
        ...
        'hotosm_auth_django',
        ...
    ]

    2. Run migrations:

    python manage.py migrate hotosm_auth_django

    3. Add middleware to settings.py:

    MIDDLEWARE = [
        ...
        'hotosm_auth_django.HankoAuthMiddleware',
    ]

    4. Use in views:

    from hotosm_auth_django import login_required, osm_required

    @login_required
    def my_view(request):
        user = request.hotosm.user
        return JsonResponse({"email": user.email})
"""

default_app_config = 'hotosm_auth_django.apps.HotosmAuthDjangoConfig'

# Middleware and authentication
from hotosm_auth_django.middleware import (
    HankoAuthMiddleware,
    login_required,
    osm_required,
    get_auth_config,
    get_jwt_validator,
    get_cookie_crypto,
    get_token_from_request,
    get_current_user,
    get_osm_connection,
    set_osm_cookie,
    clear_osm_cookie,
    get_mapped_user_id,
    get_auth_status,
    create_user_mapping,
)

# Admin routes
from hotosm_auth_django.admin_routes import (
    create_admin_urlpatterns,
    get_admin_emails,
    is_admin_user,
)

# OSM OAuth views
from hotosm_auth_django.osm_views import (
    osm_login,
    osm_callback,
    osm_status,
    osm_disconnect,
    urlpatterns as osm_urlpatterns,
)

# Django ORM models
from hotosm_auth_django.models import HankoUserMapping

__all__ = [
    # Middleware
    "HankoAuthMiddleware",
    "login_required",
    "osm_required",
    # Config
    "get_auth_config",
    "get_jwt_validator",
    "get_cookie_crypto",
    # Request helpers
    "get_token_from_request",
    "get_current_user",
    "get_osm_connection",
    # Cookie management
    "set_osm_cookie",
    "clear_osm_cookie",
    # User mapping
    "get_mapped_user_id",
    "get_auth_status",
    "create_user_mapping",
    # Admin
    "create_admin_urlpatterns",
    "get_admin_emails",
    "is_admin_user",
    # OSM views
    "osm_login",
    "osm_callback",
    "osm_status",
    "osm_disconnect",
    "osm_urlpatterns",
    # Models
    "HankoUserMapping",
]
