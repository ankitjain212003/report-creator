# Generated by Django 5.1.8 on 2025-04-22 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0016_rename_name_project_projectname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='Projectname',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
