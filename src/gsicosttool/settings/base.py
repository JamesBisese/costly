"""
Django settings for GSI Cost Tool project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import os
from pathlib import Path

from django.contrib import messages
from django.urls import reverse_lazy


DEBUG = False

TEMPLATE_DEBUG = False

"""
    Note for running in dev and on IIS
    for dev, this alias (url prefix) is blank
    for IIS - use production.py settings, which loads base, then production where this is set to IIS's name
    for the app
    
"""

# Build paths inside the project like this: BASE_DIR / "directory"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

# this is for static files not found in an app
# gsicosttool is not an included app, so it needs to be specified directly
# TODO verify if this is true and remove it if it is not.  I see that 'gsicosttool' is included in the apps, and this might be causing the double load from collectstatic
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'gsicosttool', 'static'),
]

# this is where collectstatic will put all the documents it collects
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATIC_URL = '/static/'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'gsicosttool', 'templates'),
            os.path.join(BASE_DIR, 'scenario','templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
            'builtins': [
                'scenario.templatetags.scenario_extras',
            ]
        },
    },
]



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = ''

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'profiles',
    'accounts',
    'gsicosttool',
    'scenario.apps.ScenarioConfig',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.humanize',
    'bootstrap4',
    # 'bootstrap_datepicker_plus',

    'rest_framework',
    'rest_framework_datatables',

    'mathfilters',

    'django_tables2',
    'crispy_forms',
    'easy_thumbnails',
    'django_select2',
    'multiselectfield',
    'widget_tweaks',
    'djmoney',
    # 'django_filters',
    'location_field.apps.DefaultConfig',
    'authtools'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gsicosttool.urls'

WSGI_APPLICATION = 'gsicosttool.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# the database connection is set in the local.env file

DATABASES = {}

# added this for newer Django requirement.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# DATABASES = {
#      # Raises ImproperlyConfigured exception if DATABASE_URL not in
#      # os.environ
#      'default': env.db(),
# }

#TODO 2019-05-31 at 15:11
# DATABASES = {
# 	'default': {
# 		'ENGINE': 'django.db.backends.postgresql',
# 		'NAME': '############',
# 		'USER': '#############',
# 		'PASSWORD': '###############',
# 		'HOST': '127.0.0.1',
# 		'PORT': '5433',
# 		'DATABASE_SCHEMA': 'pubic'
# 	}
# }

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Strict password authentication and validation
# To use this setting, install the Argon2 password hashing algorithm.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

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

# Crispy Form Theme - Bootstrap 3
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# For Bootstrap 3, change error alert to 'danger'

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

# Authentication Settings
AUTH_USER_MODEL = 'authtools.User'

LOGIN_REDIRECT_URL = reverse_lazy("home")

LOGIN_URL = reverse_lazy("accounts:login")

LOGOUT_REDIRECT_URL = reverse_lazy("home")

THUMBNAIL_EXTENSION = 'png'


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
}


# https://github.com/django-money/django-money
CURRENCIES = ('USD',)
CURRENCY_CHOICES = [('USD', 'USD $'), ]

# these variables should be overridden using local.development.env or local.production.env
EMAIL_CONTACT='base@tetratech.com'

HEADER_BANNER_IMAGE_URI='gsicosttool/img/Tetra_Tech_skyline.jpg'

HEADER_LOGO_URI='gsicosttool/img/tetratech-icon-1024.png'

IS_TESTING_INSTANCE='true'

VERSION_INFORMATION='Version 1.018 Updated November 29, 2021'

COPYRIGHT_DISCLAIMER='&copy; City of Raleigh, NC 2021'

SETTINGS_EXPORT = [
    'VERSION_INFORMATION',
    'EMAIL_CONTACT',
    'HEADER_BANNER_IMAGE_URI',
    'HEADER_LOGO_URI',
    'IS_TESTING_INSTANCE',
    'COPYRIGHT_DISCLAIMER',
]

