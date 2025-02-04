from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import InformatieobjecttypenJSONView, LogoutView, PermissionView
from .viewsets import (
    AccessRequestViewSet,
    AtomicPermissionViewSet,
    AuthProfileViewSet,
    GroupViewSet,
    RoleViewSet,
    UserAuthorizationProfileViewSet,
    UserViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("groups", GroupViewSet, basename="usergroups")
router.register("users", UserViewSet, basename="users")
router.register("access-requests", AccessRequestViewSet)
router.register("cases/access", AtomicPermissionViewSet, basename="accesses")
router.register("auth-profiles", AuthProfileViewSet)
router.register("roles", RoleViewSet)
router.register("user-auth-profiles", UserAuthorizationProfileViewSet)

urlpatterns = router.urls + [
    path(
        "informatieobjecttypen",
        InformatieobjecttypenJSONView.as_view(),
        name="informatieobjecttypen",
    ),
    path("logout", LogoutView.as_view(), name="logout"),
    path("permissions", PermissionView.as_view(), name="permissions"),
]
