from django.urls import path
from .views import (
    AdminDashboardView, 
    MemberDashboardView, 
    ActivityTimelineView,
    LeadStatsView
)

urlpatterns = [
    path('admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('member/', MemberDashboardView.as_view(), name='member-dashboard'),
    path('activities/', ActivityTimelineView.as_view(), name='activities'),
    path('stats/', LeadStatsView.as_view(), name='lead-stats'),
]