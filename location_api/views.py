from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import State
from .serializers import StateSerializer, CitySerializer

@api_view(['GET'])
def list_states(request):
    states = State.objects.all()
    serializer = StateSerializer(states, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def cities_by_state(request, state_name):
    try:
        state = State.objects.get(name__iexact=state_name)
        cities = state.cities.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)
    except State.DoesNotExist:
        return Response({"error": "State not found"}, status=404)
