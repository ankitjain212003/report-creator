from rest_framework import viewsets
from project.models import WorkOrder
from project.serializers import WorkOrderSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from project.models import WorkOrder


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
def print_workorder(request, pk):
    workorder = WorkOrder.objects.get(pk=pk)
    html = render_to_string('workorder_pdf.html', {'workorder': workorder})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="workorder_{pk}.pdf"'
    weasyprint.HTML(string=html).write_pdf(response)
    return response