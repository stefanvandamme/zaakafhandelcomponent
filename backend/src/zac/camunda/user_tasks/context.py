import functools
import warnings
from abc import ABC
from typing import Dict, Optional, Tuple, Type

from rest_framework import serializers

from zac.api.polymorphism import SerializerCls

from ..data import Task
from .drf import usertask_context_serializer

REGISTRY: Dict[str, Tuple[callable, SerializerCls]] = {}


class Context(ABC):
    """
    Base class for user-task contexts.

    The user task context subclass is determined by the form_key.
    """

    pass


def get_context(task: Task) -> Optional[Context]:
    """
    Retrieve the task-specific context for a given user task.

    Consult the registry mapping form keys to specific context-determination functions.
    If no callback exists for a given form key, ``None`` is returned.

    Third party or non-core apps can add form keys to the registry by importing the
    ``REGISTRY`` constant and registering their form key with the appropriote callback
    callable.
    """
    (callback, *rest) = REGISTRY.get(task.form_key)
    if callback is None:
        return None
    return callback(task)


class DuplicateFormKeyWarning(Warning):
    pass


def register(form_key: str, serializer_cls: Type[serializers.Serializer]):
    """
    Register the form key with the given callback and serializer class.
    """

    def decorator(func: callable):
        if form_key in REGISTRY:
            warnings.warn(
                f"Overwriting existing form key '{form_key}' in registry.",
                DuplicateFormKeyWarning,
            )

        REGISTRY[form_key] = (func, serializer_cls)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

    return decorator


EmptySerializer = usertask_context_serializer(serializers.JSONField)


@register("", EmptySerializer)
@register("zac:documentSelectie", EmptySerializer)
@register("zac:gebruikerSelectie", EmptySerializer)
def noop(task) -> None:
    return None
