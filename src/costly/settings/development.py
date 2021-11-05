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
DEBUG = True

# this is used to map the URLS when app is installed on IIS using an alias
IIS_APP_ALIAS = r''

#TODO figure what this does. it looks wrong, like it should use DEBUG, not false
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

# Django Debug Toolbar
# INSTALLED_APPS += (
#     'debug_toolbar',)

# Additional middleware introduced by debug toolbar
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

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
            'filename': os.path.join(LOGFILE_ROOT,'project.log'),
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
            'level': 'DEBUG',
        },
        'project': {
            'handlers': ['proj_log_file'],
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
    HEADER_LOGO_URI = env.str('HEADER_LOGO_URI')
except:
    pass

