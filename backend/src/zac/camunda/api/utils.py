import logging
from typing import Dict, Optional, Union

from django.conf import settings

from django_camunda.client import get_client
from django_camunda.interface import Variable

from zac.camunda.process_instances import delete_process_instance
from zac.camunda.processes import get_process_definitions, get_process_instances
from zac.core.models import CoreConfig
from zgw.models.zrc import Zaak

logger = logging.getLogger(__name__)


def get_bptl_app_id_variable() -> Dict[str, str]:
    """
    Get the name and value of the bptl app ID variable for BPTL.
    """
    core_config = CoreConfig.get_solo()
    return {
        "bptlAppId": core_config.app_id,
    }


def start_process(
    process_key: Optional[str] = None,
    process_id: Optional[str] = None,
    business_key: Optional[str] = None,
    variables: Dict[str, Union[Variable, dict]] = None,
) -> Dict[str, str]:
    logger.debug(
        "Received process start: process_key=%s, process_id=%s", process_key, process_id
    )
    if not (process_key or process_id):
        raise ValueError("Provide a process key or process ID")

    client = get_client()
    variables = variables or {}

    _variables = {
        key: var.serialize() if isinstance(var, Variable) else var
        for key, var in variables.items()
    }

    if process_id:
        endpoint = f"process-definition/{process_id}/start"
    else:
        endpoint = f"process-definition/key/{process_key}/start"

    body = {
        "businessKey": business_key or "",
        "withVariablesInReturn": False,
        "variables": _variables,
    }

    response = client.post(endpoint, json=body)

    self_rel = next((link for link in response["links"] if link["rel"] == "self"))
    instance_url = self_rel["href"]

    logger.info("Started process instance %s", response["id"])

    return {"instance_id": response["id"], "instance_url": instance_url}


def delete_zaak_creation_process(zaak: Zaak) -> None:
    # First check if there is still a CREATE_ZAAK_PROCESS_DEFINITION_KEY process that needs to be cleaned up.
    process_instances = get_process_instances(zaak.url)
    if process_instances:
        pdefinition_to_pinstance_map = {
            pi.definition_id: pid
            for pid, pi in process_instances.items()
            if pi.definition_id
        }
        process_definitions = get_process_definitions(
            pdefinition_to_pinstance_map.keys()
        )

        p_def_id_to_key_map = {}
        for pdef in process_definitions:
            if pdef.key in p_def_id_to_key_map:
                p_def_id_to_key_map[pdef.key].append(pdef.id)
            else:
                p_def_id_to_key_map[pdef.key] = [pdef.id]

        if pdef_id := p_def_id_to_key_map.get(
            settings.CREATE_ZAAK_PROCESS_DEFINITION_KEY
        ):
            if pdef_id in pdefinition_to_pinstance_map.keys():
                delete_pid = pdefinition_to_pinstance_map[pdef_id]
                delete_process_instance(delete_pid)
