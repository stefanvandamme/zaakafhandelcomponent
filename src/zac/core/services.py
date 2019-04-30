import hashlib
import logging
from typing import Dict, List

from django.core.cache import cache

from zgw.models import Zaak, ZaakType

from zac.config.constants import APITypes
from zac.config.models import Service

logger = logging.getLogger(__name__)


def _get_zaaktypes() -> List[Dict]:
    """
    Read the configured zaaktypes and cache the result.
    """
    KEY = 'zaaktypes'

    result = cache.get(KEY)
    if result:
        logger.debug("Zaaktypes cache hit")
        return result

    result = []

    ztcs = Service.objects.filter(api_type=APITypes.ztc)
    for ztc in ztcs:
        client = ztc.build_client(scopes=['zds.scopes.zaaktypes.lezen'])
        catalogus_uuid = ztc.extra.get('main_catalogus_uuid')
        result += client.list('zaaktype', catalogus_uuid=catalogus_uuid)

    cache.set(KEY, result, 60 * 60)
    return result


def get_zaaktypes() -> List[ZaakType]:
    zaaktypes_raw = _get_zaaktypes()
    return [ZaakType.from_raw(raw) for raw in zaaktypes_raw]


def get_zaken(zaaktypes: List[str] = None) -> list:
    """
    Fetch all zaken from the ZRCs.
    """
    _zaaktypes = get_zaaktypes()

    if zaaktypes is None:
        zaaktypes = [zt.id for zt in get_zaaktypes()]

    zt_key = ','.join(sorted(zaaktypes))
    cache_key = hashlib.md5(f"zaken.{zt_key}".encode('ascii')).hexdigest()

    zaken = cache.get(cache_key)
    if zaken is not None:
        logger.debug("Zaken cache hit")
        return zaken

    claims = {
        'scopes': ['zds.scopes.zaken.lezen'],
        'zaaktypes': [zt.url for zt in _zaaktypes if zt.id in zaaktypes],
    }
    zrcs = Service.objects.filter(api_type=APITypes.zrc)

    zaken = []
    for zrc in zrcs:
        client = zrc.build_client(**claims)
        _zaken = client.list('zaak')['results']
        zaken += [Zaak.from_raw(raw) for raw in _zaken]

    cache.set(cache_key, zaken, 60 * 30)

    return zaken
