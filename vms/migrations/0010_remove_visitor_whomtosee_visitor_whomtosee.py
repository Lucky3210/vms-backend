# Generated by Django 5.0.3 on 2024-06-24 19:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vms', '0009_remove_attendant_staff_alter_visitor_organization'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitor',
            name='whomToSee',
        ),
        migrations.AddField(
            model_name='visitor',
            name='whomToSee',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='visitors', to='vms.staff'),
        ),
    ]