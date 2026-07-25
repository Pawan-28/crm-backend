from django.db import models
from django.conf import settings
from django.utils import timezone

class Lead(models.Model):
    # Status choices
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal_sent', 'Proposal Sent'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )
    
    # Source choices
    SOURCE_CHOICES = (
        ('website', 'Website'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('google', 'Google'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    )
    
    # Basic Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=255, blank=True, null=True)
    
    # Lead Details
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_leads'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.email}"
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    @property
    def source_display(self):
        return dict(self.SOURCE_CHOICES).get(self.source, self.source)


class Note(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.lead.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Activity(models.Model):
    ACTION_CHOICES = (
        ('created', 'Lead Created'),
        ('updated', 'Lead Updated'),
        ('assigned', 'Lead Assigned'),
        ('status_changed', 'Status Changed'),
        ('note_added', 'Note Added'),
    )
    
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.lead.full_name}"