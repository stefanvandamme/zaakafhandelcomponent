from django.urls import reverse

import jwt
import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service

from zac.accounts.tests.factories import UserFactory
from zac.core.tests.utils import ClearCachesMixin
from zac.tests.utils import mock_service_oas_get

from ..models import KownslConfig

# can't use generate_oas_component because Kownsl API schema doesn't have components
REVIEW_REQUEST = {
    "created": "2020-12-16T14:15:22Z",
    "id": "45638aa6-e177-46cc-b580-43339795d5b5",
    "for_zaak": "https://zaken.nl/api/v1/zaak/123",
    "review_type": "advice",
    "documents": [],
    "frontend_url": f"https://kownsl.nl/45638aa6-e177-46cc-b580-43339795d5b5",
    "num_advices": 1,
    "num_approvals": 0,
    "num_assigned_users": 1,
    "toelichting": "Longing for the past but dreading the future",
    "user_deadlines": {
        "some-user": "2020-12-20",
    },
    "requester": "other-user",
    "metadata": {},
    "zaak_documents": [],
    "reviews": [],
}


@requests_mock.Mocker()
class ViewTests(ClearCachesMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.service = Service.objects.create(
            label="Kownsl",
            api_type=APITypes.orc,
            api_root="https://kownsl.nl",
            auth_type=AuthTypes.zgw,
            client_id="zac",
            secret="supersecret",
            oas="https://kownsl.nl/api/v1",
            user_id="zac",
        )

        config = KownslConfig.get_solo()
        config.service = cls.service
        config.save()

        cls.user = UserFactory.create(username="some-user")

    def _mock_oas_get(self, m):
        mock_service_oas_get(
            m, self.service.api_root, "kownsl", oas_url=self.service.oas
        )

    def test_create_approval(self, m):
        self._mock_oas_get(m)
        m.get(
            "https://kownsl.nl/api/v1/review-requests/45638aa6-e177-46cc-b580-43339795d5b5",
            json=REVIEW_REQUEST,
        )
        m.post(
            "https://kownsl.nl/api/v1/review-requests/45638aa6-e177-46cc-b580-43339795d5b5/approvals",
            json={"ok": "yarp"},
            status_code=201,
        )
        # log in - we need to see the user ID in the auth from ZAC to Kownsl
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "kownsl:reviewrequest-approval",
            kwargs={"request_uuid": "45638aa6-e177-46cc-b580-43339795d5b5"},
        )
        body = {"dummy": "data"}

        response = self.client.post(url, body)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"ok": "yarp"})

        auth_header = m.last_request.headers["Authorization"]
        self.assertTrue(auth_header.startswith("Bearer "))
        token = auth_header.split(" ")[1]
        claims = jwt.decode(token, verify=False)
        self.assertEqual(claims["client_id"], "zac")
        self.assertEqual(claims["user_id"], "some-user")
