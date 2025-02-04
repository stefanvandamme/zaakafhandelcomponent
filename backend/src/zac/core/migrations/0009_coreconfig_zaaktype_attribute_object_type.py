# Generated by Django 3.2.12 on 2022-08-10 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_alter_coreconfig_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="coreconfig",
            name="zaaktype_attribute_object_type",
            field=models.URLField(
                default="",
                help_text="A URL-reference to the ZaaktypeAttributes OBJECTTYPE. This is used to get extra data for EIGENSCHAPs.",
                verbose_name="URL-reference to ZaaktypeAttributes in OBJECTTYPES API.",
            ),
        ),
    ]
