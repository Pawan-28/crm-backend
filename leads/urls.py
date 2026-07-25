from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, PublicLeadCreateView

router = DefaultRouter()
router.register('', LeadViewSet, basename='leads')

urlpatterns = [
    # Public endpoint - No authentication required
    path('public/leads/', PublicLeadCreateView.as_view(), name='public-lead-create'),
    
    # All other lead endpoints - Authentication required
    path('', include(router.urls)),
]