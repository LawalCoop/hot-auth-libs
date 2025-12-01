"""
FastAPI integration for hotosm-auth.

Provides:
- Dependency injection for HankoUser and OSMConnection
- Route decorators for protecting endpoints
- Response utilities for setting cookies

## Quick Start

1. Create a `.env` file with minimal configuration:

```bash
# Required
HANKO_API_URL=https://login.hotosm.org
COOKIE_SECRET=your-secret-key-min-32-bytes-long

# Optional - for OSM integration
OSM_CLIENT_ID=your-osm-client-id
OSM_CLIENT_SECRET=your-osm-client-secret

# ✨ Everything else is auto-detected!
# - COOKIE_DOMAIN: from HANKO_API_URL → ".hotosm.org"
# - COOKIE_SECURE: from HANKO_API_URL scheme → true (https)
# - OSM_REDIRECT_URI: auto-generated → "{HANKO_API_URL}/auth/osm/callback"
```

2. Initialize auth in your FastAPI app:

```python
from fastapi import FastAPI
from hotosm_auth import AuthConfig
from hotosm_auth.integrations.fastapi import init_auth

app = FastAPI()

# Auto-load from .env
config = AuthConfig.from_env()
init_auth(config)
```

3. Use dependency injection to protect routes:

```python
from hotosm_auth.integrations.fastapi import CurrentUser, OSMConnectionOptional

@app.get("/protected")
async def protected_route(
    user: CurrentUser,
    osm: OSMConnectionOptional,
):
    return {
        "user": user.email,
        "osm": osm.osm_username if osm else None,
    }
```

## Dependencies Available

- `CurrentUser` - Requires authentication, returns HankoUser
- `CurrentUserOptional` - Optional authentication, returns Optional[HankoUser]
- `OSMConnectionDep` - Optional OSM connection, returns Optional[OSMConnection]
- `OSMConnectionRequired` - Requires OSM connection, returns OSMConnection

## Example: Public Route (Optional Auth)

```python
from hotosm_auth.integrations.fastapi import CurrentUserOptional

@app.get("/public")
async def public_route(user: CurrentUserOptional):
    if user:
        return {"message": f"Hello {user.email}"}
    return {"message": "Hello anonymous"}
```

## Example: OSM Required Route

```python
from hotosm_auth.integrations.fastapi import CurrentUser, OSMConnectionRequired

@app.get("/osm-only")
async def osm_route(
    user: CurrentUser,
    osm: OSMConnectionRequired,
):
    return {"osm_username": osm.osm_username}
```

## Logging

Control log verbosity with the LOG_LEVEL environment variable:

```bash
LOG_LEVEL=DEBUG   # Show all debug messages
LOG_LEVEL=INFO    # Show info and above
LOG_LEVEL=WARNING # Show warnings and errors only (default)
LOG_LEVEL=ERROR   # Show errors only
```
"""

from typing import Optional, Annotated
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from hotosm_auth.config import AuthConfig
from hotosm_auth.models import HankoUser, OSMConnection
from hotosm_auth.jwt_validator import JWTValidator
from hotosm_auth.crypto import CookieCrypto
from hotosm_auth.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    TokenInvalidError,
    CookieDecryptionError,
)
from hotosm_auth.logger import get_logger, log_auth_event

logger = get_logger(__name__)


# Global instances (set by init_auth)
_config: Optional[AuthConfig] = None
_jwt_validator: Optional[JWTValidator] = None
_cookie_crypto: Optional[CookieCrypto] = None

# Security scheme for Swagger UI
bearer_scheme = HTTPBearer(auto_error=False)


def init_auth(config: AuthConfig) -> None:
    """Initialize authentication for FastAPI app.

    Call this once at app startup:

        app = FastAPI()
        config = AuthConfig(...)
        init_auth(config)

    Args:
        config: Authentication configuration
    """
    global _config, _jwt_validator, _cookie_crypto

    _config = config
    _jwt_validator = JWTValidator(config)
    _cookie_crypto = CookieCrypto(config.cookie_secret)


def get_config() -> AuthConfig:
    """Get authentication configuration (dependency)."""
    if _config is None:
        raise RuntimeError("Auth not initialized. Call init_auth() at startup.")
    return _config


def get_jwt_validator() -> JWTValidator:
    """Get JWT validator (dependency)."""
    if _jwt_validator is None:
        raise RuntimeError("Auth not initialized. Call init_auth() at startup.")
    return _jwt_validator


def get_cookie_crypto() -> CookieCrypto:
    """Get cookie crypto (dependency)."""
    if _cookie_crypto is None:
        raise RuntimeError("Auth not initialized. Call init_auth() at startup.")
    return _cookie_crypto


async def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[str]:
    """Extract JWT token from cookie or Authorization header.

    Priority:
    1. Authorization header (Bearer token)
    2. hanko cookie

    Args:
        request: FastAPI request
        credentials: Bearer token from Authorization header

    Returns:
        str: JWT token or None
    """
    # Try Authorization header first
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials

    # Try cookie
    token = request.cookies.get("hanko")
    return token


async def get_current_user(
    request: Request,
    validator: JWTValidator = Depends(get_jwt_validator),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> HankoUser:
    """Get currently authenticated user (dependency).

    Validates JWT token and returns HankoUser.
    Raises HTTPException if authentication fails.

    Usage:
        @app.get("/protected")
        async def protected_route(user: HankoUser = Depends(get_current_user)):
            return {"user_id": user.id, "email": user.email}

    Args:
        request: FastAPI request
        validator: JWT validator
        credentials: Bearer token

    Returns:
        HankoUser: Authenticated user

    Raises:
        HTTPException: 401 if authentication fails
    """
    token = await get_token_from_request(request, credentials)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await validator.validate_token(token)
        return user
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (TokenInvalidError, AuthenticationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    request: Request,
    validator: JWTValidator = Depends(get_jwt_validator),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[HankoUser]:
    """Get current user if authenticated, None otherwise.

    Like get_current_user but doesn't raise exception if not authenticated.

    Usage:
        @app.get("/optional-auth")
        async def route(user: Optional[HankoUser] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user.email}"}
            return {"message": "Hello anonymous"}

    Args:
        request: FastAPI request
        validator: JWT validator
        credentials: Bearer token

    Returns:
        HankoUser or None
    """
    token = await get_token_from_request(request, credentials)

    if not token:
        return None

    try:
        user = await validator.validate_token(token)
        return user
    except (TokenExpiredError, TokenInvalidError, AuthenticationError):
        return None


async def get_osm_connection(
    request: Request,
    crypto: CookieCrypto = Depends(get_cookie_crypto),
) -> Optional[OSMConnection]:
    """Get OSM connection from encrypted cookie (dependency).

    Returns None if no OSM connection cookie found or decryption fails.

    Usage:
        @app.get("/osm-protected")
        async def route(
            user: HankoUser = Depends(get_current_user),
            osm: OSMConnection = Depends(require_osm_connection),
        ):
            return {"osm_username": osm.osm_username}

    Args:
        request: FastAPI request
        crypto: Cookie crypto

    Returns:
        OSMConnection or None
    """
    encrypted = request.cookies.get("osm_connection")

    print(f"🔍 Looking for OSM connection cookie: found={encrypted is not None}")
    print(f"🔍 All cookies present: {list(request.cookies.keys())}")
    if encrypted:
        print(f"🔍 Cookie value (first 50 chars): {encrypted[:50]}...")

    if not encrypted:
        print("❌ No OSM cookie found, returning None")
        return None

    try:
        print("🔓 Attempting to decrypt OSM cookie...")
        osm = crypto.decrypt_osm_connection(encrypted)
        print(f"✅ OSM connection decrypted successfully: {osm.osm_username}")
        return osm
    except CookieDecryptionError as e:
        print(f"❌ OSM cookie decryption failed: {e}")
        return None


async def require_osm_connection(
    osm: Optional[OSMConnection] = Depends(get_osm_connection),
) -> OSMConnection:
    """Require OSM connection (dependency).

    Like get_osm_connection but raises HTTPException if not connected.

    Usage:
        @app.get("/osm-required")
        async def route(osm: OSMConnection = Depends(require_osm_connection)):
            return {"osm_username": osm.osm_username}

    Args:
        osm: OSM connection from cookie

    Returns:
        OSMConnection

    Raises:
        HTTPException: 403 if OSM not connected
    """
    if not osm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OSM connection required",
        )
    return osm


def set_osm_cookie(
    response: Response,
    osm_connection: OSMConnection,
    config: AuthConfig,
    crypto: CookieCrypto,
) -> None:
    """Set encrypted OSM connection cookie on response.

    Usage:
        @app.get("/auth/osm/callback")
        async def osm_callback(
            response: Response,
            config: AuthConfig = Depends(get_config),
            crypto: CookieCrypto = Depends(get_cookie_crypto),
        ):
            # ... OSM OAuth flow ...
            osm_conn = OSMConnection(...)
            set_osm_cookie(response, osm_conn, config, crypto)
            return {"success": True}

    Args:
        response: FastAPI response
        osm_connection: OSM connection data to encrypt
        config: Auth configuration
        crypto: Cookie crypto
    """
    encrypted = crypto.encrypt_osm_connection(osm_connection)

    # Calculate max_age from expires_at
    max_age = None
    if osm_connection.expires_at:
        delta = osm_connection.expires_at - datetime.utcnow()
        max_age = int(delta.total_seconds())

    logger.debug(
        f"Setting OSM cookie: domain={config.cookie_domain}, "
        f"secure={config.cookie_secure}, samesite={config.cookie_samesite}"
    )

    response.set_cookie(
        key="osm_connection",
        value=encrypted,
        httponly=True,
        secure=config.cookie_secure,
        samesite=config.cookie_samesite,
        domain=config.cookie_domain,
        max_age=max_age,
        path="/",
    )


def clear_osm_cookie(
    response: Response,
    config: AuthConfig,
) -> None:
    """Clear OSM connection cookie from response.

    Tries multiple combinations of cookie attributes to ensure deletion
    regardless of how the cookie was originally set.

    Usage:
        @app.post("/auth/osm/disconnect")
        async def disconnect_osm(
            response: Response,
            config: AuthConfig = Depends(get_config),
        ):
            clear_osm_cookie(response, config)
            return {"success": True}

    Args:
        response: FastAPI response
        config: Auth configuration
    """
    # Try all combinations to ensure we delete the cookie regardless of how it was set
    # Browsers require exact attribute match to delete a cookie

    for secure in [True, False]:
        for samesite in ["lax", "strict", "none"]:
            # With domain
            if config.cookie_domain:
                response.set_cookie(
                    key="osm_connection",
                    value="",
                    httponly=True,
                    secure=secure,
                    samesite=samesite,
                    domain=config.cookie_domain,
                    max_age=0,
                    path="/",
                )

            # Without domain
            response.set_cookie(
                key="osm_connection",
                value="",
                httponly=True,
                secure=secure,
                samesite=samesite,
                max_age=0,
                path="/",
            )


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[HankoUser, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[HankoUser], Depends(get_current_user_optional)]
OSMConnectionDep = Annotated[Optional[OSMConnection], Depends(get_osm_connection)]
OSMConnectionRequired = Annotated[OSMConnection, Depends(require_osm_connection)]


# ===================================================================
# User Mapping Helpers
# ===================================================================
# These helpers allow apps with existing user systems to map Hanko
# user IDs to their existing user IDs.
#
# Example: Drone-TM has users with String IDs. When migrating to Hanko,
# we don't want to change all foreign keys. Instead, we create a mapping
# table that links hanko_user_id → drone_tm_user_id.
#
# See hotosm_auth.db_models.HankoUserMapping for the reference model.
# ===================================================================


async def get_mapped_user_id(
    hanko_user: HankoUser,
    db_conn,  # psycopg Connection or AsyncConnection
    app_name: str = "default",
    auto_create: bool = True,
    email_lookup_fn=None,  # Optional: async (conn, email) -> Optional[user_id]
    user_creator_fn=None,  # Optional: async (conn, hanko_user) -> user_id
    user_id_generator=None,  # Optional: func() -> str to generate new IDs
) -> str:
    """Get application-specific user ID for a Hanko user.

    This function looks up the mapping table to find the app-specific user ID
    corresponding to a Hanko user. If no mapping exists and auto_create=True,
    it attempts to link with existing users via email or creates a new user.

    Usage (with email-based linking):
        from hotosm_auth.integrations.fastapi import get_mapped_user_id, CurrentUser
        from app.database import get_db

        # Define lookup and creation functions
        async def lookup_by_email(conn, email: str) -> Optional[str]:
            user = await MyUser.get_by_email(conn, email)
            return user.id if user else None

        async def create_new_user(conn, hanko_user: HankoUser) -> str:
            new_user = await MyUser.create(conn, email=hanko_user.email)
            return new_user.id

        @app.get("/me")
        async def get_me(
            hanko_user: CurrentUser,
            db: Connection = Depends(get_db),
        ):
            # Get or create app user ID, linking by email if user exists
            user_id = await get_mapped_user_id(
                hanko_user=hanko_user,
                db_conn=db,
                app_name="drone-tm",
                auto_create=True,
                email_lookup_fn=lookup_by_email,
                user_creator_fn=create_new_user,
            )
            return {"user_id": user_id}

    Args:
        hanko_user: Authenticated Hanko user
        db_conn: psycopg Connection or AsyncConnection
        app_name: Application identifier (useful for multi-app deployments)
        auto_create: If True, create mapping if it doesn't exist
        email_lookup_fn: Optional async function (conn, email) -> Optional[user_id]
                        to search for existing users by email
        user_creator_fn: Optional async function (conn, hanko_user) -> user_id
                        to create new users in the app
        user_id_generator: Optional function to generate new user IDs (fallback)
                          If None and no creator_fn, uses hanko_user.id

    Returns:
        str: Application-specific user ID

    Raises:
        HTTPException: 403 if mapping doesn't exist and auto_create=False
    """
    # Look up existing mapping
    async with db_conn.cursor() as cur:
        await cur.execute(
            """
            SELECT app_user_id
            FROM hanko_user_mappings
            WHERE hanko_user_id = %s AND app_name = %s
            """,
            (hanko_user.id, app_name),
        )
        row = await cur.fetchone()

        if row:
            app_user_id = row[0]
            logger.debug(f"Found mapping: {hanko_user.id} → {app_user_id}")
            log_auth_event(
                "MAPPING_FOUND",
                app_name,
                hanko_user.id,
                email=hanko_user.email,
                app_user_id=app_user_id,
            )
            return app_user_id

        # No mapping found
        if not auto_create:
            logger.warning(f"No mapping found for Hanko user {hanko_user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User not authorized for {app_name}",
            )

        # Try to link with existing user by email
        new_user_id = None
        if email_lookup_fn:
            logger.debug(f"Searching for existing user with email: {hanko_user.email}")
            existing_user_id = await email_lookup_fn(db_conn, hanko_user.email)
            if existing_user_id:
                logger.info(f"Found existing user by email: {hanko_user.email} → {existing_user_id}")
                new_user_id = existing_user_id

        # If no existing user, try to create new user
        if not new_user_id and user_creator_fn:
            logger.debug(f"Creating new user for Hanko user: {hanko_user.id}")
            new_user_id = await user_creator_fn(db_conn, hanko_user)
            logger.info(f"Created new user: {new_user_id}")

        # Fallback: use user_id_generator or hanko_user.id
        if not new_user_id:
            if user_id_generator:
                new_user_id = user_id_generator()
            else:
                # Default: use Hanko ID as app user ID
                new_user_id = hanko_user.id

        # Create mapping
        await cur.execute(
            """
            INSERT INTO hanko_user_mappings (hanko_user_id, app_user_id, app_name, created_at)
            VALUES (%s, %s, %s, NOW())
            """,
            (hanko_user.id, new_user_id, app_name),
        )

        logger.info(f"Created mapping: {hanko_user.id} → {new_user_id} ({app_name})")
        log_auth_event(
            "MAPPING_CREATED",
            app_name,
            hanko_user.id,
            email=hanko_user.email,
            app_user_id=new_user_id,
        )
        return new_user_id


async def create_user_mapping(
    hanko_user_id: str,
    app_user_id: str,
    db_conn,  # psycopg Connection or AsyncConnection
    app_name: str = "default",
) -> None:
    """Manually create a user mapping.

    Useful for data migration when adding Hanko to an existing app.

    Usage:
        # Migration script
        from hotosm_auth.integrations.fastapi import create_user_mapping

        # For each existing user:
        for user in existing_users:
            # If user already has Hanko account:
            if user.hanko_id:
                await create_user_mapping(
                    hanko_user_id=user.hanko_id,
                    app_user_id=user.id,
                    db_conn=db,
                    app_name="drone-tm",
                )

    Args:
        hanko_user_id: Hanko user UUID
        app_user_id: Application-specific user ID
        db_conn: psycopg Connection or AsyncConnection
        app_name: Application identifier

    Raises:
        Exception: If mapping already exists or database error
    """
    async with db_conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO hanko_user_mappings (hanko_user_id, app_user_id, app_name, created_at)
            VALUES (%s, %s, %s, NOW())
            """,
            (hanko_user_id, app_user_id, app_name),
        )

    logger.info(f"Manually created mapping: {hanko_user_id} → {app_user_id} ({app_name})")
    log_auth_event(
        "MAPPING_CREATED",
        app_name,
        hanko_user_id,
        app_user_id=app_user_id,
        source="manual",
    )
