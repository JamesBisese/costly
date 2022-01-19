import environ
import logging.config
import os
import sys

from .base import *   # First import base.py and then override settings with this content

# Use 12factor inspired environment variables from a file

env = environ.Env()

# Create a local.env file in the settings directory
# But ideally this env file should be outside the git repo
env_file = os.path.join(Path(__file__).resolve().parent, 'local.development.env')

if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # env.bool('DEBUG', default=True)

# region -- toggle to allow DEV and PROD on insdev1 for testing of these systems
# if running in pycharm or with runserver, you need to clear this
IIS_APP_ALIAS = env('IIS_APP_ALIAS')

# reset these 2 URIs for IIS alias to work
iis_app_alias = ''
if len(IIS_APP_ALIAS) > 0:
    iis_app_alias = IIS_APP_ALIAS + '/'

MEDIA_URL = '/' + iis_app_alias + 'media/'
STATIC_URL = '/' + iis_app_alias + 'static/'

# end region

# TODO figure what this does. it looks wrong, like it should use DEBUG, not false
TEMPLATES[0]['OPTIONS'].update({'debug': True})

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

# Turn off debug while imported by Celery with a workaround
# See http://stackoverflow.com/a/4806384
if "celery" in sys.argv[0]:
    DEBUG = False

# unsetting this variable allows the testing account passwords to pass, although they are refused for 'production'
AUTH_PASSWORD_VALIDATORS = []

# Show emails to console in DEBUG mode
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Show thumbnail generation errors
THUMBNAIL_DEBUG = True

# Allow internal IPs for debugging
INTERNAL_IPS = [
    '127.0.0.1',
    '0.0.0.1',
]

DATABASES = {
     # Raises ImproperlyConfigured exception if DATABASE_URL not in
     # os.environ
     'default': env.db(),
}

# if the installation is using SQL Server then it needs to add the 'driver' in the OPTIONS
try:
    DATABASES['default']['OPTIONS'] = {'driver': env.str('DATABASE_default_OPTIONS_driver')}
except:
    pass


# Log everything to the logs directory at the top
# LOGFILE_ROOT = BASE_DIR.parent / 'logs'
LOGFILE_ROOT = os.path.join(BASE_DIR.parent, 'logs', 'development')

if not os.path.exists(LOGFILE_ROOT):
    try:
        os.makedirs(LOGFILE_ROOT)
    except:
        raise IOError('Log folder does not exist and could not be created: %s' % LOGFILE_ROOT)

# Reset logging
# (see http://www.caktusgroup.com/blog/2015/01/27/Django-Logging-Configuration-logging_config-default-settings-logger/)

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGFILE_ROOT, 'django.log'),
            'formatter': 'verbose'
        },
        'proj_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGFILE_ROOT, 'project.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django_log_file'],
            'propagate': True,
            'level': 'WARNING',
        },
        'project': {
            'handlers': ['proj_log_file'],
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'developer': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(LOGGING)

# these are loaded if they are found in the env file.  else the default is used from base

try:
    EMAIL_CONTACT = env.str('EMAIL_CONTACT')
except:
    pass

try:
    HEADER_BANNER_IMAGE_URI = env.str('HEADER_BANNER_IMAGE_URI')
except:
    pass

try:
    HEADER_LOGO_URI = env.str('HEADER_LOGO_URI')
except:
    pass

try:
    IS_TESTING_INSTANCE = env.str('IS_TESTING_INSTANCE')
except:
    pass

try:
    COPYRIGHT_DISCLAIMER = env.str('COPYRIGHT_DISCLAIMER')
except:
    pass

try:
    VERSION_INFORMATION = env.str('VERSION_INFORMATION')
except:
    pass

# email related stuff

EMAIL_BACKEND = env.str('EMAIL_BACKEND')
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_PORT = env.str('EMAIL_PORT')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
