"""
Django settings for rufilms project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import environ

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('RUFILMS_SECRET_KEY',default='django-insecure-@c#k0hmk0b2*+kl(%91)8r&8r@kosm@c0&$12+*5di=s%$x#-+')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('RUFILMS_DEBUG',default=True)

ALLOWED_HOSTS = env.list('RUFILMS_ALLOWED_HOSTS',default=['*'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # local
    'messenger.apps.MessengerConfig',
    'frontend.apps.FrontendConfig',
    # 3d party
    'rest_framework',
    'corsheaders',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rufilms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rufilms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('RUFILMS_POSTGRES_NAME', default='rufilms'),
        'USER': env('RUFILMS_POSTGRES_USER', default='postgres'),
        'PASSWORD': env('RUFILMS_POSTGRES_PASSWORD', default='postgres'),
        'HOST': env('RUFILMS_POSTGRES_HOST', default='localhost'),
        'PORT': env('RUFILMS_POSTGRES_PORT', default='5432'),
    },
    #'default':{
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / 'db.sqlite3',
    #}
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

import os
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'build'
STATICFILES_DIRS = ( os.path.join('build/static'), )

MEDIA_ROOT=BASE_DIR/'www'/'media'
STATICFILES_FINDERS=[
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

#
FFMPEG_PATH=env('RUFILMS_FFMPEG_PATH', default=r'D:\ffmpeg\bin\ffmpeg')


#

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOWED_ORIGINS = env.list('RUFILMS_CORS_ALLOWED_ORIGINS')

CSRF_TRUSTED_ORIGINS = env.list('RUFILMS_CSRF_TRUSTED_ORIGINS')
