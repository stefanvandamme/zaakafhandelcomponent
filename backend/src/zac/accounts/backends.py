from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password

from zac.accounts.models import BlueprintPermission, UserAtomicPermission


class UserModelEmailBackend(ModelBackend):
    """
    Authentication backend for login with email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = get_user_model().objects.get(email__iexact=username, is_active=True)
            if check_password(password, user.password):
                return user
        except get_user_model().DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None


# Deprecated
# this class is used only to support legacy SSR views
# All DRF views should use zac.api.permissions.DefinitionBasePermission and its subclasses
class PermissionsBackend:
    def authenticate(self, request):
        return None

    def has_perm(self, user_obj, perm: str, obj=None) -> bool:
        if not user_obj.is_active:
            return False

        blueprint_permissions = BlueprintPermission.objects.for_user(
            user_obj, actual=True
        ).filter(role__permissions__contains=[perm])

        user_atomic_permissions = (
            UserAtomicPermission.objects.select_related("atomic_permission")
            .filter(user=user_obj, atomic_permission__permission=perm)
            .actual()
        )

        # similar to DefinitionBasePermission.has_permission
        if not obj:
            return blueprint_permissions.exists() or user_atomic_permissions.exists()

        # similar to DefinitionBasePermission.has_object_permission
        if user_atomic_permissions.filter(
            atomic_permission__object_url=obj.url
        ).exists():
            return True

        for permission in blueprint_permissions:
            if permission.has_access(obj, user=user_obj):
                return True

        return False
