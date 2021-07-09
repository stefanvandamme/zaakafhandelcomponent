# Generated by Django 2.2.24 on 2021-07-06 11:08

from django.db import migrations, models


def add_id_to_duplicate_email(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    all_users = User.objects.values("email").distinct()
    for user in all_users:
        duplicate_users = User.objects.filter(email=user["email"]).order_by("id")[1:]

        for duplicate_user in duplicate_users:
            if "@" in duplicate_user.email:
                username, domain = duplicate_user.email.split("@")
                duplicate_user.email = f"{username}_{duplicate_user.id}@{domain}"
                duplicate_user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0036_initial_permission_reason"),
    ]

    operations = [
        migrations.RunPython(add_id_to_duplicate_email),
        migrations.AlterModelOptions(
            name="blueprintpermission",
            options={
                "ordering": ("policy__zaaktype_omschrijving", "permission"),
                "verbose_name": "blueprint definition",
                "verbose_name_plural": "blueprint definitions",
            },
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                condition=models.Q(_negated=True, email=""),
                fields=("email",),
                name="filled_email_unique",
            ),
        ),
    ]
