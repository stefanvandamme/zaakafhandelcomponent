import operator
from functools import reduce
from typing import List

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool, Nested, Range, Term, Terms
from zgw_consumers.api_models.constants import VertrouwelijkheidsAanduidingen

from .documents import ZaakDocument


def search(
    size=None,
    identificatie=None,
    bronorganisatie=None,
    zaaktypen=None,
    behandelaar=None,
    allowed=(),
    ordering=("-identificatie", "-startdatum", "-registratiedatum"),
) -> List[str]:

    size = size or 10000
    s = ZaakDocument.search()[:size]

    if identificatie:
        s = s.filter(Term(identificatie=identificatie))
    if bronorganisatie:
        s = s.filter(Term(bronorganisatie=bronorganisatie))
    if zaaktypen:
        s = s.filter(Terms(zaaktype=zaaktypen))
    if behandelaar:
        s = s.filter(
            Nested(
                path="rollen",
                query=Bool(
                    filter=[
                        Term(rollen__betrokkene_type="medewerker"),
                        Term(rollen__omschrijving_generiek="behandelaar"),
                        Term(
                            rollen__betrokkene_identificatie__identificatie=behandelaar
                        ),
                    ]
                ),
            )
        )

    # construct query part to display only allowed zaken
    _filters = []
    for filter in allowed:
        combined = Q("match_all")

        if filter["zaaktypen"]:
            combined = combined & Terms(zaaktype=filter["zaaktypen"])

        if filter["max_va"]:
            max_va_order = VertrouwelijkheidsAanduidingen.get_choice(
                filter["max_va"]
            ).order
            combined = combined & Range(va_order={"lte": max_va_order})

        if filter["oo"]:
            combined = combined & Nested(
                path="rollen",
                query=Bool(
                    filter=[
                        Term(rollen__betrokkene_type="organisatorische_eenheid"),
                        Term(
                            rollen__betrokkene_identificatie__identificatie=filter["oo"]
                        ),
                    ]
                ),
            )

        _filters.append(combined)

    if _filters:
        combined_filter = reduce(operator.or_, _filters)
        s = s.filter(combined_filter)

    if ordering:
        s = s.sort(*ordering)

    response = s.execute()
    zaak_urls = [hit.url for hit in response]
    return zaak_urls
