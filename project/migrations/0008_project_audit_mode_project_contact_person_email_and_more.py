# Generated by Django 5.1.8 on 2025-04-17 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_project_audit_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='audit_mode',
            field=models.CharField(blank=True, choices=[('on_site', 'On Site'), ('office', 'Office')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='contact_person_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='contact_person_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='contact_person_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
