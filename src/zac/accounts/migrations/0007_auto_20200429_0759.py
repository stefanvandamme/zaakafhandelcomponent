# Generated by Django 2.2.5 on 2020-04-29 07:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_auto_20200429_0758"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="UserEntitlement",
            new_name="UserAuthorizationProfile",
        ),
    ]
