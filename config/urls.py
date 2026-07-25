from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Lead Management CRM API",
        default_version='v1',
        description="Complete API documentation for Lead Management CRM System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@crm.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Routes
    path('api/auth/', include('authentication.urls')),
    path('api/users/', include('users.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]