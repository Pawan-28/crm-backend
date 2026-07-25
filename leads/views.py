from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Lead, Note, Activity
from .serializers import (
    LeadSerializer, LeadCreateSerializer, LeadUpdateSerializer,
    NoteSerializer, ActivitySerializer, PublicLeadSerializer
)
from utils.permissions import IsAdmin, IsAdminOrMember
from utils.pagination import CustomPagination


class PublicLeadCreateView(APIView):
    """
    Public endpoint for creating leads without authentication.
    Anyone can submit a lead through the landing page.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = PublicLeadSerializer(data=request.data)
        if serializer.is_valid():
            lead = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Lead submitted successfully! We will contact you soon.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAdminOrMember]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'assigned_to']
    search_fields = ['full_name', 'email', 'phone', 'company']
    ordering_fields = ['created_at', 'full_name', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Lead.objects.all()
        return Lead.objects.filter(assigned_to=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeadCreateSerializer
        if self.action in ['update', 'partial_update']:
            return LeadUpdateSerializer
        return LeadSerializer
    
    def perform_create(self, serializer):
        lead = serializer.save(created_by=self.request.user)
        # Create activity
        Activity.objects.create(
            lead=lead,
            user=self.request.user,
            action='created',
            description=f'Lead "{lead.full_name}" was created'
        )
    
    def perform_update(self, serializer):
        old_lead = self.get_object()
        old_status = old_lead.status
        old_assigned_to = old_lead.assigned_to
        lead = serializer.save()
        
        # Check if status changed
        if old_status != lead.status:
            Activity.objects.create(
                lead=lead,
                user=self.request.user,
                action='status_changed',
                description=f'Status changed from "{old_status}" to "{lead.status}"'
            )
        
        # Check if assigned user changed
        if old_assigned_to != lead.assigned_to:
            assigned_name = lead.assigned_to.full_name if lead.assigned_to else "Unassigned"
            Activity.objects.create(
                lead=lead,
                user=self.request.user,
                action='assigned',
                description=f'Lead assigned to {assigned_name}'
            )
        
        Activity.objects.create(
            lead=lead,
            user=self.request.user,
            action='updated',
            description=f'Lead "{lead.full_name}" was updated'
        )
    
    def destroy(self, request, *args, **kwargs):
        lead = self.get_object()
        lead.delete()
        return Response({
            'status': 'success',
            'message': f'Lead "{lead.full_name}" deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        lead = self.get_object()
        notes = lead.notes.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        lead = self.get_object()

        print("Request Data:", request.data)   # Debug

        serializer = NoteSerializer(data=request.data)

        if serializer.is_valid():
            note = serializer.save(
                lead=lead,
                user=request.user
            )

            Activity.objects.create(
                lead=lead,
                user=request.user,
                action='note_added',
                description=f'Note added by {request.user.full_name}'
            )

            return Response(
                NoteSerializer(note).data,
                status=status.HTTP_201_CREATED
            )

        print("Serializer Errors:", serializer.errors)   # Debug

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        lead = self.get_object()
        activities = lead.activities.all()
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        lead = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Lead.STATUS_CHOICES):
            return Response({
                'status': 'error',
                'message': 'Invalid status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = lead.status
        lead.status = new_status
        lead.save()
        
        # Create activity
        Activity.objects.create(
            lead=lead,
            user=request.user,
            action='status_changed',
            description=f'Status changed from "{old_status}" to "{new_status}"'
        )
        
        return Response({
            'status': 'success',
            'message': f'Status updated to "{new_status}"'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'new': queryset.filter(status='new').count(),
            'contacted': queryset.filter(status='contacted').count(),
            'qualified': queryset.filter(status='qualified').count(),
            'proposal_sent': queryset.filter(status='proposal_sent').count(),
            'won': queryset.filter(status='won').count(),
            'lost': queryset.filter(status='lost').count(),
        }
        
        return Response(stats)