# Generated by Django 3.2.12 on 2022-07-28 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("start_process", "0009_alter_processinformatieobject_required"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="processeigenschap",
            unique_together={("camunda_start_process", "eigenschapnaam")},
        ),
    ]
