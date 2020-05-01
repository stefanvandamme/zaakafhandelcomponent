from django.urls import reverse

import requests_mock
from django_camunda.models import CamundaConfig
from django_webtest import WebTest
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service

from zac.accounts.models import User

from .utils import mock_service_oas_get
from .zrc import get_zaak_response
from .ztc import get_roltype_response, get_zaaktype_response

ZTC_URL = "https://some.ztc.nl/api/v1/"
ZRC_URL = "https://some.zrc.nl/api/v1/"
CATALOGUS = f"{ZTC_URL}catalogussen/49ca9066-463b-4be0-b380-3f0cc7cf06bd"
ZAAKTYPE = f"{ZTC_URL}zaaktypen/e135a764-bcc2-44bf-af0e-c7c4935da06a"
ROLTYPE = f"{ZTC_URL}roltypen/e135a764-bcc2-44bf-af0e-c7c4935da06a"
ZAAK = f"{ZRC_URL}zaken/4f8b4811-5d7e-4e9b-8201-b35f5101f891"
CAMUNDA_ROOT = "https://camunda.example.com/"
CAMUNDA_API = "engine-rest/"
CAMUNDA = f"{CAMUNDA_ROOT}{CAMUNDA_API}"
TASK_ID = "5a461dc8-891e-11ea-ae32-0e13a3f6559d"


class TaskClaimTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create_superuser(
            username="demo",
            email="demo@demo.com",
            password="demo",
            first_name="first",
            last_name="last",
        )

        Service.objects.create(
            api_root=ZTC_URL,
            api_type=APITypes.ztc,
            label="some ztc",
            auth_type=AuthTypes.no_auth,
        )
        Service.objects.create(
            api_root=ZRC_URL,
            api_type=APITypes.zrc,
            label="some zrc",
            auth_type=AuthTypes.no_auth,
        )
        camunda_config = CamundaConfig.get_solo()
        camunda_config.root_url = CAMUNDA_ROOT
        camunda_config.rest_api_path = CAMUNDA_API
        camunda_config.save()

    def setUp(self):
        super().setUp()

        # because of axes middleware we can't do simple login without request object
        self.client.post(
            reverse("admin:login"),
            {"username": "demo", "password": "demo"},
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="test-browser",
        )

    @requests_mock.Mocker()
    def test_claim_task(self, m):
        # mock ztc
        mock_service_oas_get(m, "ztc", ZTC_URL)
        m.get(ZAAKTYPE, json=get_zaaktype_response(CATALOGUS, ZAAKTYPE))
        roltypen_url = (
            f"{ZTC_URL}roltypen?zaaktype={ZAAKTYPE}&&omschrijvingGeneriek=behandelaar"
        )
        roltypen_data = {
            "count": 1,
            "next": None,
            "results": [get_roltype_response(ROLTYPE, ZAAKTYPE)],
        }
        m.get(roltypen_url, json=roltypen_data)
        # mock zrc
        mock_service_oas_get(m, "zrc", ZRC_URL)
        m.get(ZAAK, json=get_zaak_response(ZAAK, ZAAKTYPE))
        rollen_url = f"{ZRC_URL}rollen"
        m.post(rollen_url, status_code=201)
        # mock camunda
        task_claim_url = f"{CAMUNDA}task/{TASK_ID}/claim"
        m.post(task_claim_url, json={})

        url = reverse("core:claim-task")
        next_url = reverse("index")

        response = self.client.post(
            url, {"zaak": ZAAK, "task_id": TASK_ID}, HTTP_REFERER=next_url
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

        # check rol body
        self.assertEqual(m.last_request.url, rollen_url)

        rol_data = m.last_request.json()
        self.assertEqual(
            rol_data,
            {
                "zaak": ZAAK,
                "betrokkeneType": "medewerker",
                "roltype": ROLTYPE,
                "roltoelichting": "task claiming",
                "betrokkeneIdentificatie": {
                    "identificatie": self.user.username,
                    "achternaam": self.user.last_name,
                    "voorletters": self.user.first_name[0],
                },
            },
        )
