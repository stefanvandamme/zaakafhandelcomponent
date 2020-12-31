from typing import Any

from django.core.validators import RegexValidator
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.translation import gettext as _

from rest_framework import serializers
from zgw_consumers.api_models.catalogi import (
    EIGENSCHAP_FORMATEN,
    Eigenschap,
    EigenschapSpecificatie,
    InformatieObjectType,
    ResultaatType,
    StatusType,
    ZaakType,
)
from zgw_consumers.api_models.constants import AardRelatieChoices
from zgw_consumers.api_models.documenten import Document
from zgw_consumers.api_models.zaken import Resultaat, Status, ZaakEigenschap
from zgw_consumers.drf.serializers import APIModelSerializer

from zgw.models.zrc import Zaak

from .utils import (
    CSMultipleChoiceField,
    ValidExpandChoices,
    ValidFieldChoices,
    get_informatieobjecttypen_for_zaak,
)


class InformatieObjectTypeSerializer(serializers.Serializer):
    url = serializers.URLField()
    omschrijving = serializers.CharField()


class AddDocumentSerializer(serializers.Serializer):
    informatieobjecttype = serializers.URLField(required=True)
    zaak = serializers.URLField(required=True)
    file = serializers.FileField(required=True, use_url=False)

    beschrijving = serializers.CharField(required=False)

    def validate(self, data):
        zaak_url = data.get("zaak")
        informatieobjecttype_url = data.get("informatieobjecttype")

        if zaak_url and informatieobjecttype_url:
            informatieobjecttypen = get_informatieobjecttypen_for_zaak(zaak_url)
            present = any(
                iot
                for iot in informatieobjecttypen
                if iot.url == informatieobjecttype_url
            )
            if not present:
                raise serializers.ValidationError(
                    "Invalid informatieobjecttype URL given."
                )

        return data


class AddDocumentResponseSerializer(serializers.Serializer):
    document = serializers.URLField(source="url")


class DocumentInfoSerializer(serializers.Serializer):
    document_type = serializers.CharField(source="informatieobjecttype.omschrijving")
    titel = serializers.CharField()
    vertrouwelijkheidaanduiding = serializers.CharField(
        source="get_vertrouwelijkheidaanduiding_display"
    )
    bestandsgrootte = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    def get_bestandsgrootte(self, obj):
        return filesizeformat(obj.bestandsomvang)

    def get_download_url(self, obj):
        path = reverse(
            "core:download-document",
            kwargs={
                "bronorganisatie": obj.bronorganisatie,
                "identificatie": obj.identificatie,
            },
        )
        return self.context["request"].build_absolute_uri(path)


class ExpandParamSerializer(serializers.Serializer):
    fields = CSMultipleChoiceField(
        choices=ValidExpandChoices.choices,
        required=False,
    )


class ExtraInfoUpSerializer(serializers.Serializer):
    burgerservicenummer = serializers.CharField(
        allow_blank=False,
        required=True,
        max_length=9,
        validators=[
            RegexValidator(
                regex="^[0-9]{9}$",
                message="Een BSN heeft 9 cijfers.",
                code="invalid",
            )
        ],
    )

    doelbinding = serializers.CharField(
        allow_blank=False,
        required=True,
    )

    fields = CSMultipleChoiceField(
        choices=ValidFieldChoices.choices,
        required=True,
        strict=True,
    )


class ExtraInfoSubjectSerializer(serializers.Serializer):
    geboortedatum = serializers.CharField()
    geboorteland = serializers.CharField()
    kinderen = serializers.ListField()
    verblijfplaats = serializers.DictField()
    partners = serializers.ListField()


class AddZaakRelationSerializer(serializers.Serializer):
    relation_zaak = serializers.URLField(required=True)
    aard_relatie = serializers.ChoiceField(required=True, choices=AardRelatieChoices)
    main_zaak = serializers.URLField(required=True)

    def validate(self, data):
        """Check that the main zaak and the relation are not the same"""

        if data["relation_zaak"] == data["main_zaak"]:
            raise serializers.ValidationError(
                _("Zaken kunnen niet met zichzelf gerelateerd worden.")
            )
        return data


class ZaakIdentificatieSerializer(serializers.Serializer):
    identificatie = serializers.CharField(required=True)


class ZaakSerializer(serializers.Serializer):
    identificatie = serializers.CharField(required=True)
    bronorganisatie = serializers.CharField(required=True)
    url = serializers.URLField(required=True)


class ZaakTypeSerializer(APIModelSerializer):
    class Meta:
        model = ZaakType
        fields = (
            "url",
            "catalogus",
            "omschrijving",
            "versiedatum",
        )


class ZaakDetailSerializer(APIModelSerializer):
    zaaktype = ZaakTypeSerializer()
    deadline = serializers.DateField(read_only=True)
    deadline_progress = serializers.FloatField(
        label=_("Progress towards deadline"),
        read_only=True,
        help_text=_(
            "Value between 0-100, representing a percentage. 100 means the deadline "
            "has been reached or exceeded."
        ),
    )

    class Meta:
        model = Zaak
        fields = (
            "url",
            "identificatie",
            "bronorganisatie",
            "zaaktype",
            "omschrijving",
            "toelichting",
            "registratiedatum",
            "startdatum",
            "einddatum",
            "einddatum_gepland",
            "uiterlijke_einddatum_afdoening",
            "vertrouwelijkheidaanduiding",
            "deadline",
            "deadline_progress",
        )


class StatusTypeSerializer(APIModelSerializer):
    class Meta:
        model = StatusType
        fields = (
            "url",
            "omschrijving",
            "omschrijving_generiek",
            "statustekst",
            "volgnummer",
            "is_eindstatus",
        )


class ZaakStatusSerializer(APIModelSerializer):
    statustype = StatusTypeSerializer()

    class Meta:
        model = Status
        fields = (
            "url",
            "datum_status_gezet",
            "statustoelichting",
            "statustype",
        )


class ResultaatTypeSerializer(APIModelSerializer):
    class Meta:
        model = ResultaatType
        fields = ("url", "omschrijving")


class ResultaatSerializer(APIModelSerializer):
    resultaattype = ResultaatTypeSerializer()

    class Meta:
        model = Resultaat
        fields = ("url", "resultaattype", "toelichting")


class EigenschapSpecificatieSerializer(APIModelSerializer):
    waardenverzameling = serializers.ListField(child=serializers.CharField())
    formaat = serializers.ChoiceField(
        choices=list(EIGENSCHAP_FORMATEN.keys()),
        label=_("data type"),
    )

    class Meta:
        model = EigenschapSpecificatie
        fields = (
            "groep",
            "formaat",
            "lengte",
            "kardinaliteit",
            "waardenverzameling",
        )


class EigenschapSerializer(APIModelSerializer):
    specificatie = EigenschapSpecificatieSerializer(label=_("property definition"))

    class Meta:
        model = Eigenschap
        fields = (
            "url",
            "naam",
            "toelichting",
            "specificatie",
        )


class ZaakEigenschapSerializer(APIModelSerializer):
    value = serializers.SerializerMethodField(
        label=_("property value"),
        help_text=_("The backing data type depens on the eigenschap format."),
    )
    eigenschap = EigenschapSerializer()

    class Meta:
        model = ZaakEigenschap
        fields = (
            "url",
            "eigenschap",
            "value",
        )

    def get_value(self, obj) -> Any:
        return obj.get_waarde()


class DocumentTypeSerializer(APIModelSerializer):
    class Meta:
        model = InformatieObjectType
        fields = (
            "url",
            "omschrijving",
        )


class ZaakDocumentSerializer(APIModelSerializer):
    download_url = serializers.SerializerMethodField(
        label=_("ZAC download URL"),
        help_text=_(
            "The download URL for the end user. Will serve the file as attachment."
        ),
    )
    vertrouwelijkheidaanduiding = serializers.CharField(
        source="get_vertrouwelijkheidaanduiding_display"
    )
    informatieobjecttype = DocumentTypeSerializer()

    class Meta:
        model = Document
        fields = (
            "url",
            "auteur",
            "identificatie",
            "beschrijving",
            "bestandsnaam",
            "locked",
            "informatieobjecttype",
            "titel",
            "vertrouwelijkheidaanduiding",
            "bestandsomvang",
            "download_url",
        )
        extra_kwargs = {
            "bestandsomvang": {
                "help_text": _("File size in bytes"),
            }
        }

    def get_download_url(self, obj) -> str:
        path = reverse(
            "core:download-document",
            kwargs={
                "bronorganisatie": obj.bronorganisatie,
                "identificatie": obj.identificatie,
            },
        )
        return self.context["request"].build_absolute_uri(path)


class RelatedZaakDetailSerializer(ZaakDetailSerializer):
    status = ZaakStatusSerializer()
    resultaat = ResultaatSerializer()

    class Meta(ZaakDetailSerializer.Meta):
        fields = ZaakDetailSerializer.Meta.fields + ("status", "resultaat")


class RelatedZaakSerializer(serializers.Serializer):
    aard_relatie = serializers.CharField()
    zaak = RelatedZaakDetailSerializer()
