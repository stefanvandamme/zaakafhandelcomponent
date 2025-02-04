from typing import List

from zac.activities.constants import ActivityStatuses
from zac.activities.models import Activity
from zac.camunda.data import Task
from zac.camunda.processes import get_top_level_process_instances
from zac.camunda.user_tasks import register
from zac.contrib.dowc.api import check_document_status
from zac.contrib.kownsl.api import get_review_requests
from zac.contrib.objects.checklists.data import ChecklistQuestion
from zac.contrib.objects.services import fetch_checklist, fetch_checklisttype
from zac.core.camunda.utils import get_process_zaak_url
from zac.core.services import (
    fetch_zaaktype,
    get_documenten,
    get_resultaattypen,
    get_zaak,
    get_zaaktype,
)
from zgw.models.zrc import Zaak

from .serializers import (
    ZetResultaatContext,
    ZetResultaatContextSerializer,
    ZetResultaatTaskSerializer,
)


def get_unanswered_checklist_questions_for_zaak(
    zaak: Zaak,
) -> List[ChecklistQuestion]:
    checklist = fetch_checklist(zaak)
    if checklist:
        answered_questions = [
            answer.question for answer in checklist.answers if answer.answer
        ]
    else:
        answered_questions = []

    zaaktype = (
        get_zaaktype(zaak.zaaktype) if isinstance(zaak.zaaktype, str) else zaak.zaaktype
    )
    checklisttype = fetch_checklisttype(zaaktype)
    if checklisttype:
        return [
            question
            for question in checklisttype.questions
            if question.question not in answered_questions
        ]

    return []


@register(
    "zac:zetResultaat",
    ZetResultaatContextSerializer,
    ZetResultaatTaskSerializer,
)
def get_context(task: Task) -> ZetResultaatContext:
    zaak_url = get_process_zaak_url(task)
    activities = (
        Activity.objects.prefetch_related("events").filter(
            zaak=zaak_url, status=ActivityStatuses.on_going
        )
        or None
    )
    zaak = get_zaak(zaak_url=zaak_url)
    checklist_questions = get_unanswered_checklist_questions_for_zaak(zaak) or None
    process_instances = get_top_level_process_instances(zaak_url)
    tasks = [task for pi in process_instances for task in pi.tasks] or None
    review_requests = [
        rr for rr in get_review_requests(zaak) if rr.completed < rr.num_assigned_users
    ] or None
    documenten, gone = get_documenten(zaak)
    open_documenten = check_document_status([doc.url for doc in documenten])
    zaaktype = fetch_zaaktype(zaak.zaaktype)

    all_result_types = get_resultaattypen(zaaktype)
    chosen_result_types = []
    if result_type_choices := task.get_variable("resultaatTypeKeuzes", default=None):
        for result in all_result_types:
            if result.omschrijving in result_type_choices:
                chosen_result_types.append(result)

    return ZetResultaatContext(
        activities=activities,
        checklist_questions=checklist_questions,
        tasks=tasks,
        review_requests=review_requests,
        result_types=chosen_result_types or all_result_types,
        open_documenten=open_documenten,
    )
