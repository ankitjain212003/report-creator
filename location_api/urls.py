from django.urls import path
from . import views
from .views_datetime import current_datetime 

urlpatterns = [
    path('states/', views.list_states, name='list_states'),
    path('states/<str:state_name>/cities/', views.cities_by_state, name='cities_by_state'),
     path('current-datetime/', current_datetime, name='current_datetime'),
]
