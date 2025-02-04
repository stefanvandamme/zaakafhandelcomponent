# Generated by Django 3.2.12 on 2022-07-10 09:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0009_auto_20220709_1139"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="checklisttype",
            options={
                "verbose_name": "checklisttype",
                "verbose_name_plural": "checklisttypes",
            },
        ),
        migrations.AlterField(
            model_name="checklistquestion",
            name="checklisttype",
            field=models.ForeignKey(
                help_text="Checklisttype related to this question.",
                on_delete=django.db.models.deletion.PROTECT,
                to="checklists.checklisttype",
            ),
        ),
    ]
