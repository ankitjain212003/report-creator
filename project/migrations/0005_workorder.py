# Generated by Django 5.1.8 on 2025-04-17 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_alter_project_enddate_alter_project_startdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audit_no', models.CharField(max_length=100)),
                ('organization_name', models.CharField(max_length=255)),
                ('scope_of_work', models.TextField()),
                ('contact_person', models.CharField(max_length=100)),
                ('phone_no', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('auditor', models.CharField(max_length=255)),
                ('verified_by', models.CharField(max_length=255)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('l1_submission_date', models.DateField(blank=True, null=True)),
                ('work_order_received', models.BooleanField(default=False)),
                ('link_working', models.BooleanField(default=False)),
                ('l1_vulnerabilities', models.TextField(blank=True, null=True)),
                ('auditor1_l1', models.CharField(blank=True, max_length=100)),
                ('auditor2_l1', models.CharField(blank=True, max_length=100)),
                ('high_l1', models.IntegerField(default=0)),
                ('medium_l1', models.IntegerField(default=0)),
                ('low_l1', models.IntegerField(default=0)),
                ('l1_verified_by', models.CharField(blank=True, max_length=255)),
                ('l1_report_sent', models.BooleanField(default=False)),
                ('l1_compliance_received', models.BooleanField(default=False)),
                ('l2_vulnerabilities', models.TextField(blank=True, null=True)),
                ('auditor1_l2', models.CharField(blank=True, max_length=100)),
                ('auditor2_l2', models.CharField(blank=True, max_length=100)),
                ('high_l2', models.IntegerField(default=0)),
                ('medium_l2', models.IntegerField(default=0)),
                ('low_l2', models.IntegerField(default=0)),
                ('l2_verified_by', models.CharField(blank=True, max_length=255)),
                ('l2_report_sent', models.BooleanField(default=False)),
                ('l2_compliance_received', models.BooleanField(default=False)),
                ('final_vulnerabilities', models.TextField(blank=True, null=True)),
                ('auditor1_final', models.CharField(blank=True, max_length=100)),
                ('auditor2_final', models.CharField(blank=True, max_length=100)),
                ('high_final', models.IntegerField(default=0)),
                ('medium_final', models.IntegerField(default=0)),
                ('low_final', models.IntegerField(default=0)),
                ('final_verified_by', models.CharField(blank=True, max_length=255)),
                ('final_report_sent', models.BooleanField(default=False)),
                ('safe_to_host_verified_by', models.CharField(blank=True, max_length=255)),
                ('safe_to_host_sent', models.BooleanField(default=False)),
                ('forwarded_to_certin', models.BooleanField(default=False)),
                ('invoice_sent', models.BooleanField(default=False)),
            ],
        ),
    ]
