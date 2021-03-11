import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from zgw_consumers.api_models.constants import VertrouwelijkheidsAanduidingen

from zac.utils.exceptions import get_error_list

from .constants import AccessRequestResult, PermissionObjectType
from .datastructures import ZaaktypeCollection
from .managers import UserManager
from .query import AccessRequestQuerySet, PermissionDefinitionQuerySet


class User(AbstractBaseUser, PermissionsMixin):
    """
    Use the built-in user model.
    """

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer."),
        error_messages={"unique": _("A user with that username already exists.")},
    )
    first_name = models.CharField(_("first name"), max_length=255, blank=True)
    last_name = models.CharField(_("last name"), max_length=255, blank=True)
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # custom permissions
    auth_profiles = models.ManyToManyField(
        "AuthorizationProfile",
        blank=True,
        through="UserAuthorizationProfile",
    )
    permission_definitions = models.ManyToManyField(
        "PermissionDefinition",
        verbose_name=_("permission definitions"),
        related_name="users",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name


# Permissions


class AuthorizationProfile(models.Model):
    """
    Model a set of permission groups that can be assigned to a user.

    "Autorisatieprofiel" in Dutch. This is the finest-grained object that is exposed
    to external systems (via SCIM eventually). Towards IAM/SCIM, this maps to the
    Entitlement concept.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_(
            "Use an easily recognizable name that maps to the function of users."
        ),
    )
    # deprecated
    permission_sets = models.ManyToManyField(
        "PermissionSet",
        verbose_name=_("permission sets"),
        help_text=_(
            "Selecting multiple sets makes them add/merge all the permissions together."
        ),
    )
    permission_definitions = models.ManyToManyField(
        "PermissionDefinition",
        verbose_name=_("permission definitions"),
        related_name="auth_profiles",
    )
    # deprecated
    oo = models.ForeignKey(
        "organisatieonderdelen.OrganisatieOnderdeel",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("organisatieonderdeel"),
        help_text=_(
            "Limit access to data belonging to this OO. Leaving this blank means that "
            "there is no restriction on OO in place."
        ),
    )

    class Meta:
        verbose_name = _("authorization profile")
        verbose_name_plural = _("authorization profiles")

    def __str__(self):
        return self.name


# Deprecated
class PermissionSet(models.Model):
    """
    A collection of permissions that belong to a zaaktype.
    """

    name = models.CharField(_("naam"), max_length=255, unique=True)
    description = models.TextField(_("description"), blank=True)
    permissions = ArrayField(
        models.CharField(max_length=255, blank=False),
        blank=True,
        default=list,
        verbose_name=_("permissions"),
    )
    catalogus = models.URLField(
        _("catalogus"),
        help_text=_("Zaaktypencatalogus waarin de zaaktypen voorkomen."),
        blank=True,
    )
    zaaktype_identificaties = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text=(
            "All permissions selected are scoped to these zaaktypen. "
            "If left empty, this applies to all zaaktypen."
        ),
    )
    max_va = models.CharField(
        _("maximale vertrouwelijkheidaanduiding"),
        max_length=100,
        choices=VertrouwelijkheidsAanduidingen.choices,
        default=VertrouwelijkheidsAanduidingen.openbaar,
        help_text=_(
            "Spans Zaken until and including this vertrouwelijkheidaanduiding."
        ),
    )

    class Meta:
        verbose_name = _("permission set")
        verbose_name_plural = _("permission sets")

    def __str__(self):
        return f"{self.name} ({self.get_max_va_display()})"

    def get_absolute_url(self):
        return reverse("accounts:permission-set-detail", args=[self.id])

    @cached_property
    def zaaktypen(self) -> ZaaktypeCollection:
        return ZaaktypeCollection(
            catalogus=self.catalogus, identificaties=self.zaaktype_identificaties
        )


# Deprecated
class InformatieobjecttypePermission(models.Model):
    permission_set = models.ForeignKey(
        PermissionSet,
        on_delete=models.CASCADE,
        verbose_name=_("permission set"),
        help_text=_("Associated set of permissions for a zaaktype."),
    )
    catalogus = models.URLField(
        verbose_name=_("catalogus"),
        max_length=1000,
        help_text=_(
            "Informatieobjecttype catalogus waarin de informatieobjecttypen voorkomen."
        ),
    )
    omschrijving = models.CharField(
        max_length=100,
        verbose_name=_("omschrijving"),
        help_text=_("Informatieobjecttype omschrijving."),
        blank=True,
    )
    max_va = models.CharField(
        verbose_name=_("maximaal vertrouwelijkheidaanduiding"),
        max_length=100,
        choices=VertrouwelijkheidsAanduidingen.choices,
        default=VertrouwelijkheidsAanduidingen.openbaar,
        help_text=_("Maximaal vertrouwelijkheidaanduiding."),
    )

    class Meta:
        verbose_name = _("informatieobjecttype permission")
        verbose_name_plural = _("informatieobjecttype permissions")

    def __str__(self):
        return f"{self.catalogus} - {self.omschrijving} ({self.max_va})"


class UserAuthorizationProfile(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    auth_profile = models.ForeignKey("AuthorizationProfile", on_delete=models.CASCADE)

    start = models.DateTimeField(_("start"), blank=True, null=True)
    end = models.DateTimeField(_("end"), blank=True, null=True)


# Deprecated
class AccessRequest(models.Model):
    requester = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="initiated_requests"
    )
    handler = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="handled_requests",
        help_text=_("user who has handled the request"),
    )
    zaak = models.URLField(
        _("zaak"),
        max_length=1000,
        help_text=_("URL reference to the zaak in its API"),
    )
    comment = models.CharField(
        _("comment"),
        max_length=1000,
        blank=True,
        help_text=_("Comment provided by the handler"),
    )
    result = models.CharField(
        _("result"),
        max_length=50,
        choices=AccessRequestResult.choices,
        blank=True,
        help_text=_("Result of the access request"),
    )
    start_date = models.DateField(
        _("start date"),
        blank=True,
        null=True,
        help_text=_("Start date of the granted access"),
    )
    end_date = models.DateField(
        _("end date"),
        blank=True,
        null=True,
        help_text=_("End date of the granted access"),
    )

    objects = AccessRequestQuerySet.as_manager()

    def clean(self):
        super().clean()

        if self.result and not self.handler:
            raise ValidationError(
                _("The result can't be specified without its handler")
            )


class PermissionDefinition(models.Model):
    object_type = models.CharField(
        _("object type"),
        max_length=50,
        choices=PermissionObjectType.choices,
        help_text=_("Type of the objects this permission applies to"),
    )
    permission = models.CharField(
        _("Permission"), max_length=255, help_text=_("Name of the permission")
    )
    object_url = models.CharField(
        _("object URL"),
        max_length=1000,
        blank=True,
        help_text=_("URL of the object in one of ZGW APIs this permission applies to"),
    )
    policy = JSONField(
        _("policy"),
        null=True,
        blank=True,
        default=dict,
        help_text=_(
            "Blueprint permission definitions, used to check the access to objects based "
            "on their properties i.e. zaaktype, informatieobjecttype"
        ),
    )
    start_date = models.DateTimeField(
        _("start date"),
        blank=True,
        null=True,
        default=timezone.now,
        help_text=_("Start date of the permission"),
    )
    end_date = models.DateTimeField(
        _("end date"),
        blank=True,
        null=True,
        help_text=_("End date of the permission"),
    )
    objects = PermissionDefinitionQuerySet.as_manager()

    class Meta:
        verbose_name = _("permission definition")
        verbose_name_plural = _("permission definitions")

    def get_blueprint_class(self):
        # TODO after burning all deprecated code this import should be moved to the top of the file
        # it will help testing a lot
        from .permissions import registry

        permission = registry[self.permission]
        return permission.blueprint_class

    def clean(self):
        super().clean()

        if not (bool(self.object_url) ^ bool(self.policy)):
            raise ValidationError(
                _("object_url and policy should be mutually exclusive")
            )

        # policy data should be validated against the serializer which is connected to this permission
        blueprint_class = self.get_blueprint_class()
        if self.policy:
            blueprint = blueprint_class(data=self.policy)
            if not blueprint.is_valid():
                raise ValidationError({"policy": get_error_list(blueprint.errors)})

    def has_policy_access(self, obj):
        if not self.policy:
            return False

        blueprint_class = self.get_blueprint_class()
        blueprint = blueprint_class(self.policy)
        return blueprint.has_access(obj)
