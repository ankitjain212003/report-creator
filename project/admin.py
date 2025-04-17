from django.contrib import admin
from .models import Project,Vulnerability, Vulnerableinstance,WorkOrder

# Register your models here.
admin.site.register(Project)
admin.site.register(Vulnerability)
admin.site.register(Vulnerableinstance)
admin.site.register(WorkOrder)