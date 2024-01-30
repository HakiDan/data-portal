# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config, Csv
from unipath import Path
from django.contrib.messages import constants as messages
from datetime import timedelta

MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

# load production server from .env
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
ALLOWED_IPS = config('ALLOWED_IPS', cast=Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'apps.home',  # Enable the inner home (home)
    'apps.masterlist',
    'apps.history',
    'apps.upload',
    'apps.datacleaning',
    'apps.datacatalogue',
    'apps.inventory',
    'apps.validation',
    'apps.faq',
    'crispy_forms',
    'background_task',
    'admin_honeypot',
]

MIDDLEWARE = [
    # 'core.middleware.InternalUseOnlyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.auto_logout',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates
SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = True

# Zabbix settings

ZABBIX_SERVER = config('ZABBIX_SERVER')
ZABBIX_PORT = config('ZABBIX_PORT')

# Superset settings

SUPERSET_PASSWORD = config('SUPERSET_PASSWORD')

# DAG settings

DAG_URL = config('DAG_URL')
DAG_USER = config('DAG_USER')
DAG_PASS = config('DAG_PASS')

AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=120),
    'SESSION_TIME': timedelta(minutes=120),
    'MESSAGE': 'Sesi anda telah tamat tempoh. Sila log masuk semula untuk sambungan sesi.',
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]



WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':config('DB_ENGINE'),
        'NAME':config('DB_NAME'),
        'USER':config('DB_USER'),
        'PASSWORD':config('DB_PASSWORD'),
        'HOST':config('DB_HOST'),
        'PORT':config('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'core.validators.CustomUserAttributeSimilarityValidator',
    },
    {
        'NAME': 'core.validators.CustomMinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'core.validators.CustomCommonPasswordValidator',
    },
    {
        'NAME': 'core.validators.CustomNumericPasswordValidator',
    },
    {
        'NAME': 'core.validators.CustomComplexPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kuala_Lumpur'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static'),
)

#############################################################
#############################################################

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MAINPATH = config('MAINPATH')
PRIVATE_STORAGE_ROOT = config('PRIVATE_STORAGE_ROOT')
PRIVATE_STORAGE_ROOT_MASTERLIST = config('PRIVATE_STORAGE_ROOT_MASTERLIST')
PRIVATE_STORAGE_ROOT_STANDARD_COL = config('PRIVATE_STORAGE_ROOT_STANDARD_COL')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_formatter': {
            'format': '{asctime} - {levelname} - {message}',
            'style': "{",
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': MAINPATH + '/action.log',
            'formatter': 'main_formatter',
        },
    },
    'loggers': {
        'main': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}