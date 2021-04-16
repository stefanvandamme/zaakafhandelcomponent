from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from zac.accounts.api.serializers import UserSerializer
from zac.camunda.api.validators import UserValidator

from ..models import Activity, Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "activity",
            "notes",
            "created",
        )


class ActivitySerializer(serializers.ModelSerializer):
    assignee = UserSerializer(
        read_only=True,
    )
    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = (
            "id",
            "url",
            "zaak",
            "name",
            "remarks",
            "status",
            "assignee",
            "document",
            "created",
            "events",
        )
        extra_kwargs = {
            "url": {
                "view_name": "activities:activity-detail",
            },
        }


class PatchActivitySerializer(ActivitySerializer):
    assignee = serializers.CharField(
        label=_("assignee"),
        help_text=_("User assigned to the activity."),
        required=False,
        validators=(UserValidator(),),
    )

    class Meta(ActivitySerializer.Meta):
        fields = (
            "assignee",
            "document",
            "status",
        )
