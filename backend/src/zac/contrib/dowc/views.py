from typing import Any, NoReturn, Optional

from django.http import HttpResponse

from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from zac.core.services import find_document

from .api import get_doc_info, patch_and_destroy_doc
from .permissions import CanOpenDocuments
from .serializers import DowcResponseSerializer


def _cast(value: Optional[Any], type_: type) -> Any:
    if value is None:
        return value
    return type_(value)


class OpenDowcView(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated & CanOpenDocuments,)
    http_method_names = ["post"]
    document = None
    serializer_class = DowcResponseSerializer

    def get_object(self) -> NoReturn:
        bronorganisatie = self.kwargs["bronorganisatie"]
        identificatie = self.kwargs["identificatie"]
        purpose = self.kwargs["purpose"]

        if not self.document:
            versie = _cast(self.request.GET.get("versie", None), int)
            self.document = find_document(bronorganisatie, identificatie, versie=versie)

    def post(self, request, bronorganisatie, identificatie, purpose):
        self.get_object()
        drc_url = self.document.url
        dowc_response, status_code = get_doc_info(request.user, drc_url, purpose)
        serializer = self.serializer_class(dowc_response)
        return Response(serializer.data, status=status_code)


class DeleteDowcView(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated & CanOpenDocuments,)
    http_method_names = ["delete"]

    def delete(self, request, doc_request_uuid):
        response = patch_and_destroy_doc(request.user, doc_request_uuid)
        return response
