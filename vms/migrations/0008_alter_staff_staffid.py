# Generated by Django 5.0.3 on 2024-06-12 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vms', '0007_staff_staffid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='staffId',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
