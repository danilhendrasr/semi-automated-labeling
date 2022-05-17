# Copyright (C) 2021 Intel Corporation
#
# SPDX-License-Identifier: MIT

from django.urls import path, re_path
from django.conf import settings
from django.urls.conf import include
from rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView)
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView
from allauth.account import app_settings as allauth_settings

from cvat.apps.iam.views import SigningView, RegisterViewEx

urlpatterns = [
    path('login', LoginView.as_view(), name='rest_login'),
    path('logout', LogoutView.as_view(), name='rest_logout'),
    path('signing', SigningView.as_view(), name='signing')
]

if settings.IAM_TYPE == 'BASIC':
    urlpatterns += [
        path('register', RegisterViewEx.as_view(), name='rest_register'),
        path('password/reset', PasswordResetView.as_view(),
            name='rest_password_reset'),
        path('password/reset/confirm', PasswordResetConfirmView.as_view(),
            name='rest_password_reset_confirm'),
        path('password/change', PasswordChangeView.as_view(),
            name='rest_password_change'),
    ]
    if allauth_settings.EMAIL_VERIFICATION != \
       allauth_settings.EmailVerificationMethod.NONE:
        urlpatterns += [
            re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
                name='account_confirm_email'),
            path('register/account-email-verification-sent', EmailVerificationSentView.as_view(),
                name='account_email_verification_sent'),
        ]

urlpatterns = [path('auth/', include(urlpatterns))]