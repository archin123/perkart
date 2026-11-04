"""
Django settings for perkcart project.
PerkCart - Corporate Employee Shopping Platform.
"""

import os
from pathlib import Path

# Load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-du4bs^!7p6u15@o*+$wpzi#d4do)+4^r)p@zm&2zat%cw0s4_!'
)

# SECURITY WARNING: don't run with debug turned on in production!
# On Vercel, default to False to show custom branded error pages (404, 500)
if os.getenv('VERCEL'):
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
else:
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '*').split(',') if h.strip()]
if '.vercel.app' not in ALLOWED_HOSTS and '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('.vercel.app')

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
]
csrf_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_env:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in csrf_env.split(',') if origin.strip()])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # PerkCart Custom Applications
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'cart.apps.CartConfig',
    'faq.apps.FaqConfig',
    'troubleshooting.apps.TroubleshootingConfig',
    'assistant.apps.AssistantConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]
try:
    import whitenoise
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass

MIDDLEWARE.extend([
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'troubleshooting.middleware.AppErrorLoggingMiddleware',
])

ROOT_URLCONF = 'perkcart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_perkcart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'perkcart.wsgi.application'

# Database
# Default: SQLite3 for convenient local college development.
# Supports PostgreSQL in production if DATABASE_URL environment variable is provided.
DATABASE_URL = os.getenv('DATABASE_URL', '')
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('Database_url') or os.getenv('database_url') or ''
if DATABASE_URL and (DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://')):
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.parse(
                DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
                ssl_require=True
            )
        }
    except ImportError:
        import urllib.parse
        url = urllib.parse.urlparse(DATABASE_URL)
        db_name = url.path[1:]
        db_options = {}
        if '?' in db_name:
            db_name, query_string = db_name.split('?', 1)
            params = urllib.parse.parse_qs(query_string)
            if 'sslmode' in params:
                db_options['sslmode'] = params['sslmode'][0]

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': urllib.parse.unquote(url.username or ''),
                'PASSWORD': urllib.parse.unquote(url.password or ''),
                'HOST': url.hostname,
                'PORT': str(url.port or 5432),
                'OPTIONS': db_options,
            }
        }
elif DATABASE_URL and (DATABASE_URL.startswith('mongodb://') or DATABASE_URL.startswith('mongodb+srv://')):
    # MongoDB configuration using MongoEngine (PyMongo)
    try:
        import mongoengine
        mongoengine.connect(
            db=os.getenv('MONGODB_NAME', 'perkcart'),
            host=DATABASE_URL,
        )
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
    # Fallback SQLite path: /tmp/db.sqlite3 on Vercel (writable), BASE_DIR / db.sqlite3 locally
    default_db_path = Path('/tmp') / 'db.sqlite3' if os.getenv('VERCEL') else BASE_DIR / 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': default_db_path,
        }
    }
else:
    # Fallback SQLite path: /tmp/db.sqlite3 on Vercel (writable), BASE_DIR / db.sqlite3 locally
    default_db_path = Path('/tmp') / 'db.sqlite3' if os.getenv('VERCEL') else BASE_DIR / 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': default_db_path,
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
try:
    import whitenoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
except ImportError:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# AI Assistant Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('API_Key') or os.getenv('API_KEY') or ''
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Production Security Headers (Active when DEBUG is False)
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
