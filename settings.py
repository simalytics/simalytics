# Django settings for the Simalytics project.
import os
import logging
import dj_database_url

logging.basicConfig (
	level = logging.INFO,
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(__file__)))

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3', 
#        'NAME': 'simalytics.db',
#    }
#}

DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static/'),
)
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r&!!=y+^jz#87_7eac2w+@puu(cc_clo+5cv1!e%m+5x253bbr'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'breadcrumbs.middleware.BreadcrumbsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'breadcrumbs.middleware.FlatpageFallbackMiddleware',
    'visitor.middleware.VisitorMiddleware'
)

ROOT_URLCONF = "urls" 

TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'templates/'),)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'south',
    'django.contrib.admin',

    #3rd party apps
    'registration',
    'crispy_forms',
    'social_auth',
    'tinymce',
    'visitor',

    # simalytics applications:
    #'simalytics.api',
    #'simalytics.content_profiles'
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleBackend',
    'enhanced_accounts.backends.EmailAuthBackend',
)
LOGIN_REDIRECT_URL = '/'

FACEBOOK_APP_ID              = '123640527811139'
FACEBOOK_API_SECRET          = 'b92913be91d7e17fe1f437edafc82aa4'

EMAIL_HOST='smtp1.bethere.co.uk'
EMAIL_PORT=25
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL='michaelc@simalytics.com'

# Registration related settings:
# This is the number of days users will have to activate their accounts after registering.
ACCOUNT_ACTIVATION_DAYS = 5

COOKIE_DOMAIN = None # .domain.com
COOKIE_MAX_AGE = 31536000

# Displaing:
PROFILES_PER_PAGE = 25

BREADCRUMBS_AUTO_HOME = True

TINYMCE_JS_URL = STATIC_URL + 'js/tiny_mce/tiny_mce.js'

TINYMCE_DEFAULT_CONFIG = {
    'theme_advanced_buttons1' : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
    'theme_advanced_buttons2' : "bullist,numlist,link,unlink,anchor,code,",
    'mode' : "textareas",
    'theme' : "advanced",
    'plugins' : "inlinepopups",

    }


