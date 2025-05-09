# Generated by Django 5.1.8 on 2025-04-22 06:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_remove_company_audit_organisation_name'),
        ('project', '0014_remove_project_companyname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_projects', to='project.project'),
        ),
    ]
