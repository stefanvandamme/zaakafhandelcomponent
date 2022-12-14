from django_filters import rest_framework as filters
from django_filters.widgets import QueryArrayWidget
from zac.utils.filters import ApiFilterSet

from rest_framework import serializers
from zac.accounts.models import User

class StringInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class UserFilter(filters.FilterSet):
    include = StringInFilter(
        field_name="username",
        widget=QueryArrayWidget,
        help_text="Deprecated - please use 'include_username' instead.",
    )
    exclude = StringInFilter(
        field_name="username",
        widget=QueryArrayWidget,
        exclude=True,
        help_text="Deprecated - please use 'exclude_username' instead.",
    )
    include_username = StringInFilter(field_name="username", widget=QueryArrayWidget)
    exclude_username = StringInFilter(
        field_name="username", widget=QueryArrayWidget, exclude=True
    )
    include_email = StringInFilter(field_name="email", widget=QueryArrayWidget)
    exclude_email = StringInFilter(
        field_name="email", widget=QueryArrayWidget, exclude=True
    )
    include_groups = StringInFilter(field_name="groups__name", widget=QueryArrayWidget)


class PermissionFilter(ApiFilterSet):
    availableFor = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all(),
        required=False,
        help_text=_("The username of the user for which unassigned permissions are requested.")
    )
