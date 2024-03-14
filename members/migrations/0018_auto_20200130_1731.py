# Generated by Django 2.2.9 on 2020-01-30 16:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0017_auto_20200125_1457"),
    ]

    operations = [
        migrations.RenameField(
            model_name="department",
            old_name="responsible_contact",
            new_name="department_email",
        ),
        migrations.RemoveField(
            model_name="department",
            name="onMap",
        ),
        migrations.AddField(
            model_name="department",
            name="department_leaders",
            field=models.ManyToManyField(
                limit_choices_to={"user__is_staff": True}, to="members.Person"
            ),
        ),
    ]
