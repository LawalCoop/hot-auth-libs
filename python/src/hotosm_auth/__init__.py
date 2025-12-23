"""
hotosm-auth: HOTOSM SSO Authentication Library

This library provides authentication for HOTOSM applications using:
- Hanko v2.1.0 for base SSO (Google, GitHub, Email/Password)
- OpenStreetMap OAuth 2.0 for OSM authorization

Key Features:
- JWT validation with JWKS
- httpOnly cookie-based session management
- Optional/required OSM integration
- FastAPI and Django support
- Legacy user mapping for gradual migration
"""

__version__ = "0.1.4"

from hotosm_auth.models import HankoUser, OSMConnection, OSMScope
from hotosm_auth.config import AuthConfig

# SQLAlchemy model - only import if sqlalchemy is available (FastAPI projects)
# Django projects use hotosm_auth_django.models instead
try:
    from hotosm_auth.db_models import HankoUserMapping
    __all__ = [
        "HankoUser",
        "OSMConnection",
        "OSMScope",
        "AuthConfig",
        "HankoUserMapping",
        "__version__",
    ]
except ImportError:
    # SQLAlchemy not installed (e.g., Django projects)
    __all__ = [
        "HankoUser",
        "OSMConnection",
        "OSMScope",
        "AuthConfig",
        "__version__",
    ]

# Admin functionality - only import if FastAPI is available
try:
    from hotosm_auth.integrations.fastapi_admin import AdminUser, require_admin
    from hotosm_auth.integrations.fastapi_admin_routes import create_admin_mappings_router
    from hotosm_auth.integrations.fastapi_admin_routes_psycopg import create_admin_mappings_router_psycopg
    from hotosm_auth.schemas.admin import (
        MappingResponse,
        MappingListResponse,
        MappingCreate,
        MappingUpdate,
    )
    __all__.extend([
        "AdminUser",
        "require_admin",
        "create_admin_mappings_router",
        "create_admin_mappings_router_psycopg",
        "MappingResponse",
        "MappingListResponse",
        "MappingCreate",
        "MappingUpdate",
    ])
except ImportError:
    # FastAPI not installed
    pass

# Django admin functionality - only import if Django is available
try:
    from hotosm_auth.integrations.django_admin_routes import create_admin_urlpatterns
    __all__.append("create_admin_urlpatterns")
except ImportError:
    # Django not installed
    pass
