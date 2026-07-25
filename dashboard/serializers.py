from rest_framework import serializers
from leads.models import Lead, Activity
from users.models import User

class DashboardStatsSerializer(serializers.Serializer):
    total_leads = serializers.IntegerField()
    new_leads = serializers.IntegerField()
    won_leads = serializers.IntegerField()
    lost_leads = serializers.IntegerField()
    total_members = serializers.IntegerField()
    contacted = serializers.IntegerField()
    qualified = serializers.IntegerField()
    proposal_sent = serializers.IntegerField()

class RecentActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        from leads.models import Activity
        model = Activity
        fields = ('id', 'action', 'action_display', 'description', 'user_name', 'lead_name', 'created_at')
        read_only_fields = ('id', 'action', 'action_display', 'description', 'user_name', 'lead_name', 'created_at')

class MemberDashboardSerializer(serializers.Serializer):
    assigned_leads = serializers.IntegerField()
    new_leads = serializers.IntegerField()
    contacted = serializers.IntegerField()
    qualified = serializers.IntegerField()
    proposal_sent = serializers.IntegerField()
    won = serializers.IntegerField()
    lost = serializers.IntegerField()
    recent_activities = RecentActivitySerializer(many=True)