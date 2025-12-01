"""
hotosm_auth_django: Django app for HOTOSM authentication.

Add to INSTALLED_APPS to use HankoUserMapping model with migrations.

Usage:
    # settings.py
    INSTALLED_APPS = [
        ...
        'hotosm_auth_django',
        ...
    ]

    # Then run migrations
    python manage.py migrate hotosm_auth_django
"""

default_app_config = 'hotosm_auth_django.apps.HotosmAuthDjangoConfig'
