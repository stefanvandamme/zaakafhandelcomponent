from unittest.mock import patch

from django.conf import settings
from django.urls import reverse_lazy

import requests_mock
from django_webtest import TransactionWebTest
from zgw_consumers.api_models.constants import VertrouwelijkheidsAanduidingen
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from zac.accounts.tests.factories import PermissionSetFactory, UserFactory
from zac.tests.utils import generate_oas_component, mock_service_oas_get

from ..permissions import zaken_inzien
from .utils import ClearCachesMixin

CATALOGI_ROOT = "https://api.catalogi.nl/api/v1/"
ZAKEN_ROOT = "https://api.zaken.nl/api/v1/"

BRONORGANISATIE = "123456782"
IDENTIFICATIE = "ZAAK-001"


@requests_mock.Mocker()
class ZaakDetailTests(ClearCachesMixin, TransactionWebTest):

    url = reverse_lazy(
        "core:zaak-detail",
        kwargs={"bronorganisatie": BRONORGANISATIE, "identificatie": IDENTIFICATIE,},
    )

    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()

        Service.objects.create(api_type=APITypes.ztc, api_root=CATALOGI_ROOT)
        Service.objects.create(api_type=APITypes.zrc, api_root=ZAKEN_ROOT)

    def test_login_required(self, m):
        response = self.app.get(self.url)

        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_user_auth_no_perms(self, m):
        response = self.app.get(self.url, user=self.user, status=403)

        self.assertEqual(response.status_code, 403)

    def test_user_has_perm_but_not_for_zaaktype(self, m):
        mock_service_oas_get(m, ZAKEN_ROOT, "zrc")
        mock_service_oas_get(m, CATALOGI_ROOT, "ztc")
        zaak = generate_oas_component(
            "zrc",
            "schemas/Zaak",
            bronorganisatie=BRONORGANISATIE,
            identificatie=IDENTIFICATIE,
            zaaktype=f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
        )
        zaaktype = generate_oas_component(
            "ztc",
            "schemas/ZaakType",
            url=f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            identificatie="ZT1",
        )
        m.get(
            f"{ZAKEN_ROOT}zaken?bronorganisatie={BRONORGANISATIE}&identificatie={IDENTIFICATIE}",
            json={"count": 1, "previous": None, "next": None, "results": [zaak],},
        )
        m.get(
            f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            json=zaaktype,
        )

        # gives them access to the page, but no zaaktypen specified -> nothing visible
        PermissionSetFactory.create(
            permissions=[zaken_inzien.name],
            for_user=self.user,
            catalogus="",
            zaaktype_identificaties=[],
            max_va=VertrouwelijkheidsAanduidingen.beperkt_openbaar,
        )

        response = self.app.get(self.url, user=self.user, status=403)

        self.assertEqual(response.status_code, 403)

    def test_user_has_perm_but_not_for_va(self, m):
        mock_service_oas_get(m, ZAKEN_ROOT, "zrc")
        mock_service_oas_get(m, CATALOGI_ROOT, "ztc")
        zaak = generate_oas_component(
            "zrc",
            "schemas/Zaak",
            bronorganisatie=BRONORGANISATIE,
            identificatie=IDENTIFICATIE,
            url=f"{ZAKEN_ROOT}zaken/85a59d62-2ac7-432e-9ca7-4f6c9bde4d10",
            zaaktype=f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            vertrouwelijkheindaanduiding=VertrouwelijkheidsAanduidingen.beperkt_openbaar,
        )
        zaaktype = generate_oas_component(
            "ztc",
            "schemas/ZaakType",
            url=f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            catalogus=f"{CATALOGI_ROOT}catalogi/2fa14cce-12d0-4f57-8d5d-ecbdfbe06a5e",
            identificatie="ZT1",
        )
        m.get(
            f"{ZAKEN_ROOT}zaken?bronorganisatie={BRONORGANISATIE}&identificatie={IDENTIFICATIE}",
            json={"count": 1, "previous": None, "next": None, "results": [zaak],},
        )
        m.get(
            f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            json=zaaktype,
        )

        # gives them access to the page, but no zaaktypen specified -> nothing visible
        PermissionSetFactory.create(
            permissions=[zaken_inzien.name],
            for_user=self.user,
            catalogus=zaaktype["catalogus"],
            zaaktype_identificaties=["ZT1"],
            max_va=VertrouwelijkheidsAanduidingen.openbaar,
        )

        response = self.app.get(self.url, user=self.user, status=403)

        self.assertEqual(response.status_code, 403)

    def test_user_has_perm(self, m):
        mock_service_oas_get(m, ZAKEN_ROOT, "zrc")
        mock_service_oas_get(m, CATALOGI_ROOT, "ztc")
        zaak = generate_oas_component(
            "zrc",
            "schemas/Zaak",
            url=f"{ZAKEN_ROOT}zaken/fa988e62-c1fe-4496-8c0f-29b85373e4df",
            bronorganisatie=BRONORGANISATIE,
            identificatie=IDENTIFICATIE,
            zaaktype=f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            vertrouwelijkheidaanduiding=VertrouwelijkheidsAanduidingen.beperkt_openbaar,
        )
        zaaktype = generate_oas_component(
            "ztc",
            "schemas/ZaakType",
            url=f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            catalogus=f"{CATALOGI_ROOT}catalogi/2fa14cce-12d0-4f57-8d5d-ecbdfbe06a5e",
            identificatie="ZT1",
        )
        m.get(
            f"{ZAKEN_ROOT}zaken?bronorganisatie={BRONORGANISATIE}&identificatie={IDENTIFICATIE}",
            json={"count": 1, "previous": None, "next": None, "results": [zaak],},
        )
        m.get(
            f"{CATALOGI_ROOT}zaaktypen/17e08a91-67ff-401d-aae1-69b1beeeff06",
            json=zaaktype,
        )
        m.get(
            f"{CATALOGI_ROOT}zaaktypen?catalogus={zaaktype['catalogus']}",
            json={"count": 1, "previous": None, "next": None, "results": [zaaktype]},
        )

        # gives them access to the page, but no zaaktypen specified -> nothing visible
        PermissionSetFactory.create(
            permissions=[zaken_inzien.name],
            for_user=self.user,
            catalogus=zaaktype["catalogus"],
            zaaktype_identificaties=["ZT1"],
            max_va=VertrouwelijkheidsAanduidingen.zaakvertrouwelijk,
        )

        # mock out all the other calls - we're testing auth here
        with patch("zac.core.views.zaken.get_statussen", return_value=[]), patch(
            "zac.core.views.zaken.get_documenten", return_value=([], [])
        ), patch("zac.core.views.zaken.get_zaak_eigenschappen", return_value=[]), patch(
            "zac.core.views.zaken.get_related_zaken", return_value=[]
        ), patch(
            "zac.core.views.zaken.get_resultaat", return_value=None
        ):
            response = self.app.get(self.url, user=self.user)

        self.assertEqual(response.status_code, 200)
