# Generated by Django 3.2.12 on 2022-07-09 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0008_auto_20220525_0701"),
    ]

    operations = [
        migrations.RenameField(
            model_name="checklist",
            old_name="checklist_type",
            new_name="checklisttype",
        ),
        migrations.RenameField(
            model_name="checklistquestion",
            old_name="checklist_type",
            new_name="checklisttype",
        ),
        migrations.AlterUniqueTogether(
            name="checklistquestion",
            unique_together={("question", "checklisttype"), ("checklisttype", "order")},
        ),
    ]
