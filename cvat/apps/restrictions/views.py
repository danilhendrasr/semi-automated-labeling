# Copyright (C) 2020 Intel Corporation
#
# SPDX-License-Identifier: MIT

from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from drf_spectacular.utils import OpenApiResponse, extend_schema


from cvat.apps.restrictions.serializers import UserAgreementSerializer

@extend_schema(tags=['restrictions'])
class RestrictionsViewSet(viewsets.ViewSet):
    serializer_class = None
    permission_classes = [AllowAny]
    authentication_classes = []
    iam_organization_field = None

    # To get nice documentation about ServerViewSet actions it is necessary
    # to implement the method. By default, ViewSet doesn't provide it.
    def get_serializer(self, *args, **kwargs):
        pass

    @staticmethod
    @extend_schema(summary='Method provides user agreements that the user must accept to register',
                  responses={'200': UserAgreementSerializer})
    @action(detail=False, methods=['GET'], serializer_class=UserAgreementSerializer, url_path='user-agreements')
    def user_agreements(request):
        user_agreements = settings.RESTRICTIONS['user_agreements']
        serializer = UserAgreementSerializer(data=user_agreements, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)

    @staticmethod
    @extend_schema(summary='Method provides CVAT terms of use',
                responses={'200': OpenApiResponse(description='CVAT terms of use')})
    @action(detail=False, methods=['GET'], renderer_classes=(TemplateHTMLRenderer,),
        url_path='terms-of-use')
    def terms_of_use(request):
        return Response(template_name='restrictions/terms_of_use.html')
