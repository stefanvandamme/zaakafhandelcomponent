from django.core.management import BaseCommand

from zgw_consumers.api_models.constants import VertrouwelijkheidsAanduidingen

from zac.core.services import get_zaaktypen

from ...constants import PermissionObjectTypeChoices
from ...models import BlueprintPermission, Role


class Command(BaseCommand):
    help = """
    Create blueprint permissions for all available zaaktypen
    """

    def handle(self, **options):
        # give access to zaak behandelaars
        zaaktypen = get_zaaktypen()
        roles = Role.objects.all()
        added = []
        for zaaktype in zaaktypen:
            policy = {
                "catalogus": zaaktype.catalogus,
                "zaaktype_omschrijving": zaaktype.omschrijving,
                "max_va": VertrouwelijkheidsAanduidingen.zeer_geheim,
            }

            for role in roles:
                obj, created = BlueprintPermission.objects.get_or_create(
                    role=role,
                    policy=policy,
                    object_type=PermissionObjectTypeChoices.zaak,
                )
                if created:
                    added.append(obj)

        self.stdout.write(
            f" {len(added)} blueprint permissions for zaaktypen are added"
        )
