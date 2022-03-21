from django.contrib.auth.models import Group
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as django_filter
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from zac.core.api.pagination import BffPagination
from zac.utils.mixins import PatchModelMixin, UpdateModelMixin

from ..constants import AccessRequestResult
from ..email import send_email_to_requester
from ..models import (
    AccessRequest,
    AuthorizationProfile,
    Role,
    User,
    UserAtomicPermission,
    UserAuthorizationProfile,
)
from .filters import UserFilter
from .permissions import CanCreateOrHandleAccessRequest, CanGrantAccess, ManageGroup
from .serializers import (
    AccessRequestDetailSerializer,
    AtomicPermissionSerializer,
    AuthProfileSerializer,
    CreateAccessRequestSerializer,
    GrantPermissionSerializer,
    GroupSerializer,
    HandleAccessRequestSerializer,
    ManageGroupSerializer,
    ReadUserAuthorizationProfileSerializer,
    RoleSerializer,
    UserAuthorizationProfileSerializer,
    UserSerializer,
)


@extend_schema_view(
    list=extend_schema(summary=_("List user accounts.")),
    retrieve=extend_schema(summary=_("Retrieve user account.")),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.prefetch_related("groups").all().order_by("username")
    serializer_class = UserSerializer
    pagination_class = BffPagination
    filter_backends = (
        filters.SearchFilter,
        django_filter.DjangoFilterBackend,
    )
    search_fields = ["username", "first_name", "last_name", "email"]
    filterset_class = UserFilter

    @extend_schema(summary=_("Retrieve current logged in user."))
    @action(detail=False)
    def me(self, request, *args, **kwargs):
        self.kwargs["pk"] = self.request.user.id
        return self.retrieve(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(summary=_("List user groups.")),
    retrieve=extend_schema(summary=_("Retrieve a user group.")),
    create=extend_schema(summary=_("Create a user group.")),
    update=extend_schema(summary=_("Update a user group.")),
    destroy=extend_schema(summary=_("Delete a user group.")),
    partial_update=extend_schema(exclude=True),
)
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.prefetch_related("user_set").all().order_by("name")
    pagination_class = BffPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ["name"]
    permission_classes = [IsAuthenticated, ManageGroup]
    allowed_methods = ["get", "put", "post", "delete"]
    serializer_class = ManageGroupSerializer

    def get_serializer_class(self):
        if self.action == "list" and self.request.method == "GET":
            return GroupSerializer
        return ManageGroupSerializer

    def perform_create(self, serializer):
        group = serializer.save()
        self.request.user.manages_groups.add(group)


@extend_schema_view(
    retrieve=extend_schema(summary=_("Retrieve access requests.")),
    create=extend_schema(
        summary=_("Create an access request."),
        request=CreateAccessRequestSerializer,
        responses={201: CreateAccessRequestSerializer},
    ),
    partial_update=extend_schema(
        summary=_("Handle an access request."),
        request=HandleAccessRequestSerializer,
        responses={200: HandleAccessRequestSerializer},
    ),
)
class AccessRequestViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    PatchModelMixin,
    viewsets.GenericViewSet,
):
    """
    Access request for a particular zaak
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, CanCreateOrHandleAccessRequest]
    queryset = AccessRequest.objects.all()

    def get_serializer_class(self):
        mapping = {
            "GET": AccessRequestDetailSerializer,
            "POST": CreateAccessRequestSerializer,
            "PATCH": HandleAccessRequestSerializer,
        }
        return mapping[self.request.method]


@extend_schema_view(
    retrieve=extend_schema(summary=_("Retrieve atomic permission.")),
    create=extend_schema(
        summary=_("Grant atomic permission to ZAAK."),
        request=GrantPermissionSerializer,
        responses={201: GrantPermissionSerializer},
    ),
    destroy=extend_schema(summary=_("Delete atomic permission.")),
)
class AtomicPermissionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Create and delete an atomic permission for a particular user
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, CanGrantAccess]
    queryset = UserAtomicPermission.objects.select_related("user", "atomic_permission")
    serializer_class = AtomicPermissionSerializer

    def get_serializer_class(self):
        mapping = {
            "GET": AtomicPermissionSerializer,
            "POST": GrantPermissionSerializer,
            "DELETE": AtomicPermissionSerializer,
        }
        return mapping[self.request.method]

    @transaction.atomic
    def perform_destroy(self, instance):
        atomic_permission = instance.atomic_permission
        user = instance.user
        zaak = atomic_permission.object_url

        super().perform_destroy(instance)

        # remove permission if there are no users using it
        if not atomic_permission.useratomicpermission_set.count():
            atomic_permission.delete()

        # send email about losing the access to the user
        transaction.on_commit(
            lambda: send_email_to_requester(
                user,
                zaak_url=zaak,
                result=AccessRequestResult.reject,
                request=self.request,
                ui=True,
            )
        )


@extend_schema_view(
    list=extend_schema(summary=_("List authorization profiles.")),
    retrieve=extend_schema(summary=_("Retrieve authorization profile.")),
    create=extend_schema(summary=_("Create authorization profile.")),
    update=extend_schema(summary=_("Update authorization profile.")),
    destroy=extend_schema(summary=_("Delete authorization profile.")),
)
class AuthProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = AuthorizationProfile.objects.all()
    serializer_class = AuthProfileSerializer
    lookup_field = "uuid"
    http_method_names = ["get", "post", "put", "delete"]


@extend_schema_view(
    list=extend_schema(summary=_("List roles.")),
    retrieve=extend_schema(summary=_("Retrieve role.")),
    create=extend_schema(summary=_("Create role.")),
    update=extend_schema(summary=_("Update role.")),
)
class RoleViewSet(
    mixins.CreateModelMixin,
    UpdateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        serializer = serializer_class(*args, **kwargs)
        if kwargs.get("many", False):
            serializer.child.set_permissions_choices()
        else:
            serializer.set_permissions_choices()

        return serializer


@extend_schema_view(
    list=extend_schema(summary=_("List user authorization profiles.")),
    retrieve=extend_schema(summary=_("Retrieve user authorization profile.")),
    create=extend_schema(summary=_("Create user authorization profile.")),
    partial_update=extend_schema(
        summary=_("Partially update user authorization profile.")
    ),
    update=extend_schema(summary=_("Update user authorization profile.")),
    destroy=extend_schema(summary=_("Delete user authorization profile.")),
)
class UserAuthorizationProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = (
        UserAuthorizationProfile.objects.select_related("user")
        .select_related("auth_profile")
        .all()
        .order_by("user", "auth_profile")
    )
    pagination_class = BffPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["user", "auth_profile"]

    def get_serializer_class(self):
        mapping = {
            "GET": ReadUserAuthorizationProfileSerializer,
            "POST": UserAuthorizationProfileSerializer,
            "PUT": UserAuthorizationProfileSerializer,
            "PATCH": UserAuthorizationProfileSerializer,
            "DELETE": UserAuthorizationProfileSerializer,
        }
        return mapping[self.request.method]
