from typing import Any, Dict, List, Optional

from zds_client import ClientError
from zds_client.client import get_operation_url
from zgw_consumers.api_models.base import factory
from zgw_consumers.api_models.zaken import Zaak
from zgw_consumers.client import ZGWClient

from .data import AdviceCollection, ReviewRequest
from .models import KownslConfig


def get_client() -> ZGWClient:
    config = KownslConfig.get_solo()
    assert config.service, "A service must be configured first"
    return config.service.build_client()


def create_review_request(zaak_url: str, review_type: str = "advice") -> Dict[str, Any]:
    client = get_client()
    data = {
        "for_zaak": zaak_url,
        "review_type": review_type,
    }
    resp = client.create("reviewrequest", data=data)
    return resp


def retrieve_advice_collection(zaak: Zaak) -> Optional[AdviceCollection]:
    """
    Retrieve the advice collection for a single advice case.

    :param zaak_url: URL of the case to check. This particular case is supposed to be
      the case that is used to collect the advices, not the case that requests for
      advices.
    :return: an advice-collection object
    """
    client = get_client()
    operation_id = "advicecollection_retrieve"
    url = get_operation_url(client.schema, operation_id, base_url=client.base_url)
    try:
        result = client.request(url, operation_id, params={"objectUrl": zaak.url})
    except ClientError as exc:
        if exc.__context__.response.status_code == 404:
            return None
        raise
    return factory(AdviceCollection, result)


def get_review_requests(zaak: Zaak) -> List[ReviewRequest]:
    client = get_client()
    result = client.list("reviewrequest", query_params={"for_zaak": zaak.url})
    review_requests = factory(ReviewRequest, result)

    # fix relation reference
    for review_request in review_requests:
        review_request.for_zaak = zaak
    return review_requests
