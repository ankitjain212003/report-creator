# Django imports
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Local imports
from customers.models import Company
from accounts.models import CustomUser
from utils.validators import xss_validator

# Constants
VULNERABLE = 'Vulnerable'
CONFIRMED = 'Confirm Fixed'
ACCEPTED_RISK = 'Accepted Risk'

STATUS_CHOICES = [
    (VULNERABLE, 'Vulnerable'),
    (CONFIRMED, 'Confirm Fixed'),
    (ACCEPTED_RISK, 'Accepted Risk'),
]

PROJECT_STATUS_CHOICES = [
    ('Upcoming', 'Upcoming'),
    ('In Progress', 'In Progress'),
    ('Delay', 'Delay'),
    ('Completed', 'Completed'),
]

AUDIT_TYPE_CHOICES = [
    ('network_infra', 'Network Infrastructure Audit'),
    ('process_audit', 'Process Audit'),
    ('red_team', 'Red Team Assessment'),
    ('source_code', 'Source Code Review'),
    ('vapt_infra', 'VAPT - Infrastructure'),
    ('vapt_app', 'VAPT - Application'),
    ('website', 'Website'),
    ('web_app', 'Web Application'),
    ('wireless', 'Wireless Security Audit'),
]
AUDIT_MODE_CHOICES = [
    ('on_site', 'On Site'),
    ('office', 'Office')
]

class Project(models.Model):
    name = models.CharField(max_length=100, unique=False, null=False, blank=False, default=None)
    companyname = models.ForeignKey(Company, on_delete=models.CASCADE, editable=False, blank=True, null=True)
    description = models.TextField(null=False, blank=False, default=None, validators=[xss_validator])
    projecttype = models.CharField(max_length=100, null=False, blank=False, default=None)
    audit_type = models.CharField(max_length=50, choices=AUDIT_TYPE_CHOICES, blank=True, null=True)
    audit_mode = models.CharField(max_length=20, choices=AUDIT_MODE_CHOICES, blank=True, null=True)
    startdate = models.DateField(default=timezone.now)
    enddate = models.DateField(null=True, blank=True)
    TESTING_TYPE_CHOICES = [
    ("White Box", "White Box"),
    ("Black Box", "Black Box"),
    ("Grey Box", "Grey Box"),
]

    testingtype = models.CharField(
    max_length=100,
    choices=TESTING_TYPE_CHOICES,
    default="White Box",
    null=False,
    blank=False
)
   
    projectexception = models.TextField(null=True, blank=True, validators=[xss_validator])
    owner = models.ManyToManyField(CustomUser, blank=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES)
    contact_person_name = models.CharField(max_length=100, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)
    audit_organisation_name = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True, related_name='audit_projects')
    website_detail = models.ForeignKey('PrjectScope', on_delete=models.SET_NULL, blank=True, null=True, related_name='website_projects')
    

    def clean(self):
        if self.enddate and self.enddate < self.startdate:
            raise ValidationError(_('End date cannot be earlier than start date'))

    @property
    def calculate_status(self):
        current_date = timezone.now().date()
        if self.enddate:
            if current_date < self.startdate:
                return 'Upcoming'
            elif self.startdate <= current_date <= self.enddate:
                return 'In Progress'
            elif current_date > self.enddate:
                return 'Delay'
        return 'Upcoming'

    def save(self, *args, **kwargs):
        if self.status != 'Completed':
            self.status = self.calculate_status
        super(Project, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']


class PrjectScope(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    scope = models.CharField(max_length=500)
    description = models.CharField(max_length=100, null=True, blank=True, default=None)

    class Meta:
        unique_together = ['project', 'scope']


class Vulnerability(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    vulnerabilityname = models.CharField(max_length=300, default=None, blank=True, null=True)
    vulnerabilityseverity = models.CharField(max_length=300, null=True)
    cvssscore = models.FloatField(blank=True, null=True)
    cvssvector = models.CharField(max_length=300, default=None, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=VULNERABLE)
    vulnerabilitydescription = models.TextField(blank=True, null=True, validators=[xss_validator])
    POC = models.TextField(default=None, blank=True, null=True, validators=[xss_validator])
    created = models.DateTimeField(auto_now_add=True, editable=False, null=True)
    vulnerabilitysolution = models.TextField(blank=True, null=True, validators=[xss_validator])
    vulnerabilityreferlnk = models.TextField(blank=True, null=True, validators=[xss_validator])
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, editable=False, related_name='vulnerability_created_by', to_field='id')
    last_updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='vulnerability_last_updated_by', to_field='id')
    cwe = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = (("project", "vulnerabilityname"),)

    def __str__(self):
        return self.vulnerabilityname


class Vulnerableinstance(models.Model):
    vulnerabilityid = models.ForeignKey(Vulnerability, on_delete=models.CASCADE, related_name='instances')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    URL = models.CharField(max_length=1000, default=None, blank=True, null=True)
    Parameter = models.CharField(max_length=1000, default=None, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=VULNERABLE)

    def save(self, *args, **kwargs):
        existing_instances = Vulnerableinstance.objects.filter(
            vulnerabilityid=self.vulnerabilityid,
            URL=self.URL,
            Parameter=self.Parameter
        ).exists()
        if not existing_instances:
            super(Vulnerableinstance, self).save(*args, **kwargs)


class ProjectRetest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    startdate = models.DateField()
    enddate = models.DateField()
    owner = models.ManyToManyField(CustomUser, blank=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES)

    def clean(self):
        if self.enddate < self.startdate:
            raise ValidationError(_('End date cannot be earlier than start date'))

    @property
    def calculate_status(self):
        current_date = timezone.now().date()
        if current_date < self.startdate:
            return 'Upcoming'
        elif self.startdate <= current_date <= self.enddate:
            return 'In Progress'
        elif current_date > self.enddate:
            return 'Delay'

    def save(self, *args, **kwargs):
        if self.status != 'Completed':
            self.status = self.calculate_status
        super(ProjectRetest, self).save(*args, **kwargs)
