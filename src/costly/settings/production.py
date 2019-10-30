# In production set the environment variable like this:
#    DJANGO_SETTINGS_MODULE=costly.settings.production

# First import base.py and then override settings with this content
import environ
import logging.config

from .base import *

# Use 12factor inspired environment variables from a file

env = environ.Env()

# Create a local.env file in the settings directory
# But ideally this env file should be outside the git repo
env_file = os.path.join(Path(__file__).resolve().parent, 'local.production.env')

if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# For security and performance reasons, DEBUG is turned off
DEBUG = False

# this is used to map the URLS when app is installed on IIS using an alias
IIS_APP_ALIAS = r'costly/'

# reset these 2 URIs for IIS alias to work
MEDIA_URL = '/' + IIS_APP_ALIAS + 'media/'
STATIC_URL = '/' + IIS_APP_ALIAS + 'static/'

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

# if DEBUG == False, the django application will only run on hosts that are in the ALLOWED_HOSTS list
ALLOWED_HOSTS = [x.split('|') for x in env.list('ALLOWED_HOSTS')]

DATABASES = {
     # Raises ImproperlyConfigured exception if DATABASE_URL not in
     # os.environ
     'default': env.db(),
}

TIME_ZONE = env('TIME_ZONE')

# Cache the templates in memory for speed-up
loaders = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})


# Log everything to the logs directory at the top
LOGFILE_ROOT = os.path.join(BASE_DIR.parent, 'logs', 'production')

if not os.path.exists(LOGFILE_ROOT):
    try:
        os.makedirs(LOGFILE_ROOT)
    except:
        raise IOError('Log folder does not exist and could not be created: %s' % LOGFILE_ROOT)

# Reset logging
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
        'project': {
            'handlers': ['proj_log_file'],
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(LOGGING)
