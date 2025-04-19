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
from xlsxwriter.workbook import Workbook
from docxtpl import DocxTemplate, RichText
from django.shortcuts import get_object_or_404
from datetime import datetime
from jinja2.sandbox import SandboxedEnvironment
import html
import traceback

from accounts.models import CustomUser, CustomGroup
from customers.models import Company
from .models import PrjectScope, Project, ProjectRetest, Vulnerability, Vulnerableinstance
from utils.doc_style import get_subdoc, main_doc_style

logger = logging.getLogger(__name__)
logger = logging.getLogger('weasyprint')

base_url = ""
token = None


def CheckReport(Report_format, Report_type, pk, url, standard, request, access_token):
    global base_url, token
    base_url = url
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
            try:
                vulnerability.vulnerabilitydescription = get_subdoc(doc, vulnerability.vulnerabilitydescription, token, base_url)
            except:
                vulnerability.vulnerabilitydescription = None

            try:
                vulnerability.POC_subdoc = get_subdoc(doc, vulnerability.POC, token, base_url) if vulnerability.POC else None
            except:
                vulnerability.POC_subdoc = None

            try:
                vulnerability.vulnerabilitysolution = get_subdoc(doc, vulnerability.vulnerabilitysolution, token, base_url)
            except:
                vulnerability.vulnerabilitysolution = None

            try:
                vulnerability.vulnerabilityreferlnk = get_subdoc(doc, vulnerability.vulnerabilityreferlnk, token, base_url)
            except:
                vulnerability.vulnerabilityreferlnk = None

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
            'project': project,
            'vulnerabilities': vuln,
            'Report_type': Report_type,
            'mycomany': mycomany,
            'projectmanagers': projectmanagers,
            'customeruser': customeruser,
            'owners': owners,
            'project_exception': project_exception,
            'project_description': project_description,
            "settings": settings,
            "currentdate": currentdate,
            'standard': standard,
            'totalvulnerability': totalvulnerability,
            'totalretest': totalretest,
            'projectscope': projectscope,
            'page_break': RichText('\f'),
            'new_line': RichText('\n')
        }

        jinja_env = SandboxedEnvironment(autoescape=True)
        jinja_env.trim_blocks = True
        jinja_env.lstrip_blocks = True

        doc.render(context, jinja_env)
        doc = main_doc_style(doc)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename={project.name}vulnerability_report.docx'
        doc.save(response)
        return response

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error("Traceback: " + traceback.format_exc())
        return Response({"Status": "Failed", "Message": "Something Went Wrong"})


def CreateExcel(pk):
    try:
        project_name = Project.objects.values_list('name', flat=True).get(id=pk)
        instances = Vulnerableinstance.objects.filter(project_id=pk).select_related('vulnerabilityid').order_by('-vulnerabilityid__cvssscore')
        output = io.BytesIO()
        book = Workbook(output)
        sheet = book.add_worksheet('Vulnerabilities')
        wrap_format = book.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        sheet.set_column('A:A', 20)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('G:G', 70)
        sheet.set_column('H:H', 70)

        header = ['Title', 'Severity', 'Status', 'URL/IP', 'Parameter/Port', 'CVSS Score', 'Description', 'Recommendation']
        for col_num, col_value in enumerate(header):
            sheet.write(0, col_num, col_value, wrap_format)

        for row_num, instance in enumerate(instances, start=1):
            row_data = [
                instance.vulnerabilityid.vulnerabilityname,
                instance.vulnerabilityid.vulnerabilityseverity,
                instance.status,
                instance.URL,
                instance.Parameter,
                instance.vulnerabilityid.cvssscore,
                html.unescape(bleach.clean(instance.vulnerabilityid.vulnerabilitydescription, tags=[], strip=True)),
                html.unescape(bleach.clean(instance.vulnerabilityid.vulnerabilitysolution, tags=[], strip=True))
            ]
            for col_num, col_value in enumerate(row_data):
                sheet.write(row_num, col_num, col_value, wrap_format)

        book.close()
        response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={project_name}vulnerability_report.xlsx'
        return response

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return Response({"Status": "Failed", "Message": "Something Went Wrong"})


def GetHTML(Report_type, pk, standard, request):
    try:
        project = Project.objects.get(pk=pk)
        vuln = Vulnerability.objects.filter(project=project).order_by('-cvssscore')
        instances = Vulnerableinstance.objects.filter(project=project)
        projectmanagers = CustomUser.objects.filter(groups=CustomGroup.objects.get(name='Project Manager'))
        customeruser = CustomUser.objects.filter(company=project.companyname, is_active=True)

        ciritcal = vuln.filter(vulnerabilityseverity='Critical', status='Vulnerable').count()
        high = vuln.filter(vulnerabilityseverity='High', status='Vulnerable').count()
        medium = vuln.filter(vulnerabilityseverity='Medium', status='Vulnerable').count()
        low = vuln.filter(vulnerabilityseverity='Low', status='Vulnerable').count()
        info = vuln.filter(Q(status='Vulnerable') & Q(vulnerabilityseverity__in=['Informational', 'None'])).count()

        custom_style = Style(
            colors=("#FF491C", "#F66E09", "#FBBC02", "#20B803", "#3399FF"),
            background='transparent',
            plot_background='transparent',
            legend_font_size=0,
            legend_box_size=0,
            value_font_size=40
        )
        pie_chart = pygal.Pie(style=custom_style)
        pie_chart.legend_box_size = 0
        pie_chart.add('Critical', ciritcal)
        pie_chart.add('High', high)
        pie_chart.add('Medium', medium)
        pie_chart.add('Low', low)
        pie_chart.add('Informational', info)

        context = {
            'projectscope': PrjectScope.objects.filter(project=project),
            'totalvulnerability': vuln.count(),
            'standard': standard,
            'Report_type': Report_type,
            'mycomany': Company.objects.filter(internal=True).values_list('name', flat=True).first(),
            'totalretest': ProjectRetest.objects.filter(project_id=pk),
            'vuln': vuln,
            'project': project,
            'ciritcal': ciritcal,
            'high': high,
            'medium': medium,
            'low': low,
            'info': info,
            'instances': instances,
            'projectmanagers': projectmanagers,
            'customeruser': customeruser,
            'pie_chart': pie_chart.render(is_unicode=True)
        }

        rendered_content = render_to_string('report.html', context, request=request)
        response = generate_pdf_report(rendered_content, base_url)
        response['Content-Disposition'] = f'attachment; filename={project.name}vulnerability_report.pdf'
        return response

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return Response({"Status": "Failed", "Message": "Something Went Wrong"})


def generate_pdf_report(rendered_content, base_url):
    try:
        pdf = HTML(string=rendered_content, url_fetcher=my_fetcher, base_url=base_url).write_pdf()
        return HttpResponse(pdf, content_type='application/pdf')
    except Exception as e:
        logger.error("Something Went Wrong: %s", e)
        return Response({"Status": "Failed", "Message": "Something Went Wrong"})


def is_whitelisted(url):
    parsed_url = urllib.parse.urlparse(url)
    netloc = parsed_url.netloc.lower()
    port = parsed_url.port if parsed_url.port else 80

    for whitelisted_entry in settings.WHITELIST_IP:
        whitelisted_parsed = urllib.parse.urlparse(whitelisted_entry)
        if netloc == whitelisted_parsed.netloc.lower() and port == (whitelisted_parsed.port or 80):
            return True

    logger.error("URL is not Whitelisted Check the %s", url)
    return False


def my_fetcher(url):
    if is_whitelisted(url):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        headers = {"Authorization": f"Bearer {token}"} if "/api/project/getimage/" in url else {}
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        return {
            "string": response.content,
            "mime_type": response.headers.get("Content-Type", "image/jpeg"),
            "encoding": response.encoding,
            "redirected_url": response.url
        }

    raise ValueError(f'URL is Not WhiteListed for: {url!r}')
