import io
import logging
import urllib
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import bleach
import pygal
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from pygal.style import Style
from weasyprint import HTML
from weasyprint.urls import default_url_fetcher
from xlsxwriter.workbook import Workbook
from docxtpl import DocxTemplate, RichText
from django.shortcuts import get_object_or_404
from datetime import datetime
from jinja2.sandbox import SandboxedEnvironment
import html
import traceback

from accounts.models import CustomUser, CustomGroup
from customers.models import Company
from .models import (PrjectScope, Project, ProjectRetest, Vulnerability,
                     Vulnerableinstance)
from utils.doc_style import get_subdoc, main_doc_style

logger = logging.getLogger(__name__)
logger = logging.getLogger('weasyprint')

base_url = ""
token = None

def whitelisted_fetcher(url):
    allowed_prefixes = [
        "https://report-creator.onrender.com/static/css/"
    ]
    if any(url.startswith(prefix) for prefix in allowed_prefixes):
        return default_url_fetcher(url)
    raise ValueError(f"URL is Not WhiteListed for: '{url}'")

def CheckReport(Report_format, Report_type, pk, url, standard, request, access_token):
    global base_url
    base_url = url
    global token
    token = access_token

    if Report_format == "excel":
        return CreateExcel(pk)
    if Report_format == "docx":
        return generate_vulnerability_document(pk, Report_type, standard)
    if Report_format == "pdf":
        return GetHTML(Report_type, pk, standard, request)

def generate_vulnerability_document(pk, Report_type, standard):
    try:
        project = get_object_or_404(Project, id=pk)
        owners = project.owner.all()
        vuln = Vulnerability.objects.filter(project=project).order_by('-cvssscore')
        totalvulnerability = vuln.count()
        totalretests_queryset = ProjectRetest.objects.filter(project_id=pk)
        projectscope = PrjectScope.objects.filter(project=project)

        template_path = os.path.join(settings.BASE_DIR, 'templates', 'report.docx')
        doc = DocxTemplate(template_path)

        project_manager_group = CustomGroup.objects.get(name='Project Manager')
        projectmanagers = CustomUser.objects.filter(groups=project_manager_group)
        customeruser = CustomUser.objects.filter(company=project.companyname, is_active=True)
        mycomany = Company.objects.filter(internal=True).values_list('name', flat=True).first()

        project_description = get_subdoc(doc, project.description, token, base_url)
        project_exception = get_subdoc(doc, project.projectexception, token, base_url)

        for vulnerability in vuln:
            vulnerability.vulnerabilitydescription = get_subdoc(doc, vulnerability.vulnerabilitydescription, token, base_url)
            vulnerability.POC = get_subdoc(doc, vulnerability.POC, token, base_url)
            vulnerability.vulnerabilitysolution = get_subdoc(doc, vulnerability.vulnerabilitysolution, token, base_url)
            vulnerability.vulnerabilityreferlnk = get_subdoc(doc, vulnerability.vulnerabilityreferlnk, token, base_url)
            vulnerability.instances_data = [
                {
                    'URL': instance.URL,
                    'Parameter': instance.Parameter or '',
                    'Status': instance.status
                }
                for instance in Vulnerableinstance.objects.filter(vulnerabilityid=vulnerability, project=project)
                if instance.URL
            ]

        totalretest = [
            {
                "startdate": retest.startdate,
                "enddate": retest.enddate,
                "owners": [owner.full_name for owner in retest.owner.all()]
            }
            for retest in totalretests_queryset
        ]

        currentdate = datetime.now()
        context = {
            'project': project, 'vulnerabilities': vuln, 'Report_type': Report_type, 'mycomany': mycomany,
            'projectmanagers': projectmanagers, 'customeruser': customeruser, 'owners': owners,
            'project_exception': project_exception, 'project_description': project_description,
            "settings": settings, "currentdate": currentdate, 'standard': standard,
            'totalvulnerability': totalvulnerability, 'totalretest': totalretest,
            'projectscope': projectscope, 'page_break': RichText('\f'), 'new_line': RichText('\n')
        }

        jinja_env = SandboxedEnvironment(autoescape=True)
        jinja_env.trim_blocks = True
        jinja_env.lstrip_blocks = True
        doc.render(context, jinja_env)
        doc = main_doc_style(doc)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename={project.name}vulnerability_report.docx'
        doc.save("report.docx")

        return response

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error("Traceback: " + traceback.format_exc())
        return Response({"Status": "Failed", "Message": "Something Went Wrong"})

def generate_pdf_report(rendered_content, base_url):
    try:
        pdf = HTML(string=rendered_content, url_fetcher=whitelisted_fetcher, base_url=base_url).write_pdf()
        return HttpResponse(pdf, content_type='application/pdf')
    except Exception as e:
        logger.error("Something Went Wrong: %s", e)
        return Response({"Status": "Failed", "Message": "Something Went Wrong"})
