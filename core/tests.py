from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import Event
import json
import datetime

User = get_user_model()

class EventSharingTest(TestCase):
    def setUp(self):
        # Create an officer who can create events
        self.officer = User.objects.create_user(username='officer', password='password', role=User.Role.OFFICER)
        
        # Create a regular member
        self.member = User.objects.create_user(username='member', password='password', role=User.Role.MEMBER)
        
        # Officer creates an event
        self.event_start = timezone.now() + datetime.timedelta(days=1)
        self.event = Event.objects.create(
            user=self.officer,
            title="Shared Event",
            start=self.event_start,
            end=self.event_start + datetime.timedelta(hours=2)
        )

    def test_member_can_see_officer_event(self):
        """
        Verify that a regular member can see the event created by the officer via the events_json API.
        """
        self.client.force_login(self.member)
        response = self.client.get(reverse('events_json'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        # Should find the event in the list
        found = False
        for item in data:
            if item['id'] == self.event.id:
                found = True
                break
        
        self.assertTrue(found, "Member should be able to see the event created by Officer")

    def test_calendar_view_visibility(self):
        """
        Verify that the event appears in the calendar view context for a member.
        """
        self.client.force_login(self.member)
        # Assuming calendar view expects query params or defaults to current month
        # We ensure the event is within the queried range. 
        # For simplicity, let's just hit the calendar root, which defaults to today's month.
        # If the event is next month, we might miss it if we don't adjust args, 
        # so let's make sure the event is today/soon.
        
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        
        # events_by_date is in context
        events_by_date = response.context['events_by_date']
        # Flatten the list of events
        all_events = []
        for date_events in events_by_date.values():
            all_events.extend(date_events)
            
        self.assertIn(self.event, all_events, "Event should be in calendar context for Member")
