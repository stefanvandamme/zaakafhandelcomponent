from django.http import JsonResponse

from rest_framework import generics, views
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from zac.accounts.api.serializers import CatalogusURLSerializer
from zac.core.permissions import zaken_handle_access
from zac.core.services import get_informatieobjecttypen

from .serializers import ZaakAccessSerializer


class InformatieobjecttypenJSONView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    schema = None

    def get(self, request):
        """Return the informatieobjecttypen for a catalogus"""
        catalogus_url_serializer = CatalogusURLSerializer(
            data={"url": request.GET.get("catalogus")}
        )
        catalogus_url_serializer.is_valid(raise_exception=True)

        informatieobjecttypen = get_informatieobjecttypen(
            catalogus=catalogus_url_serializer.validated_data["url"]
        )
        informatieobjecttypen = sorted(
            informatieobjecttypen, key=lambda iot: iot.omschrijving.lower()
        )

        response_data = {"formData": [], "emptyFormData": []}
        for informatieobjecttype in informatieobjecttypen:
            response_data["emptyFormData"].append(
                {
                    "catalogus": catalogus_url_serializer.validated_data["url"],
                    "omschrijving": informatieobjecttype.omschrijving,
                    "selected": False,
                }
            )
        return JsonResponse(response_data)


class GrantZaakAccessView(generics.CreateAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ZaakAccessSerializer
