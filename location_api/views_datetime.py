from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def current_datetime(request):
    now = datetime.now()
    return Response({
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M:%S")
    })
