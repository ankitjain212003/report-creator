from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.urls import path, re_path

schema_view = get_schema_view(
   openapi.Info(
      title="State & City API",
      default_version='v1',
      description="Browse and test the APIs for all Indian states and cities",
      contact=openapi.Contact(email="youremail@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
