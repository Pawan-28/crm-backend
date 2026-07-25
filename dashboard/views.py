from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from leads.models import Lead, Activity
from users.models import User
from .serializers import DashboardStatsSerializer, RecentActivitySerializer, MemberDashboardSerializer
from utils.permissions import IsAdmin, IsAdminOrMember

class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Get all leads
        total_leads = Lead.objects.count()
        
        # Status wise counts
        new_leads = Lead.objects.filter(status='new').count()
        contacted = Lead.objects.filter(status='contacted').count()
        qualified = Lead.objects.filter(status='qualified').count()
        proposal_sent = Lead.objects.filter(status='proposal_sent').count()
        won_leads = Lead.objects.filter(status='won').count()
        lost_leads = Lead.objects.filter(status='lost').count()
        
        # Member count
        total_members = User.objects.filter(role='member').count()
        
        # Recent activities (last 10)
        recent_activities = Activity.objects.all()[:10]
        activities_serializer = RecentActivitySerializer(recent_activities, many=True)
        
        # Prepare stats
        stats = {
            'total_leads': total_leads,
            'new_leads': new_leads,
            'contacted': contacted,
            'qualified': qualified,
            'proposal_sent': proposal_sent,
            'won_leads': won_leads,
            'lost_leads': lost_leads,
            'total_members': total_members,
            'recent_activities': activities_serializer.data,
        }
        
        return Response({
            'status': 'success',
            'data': stats
        })

class MemberDashboardView(APIView):
    permission_classes = [IsAdminOrMember]
    
    def get(self, request):
        user = request.user
        
        # Get leads assigned to this member
        assigned_leads = Lead.objects.filter(assigned_to=user)
        
        # Count by status
        total_assigned = assigned_leads.count()
        new_leads = assigned_leads.filter(status='new').count()
        contacted = assigned_leads.filter(status='contacted').count()
        qualified = assigned_leads.filter(status='qualified').count()
        proposal_sent = assigned_leads.filter(status='proposal_sent').count()
        won = assigned_leads.filter(status='won').count()
        lost = assigned_leads.filter(status='lost').count()
        
        # Recent activities (last 10)
        recent_activities = Activity.objects.filter(user=user)[:10]
        activities_serializer = RecentActivitySerializer(recent_activities, many=True)
        
        # Prepare stats
        stats = {
            'assigned_leads': total_assigned,
            'new_leads': new_leads,
            'contacted': contacted,
            'qualified': qualified,
            'proposal_sent': proposal_sent,
            'won': won,
            'lost': lost,
            'recent_activities': activities_serializer.data,
        }
        
        return Response({
            'status': 'success',
            'data': stats
        })

class ActivityTimelineView(APIView):
    permission_classes = [IsAdminOrMember]
    
    def get(self, request):
        user = request.user
        
        if user.role == 'admin':
            activities = Activity.objects.all()[:20]
        else:
            activities = Activity.objects.filter(
                Q(user=user) | Q(lead__assigned_to=user)
            ).distinct()[:20]
        
        serializer = RecentActivitySerializer(activities, many=True)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        })

class LeadStatsView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Get last 30 days stats
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        leads_last_30_days = Lead.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Daily stats
        daily_stats = []
        for i in range(30):
            date = start_date + timedelta(days=i)
            day_leads = leads_last_30_days.filter(
                created_at__date=date.date()
            )
            daily_stats.append({
                'date': date.date().strftime('%Y-%m-%d'),
                'count': day_leads.count()
            })
        
        # Status distribution
        status_distribution = {}
        for status, _ in Lead.STATUS_CHOICES:
            status_distribution[status] = Lead.objects.filter(status=status).count()
        
        return Response({
            'status': 'success',
            'data': {
                'daily_stats': daily_stats,
                'status_distribution': status_distribution,
                'total_leads_30_days': leads_last_30_days.count(),
            }
        })