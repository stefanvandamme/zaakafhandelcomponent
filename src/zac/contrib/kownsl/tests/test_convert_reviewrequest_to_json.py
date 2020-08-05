import datetime
import uuid

from django.test import TestCase
from django.utils import timezone

from zgw_consumers.api_models.base import factory

from zac.contrib.kownsl.data import Advice, Approval, ReviewRequest
from zac.utils.api_models import convert_model_to_json


class ConvertToJsonTests(TestCase):
    def test_review_requests_for_advice(self):
        review_request_data = {
            "id": "45638aa6-e177-46cc-b580-43339795d5b5",
            "for_zaak": "https://zaken.nl/api/v1/zaak/123",
            "review_type": "advice",
            "documents": [],
            "frontend_url": f"https://kownsl.nl/45638aa6-e177-46cc-b580-43339795d5b5",
            "num_advices": 1,
            "num_approvals": 0,
            "num_assigned_users": 1,
        }
        advice_data = {
            "created": "2020-06-17T10:21:16Z",
            "author": {"username": "foo", "first_name": "", "last_name": "",},
            "advice": "dummy",
            "documents": [],
        }
        review_request = factory(ReviewRequest, review_request_data)
        advice = factory(Advice, advice_data)
        review_request.advices = [advice]
        review_requests = [review_request]

        result = convert_model_to_json(review_requests)

        self.assertEqual(
            result,
            [
                {
                    "id": uuid.UUID("45638aa6-e177-46cc-b580-43339795d5b5"),
                    "for_zaak": "https://zaken.nl/api/v1/zaak/123",
                    "review_type": "advice",
                    "documents": [],
                    "frontend_url": "https://kownsl.nl/45638aa6-e177-46cc-b580-43339795d5b5",
                    "num_advices": 1,
                    "num_approvals": 0,
                    "num_assigned_users": 1,
                    "advices": [
                        {
                            "created": timezone.make_aware(
                                datetime.datetime(2020, 6, 17, 10, 21, 16)
                            ),
                            "author": {
                                "username": "foo",
                                "first_name": "",
                                "last_name": "",
                            },
                            "advice": "dummy",
                            "documents": [],
                        }
                    ],
                }
            ],
        )

    def test_review_request_for_approval(self):
        review_request_data = {
            "id": "45638aa6-e177-46cc-b580-43339795d5b5",
            "for_zaak": "https://zaken.nl/api/v1/zaak/123",
            "review_type": "advice",
            "documents": [],
            "frontend_url": f"https://kownsl.nl/45638aa6-e177-46cc-b580-43339795d5b5",
            "num_advices": 0,
            "num_approvals": 1,
            "num_assigned_users": 1,
        }
        approval_data = {
            "created": "2020-06-17T10:21:16Z",
            "author": {"username": "foo", "first_name": "", "last_name": "",},
            "approved": True,
        }
        review_request = factory(ReviewRequest, review_request_data)
        approval = factory(Approval, approval_data)
        review_request.approvals = [approval]
        review_requests = [review_request]

        result = convert_model_to_json(review_requests)

        self.assertEqual(
            result,
            [
                {
                    "id": uuid.UUID("45638aa6-e177-46cc-b580-43339795d5b5"),
                    "for_zaak": "https://zaken.nl/api/v1/zaak/123",
                    "review_type": "advice",
                    "documents": [],
                    "frontend_url": "https://kownsl.nl/45638aa6-e177-46cc-b580-43339795d5b5",
                    "num_advices": 0,
                    "num_approvals": 1,
                    "num_assigned_users": 1,
                    "approvals": [
                        {
                            "created": timezone.make_aware(
                                datetime.datetime(2020, 6, 17, 10, 21, 16)
                            ),
                            "author": {
                                "username": "foo",
                                "first_name": "",
                                "last_name": "",
                            },
                            "approved": True,
                        }
                    ],
                }
            ],
        )
