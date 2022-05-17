# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += [
    'django_extensions',
]

ALLOWED_HOSTS.append('testserver')

# Django-sendfile:
# https://github.com/moggers87/django-sendfile2
SENDFILE_BACKEND = 'django_sendfile.backends.development'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Cross-Origin Resource Sharing settings for CVAT UI
UI_SCHEME = os.environ.get('UI_SCHEME', 'http')
UI_HOST = os.environ.get('UI_HOST', 'localhost')
UI_PORT = os.environ.get('UI_PORT', 3000)
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [UI_HOST]
UI_URL = '{}://{}'.format(UI_SCHEME, UI_HOST)

if UI_PORT and UI_PORT != '80':
    UI_URL += ':{}'.format(UI_PORT)
# set UI url to redirect to after successful e-mail confirmation
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '{}/auth/email-confirmation'.format(UI_URL)

CORS_ORIGIN_WHITELIST = [UI_URL]
CORS_REPLACE_HTTPS_REFERER = True
IAM_OPA_DATA_URL = 'http://localhost:8181/v1/data'
