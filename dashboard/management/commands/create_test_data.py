from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from leads.models import Lead, Activity
import random
from faker import Faker

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Create test data for the CRM'

    def handle(self, *args, **kwargs):
        # Get or create admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@crm.com',
                'role': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('Admin@123')
            admin.save()
            self.stdout.write('Admin user created')
        
        # Get or create members
        members = []
        for i in range(3):
            member, created = User.objects.get_or_create(
                username=f'member{i+1}',
                defaults={
                    'email': f'member{i+1}@crm.com',
                    'role': 'member',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                }
            )
            if created:
                member.set_password('Member@123')
                member.save()
                self.stdout.write(f'Member {i+1} created')
            members.append(member)
        
        # Create leads
        statuses = ['new', 'contacted', 'qualified', 'proposal_sent', 'won', 'lost']
        sources = ['website', 'facebook', 'instagram', 'linkedin', 'google', 'referral', 'other']
        
        for i in range(20):
            lead = Lead.objects.create(
                full_name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number()[:15],
                company=fake.company(),
                source=random.choice(sources),
                status=random.choice(statuses),
                assigned_to=random.choice(members),
                created_by=admin
            )
            
            # Create activity
            Activity.objects.create(
                lead=lead,
                user=admin,
                action='created',
                description=f'Lead "{lead.full_name}" was created'
            )
            
            self.stdout.write(f'Lead {i+1}: {lead.full_name} created')
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))