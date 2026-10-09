from datetime import date
from unittest.mock import patch
from django.test import TestCase, Client
from django.core.cache import cache
from volunteers.models import Volunteer, TeamMember, generate_unique_member_id
from volunteers.subscription_services import (
    get_member_subscription_summary,
    send_member_registration_notification,
    send_member_monthly_reminder
)
from volunteers.views import send_member_notifications

class VolunteerApplicationDebounceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/volunteers/apply/'
        cache.clear()

    @patch('volunteers.views.send_sms')
    @patch('volunteers.views.send_system_email')
    def test_apply_volunteer_debounce(self, mock_email, mock_sms):
        """Rapid double-click on apply_volunteer within 60s creates exactly 1 record."""
        post_data = {
            'full_name': 'Tariqul Islam',
            'phone': '01712003344',
            'email': 'tariqul@example.com',
            'blood_group': 'B+',
            'occupation': 'Student',
            'division': 'Rajshahi',
            'district': 'Naogaon',
            'upazila': 'Naogaon Sadar',
            'address': 'Chakdev',
            'payment_mode': 'manual',
            'manual_channel': 'bKash',
            'sender_account': '01712003344',
            'trx_id': 'TRX123456',
        }
        # First submission
        resp1 = self.client.post(self.url, data=post_data)
        self.assertEqual(Volunteer.objects.filter(phone='01712003344').count(), 1)

        # Immediate second submission (simulating rapid double click)
        resp2 = self.client.post(self.url, data=post_data)
        # Must NOT create second volunteer (preventing duplicate member ID registration)
        self.assertEqual(Volunteer.objects.filter(phone='01712003344').count(), 1)

    @patch('volunteers.views.send_sms')
    @patch('volunteers.views.send_system_email')
    def test_apply_volunteer_atomic_cache_lock(self, mock_email, mock_sms):
        """Simulating concurrent request: if atomic cache lock is already acquired, submission is blocked."""
        # Pre-set the atomic cache lock
        cache.set('lock_apply_vol_01712998877', '1', 60)
        post_data = {
            'full_name': 'Concurrent User',
            'phone': '01712998877',
            'payment_mode': 'manual',
            'sender_account': '01712998877',
            'trx_id': 'TRX998877',
        }
        resp = self.client.post(self.url, data=post_data)
        # Must be debounced immediately, no database record created
        self.assertEqual(Volunteer.objects.filter(phone='01712998877').count(), 0)

    def test_apply_volunteer_invalid_phone_rejected(self):
        """Invalid phone number is rejected."""
        post_data = {
            'full_name': 'Invalid Phone User',
            'phone': '12345',  # Invalid phone
            'payment_mode': 'manual',
            'sender_account': '12345',
        }
        resp = self.client.post(self.url, data=post_data)
        self.assertEqual(Volunteer.objects.filter(full_name='Invalid Phone User').count(), 0)


class SubscriptionSummaryCalculationTests(TestCase):
    def test_precomputed_paid_batching(self):
        """Verify precomputed_paid correctly calculates balance without extra DB queries."""
        vol = Volunteer.objects.create(
            full_name="Mahmudur Rahman",
            phone="01711889900",
            member_id="26100101",
            status="approved",
            contribution_frequency="monthly",
            contribution_amount=200.0,
        )
        # With precomputed paid 600.0
        summary = get_member_subscription_summary(vol, precomputed_paid=600.0)
        self.assertEqual(summary['total_paid'], 600.0)
        self.assertEqual(summary['monthly_fee'], 200.0)


class VolunteerSMSTemplateLengthTests(TestCase):
    @patch('volunteers.views.send_sms')
    @patch('volunteers.views.send_system_email')
    def test_volunteer_welcome_sms_length(self, mock_email, mock_sms):
        """Volunteer welcome SMS must not exceed 2 segments (<= 134 chars UCS-2)."""
        vol = Volunteer.objects.create(
            full_name="তরিকুল ইসলাম",
            phone="01712003344",
            member_id="26100804",
            status="approved",
            payment_status="paid",
            contribution_frequency="monthly",
            contribution_amount=200.0,
        )
        send_member_notifications(vol)
        self.assertTrue(mock_sms.called)
        sent_sms = mock_sms.call_args_list[0][0][1]
        # Must fit within 2 segments (<= 134 chars UCS-2)
        self.assertLessEqual(len(sent_sms), 134)
        ucs2_units = len(sent_sms.encode('utf-16-be')) // 2
        self.assertLessEqual(ucs2_units, 134)

    @patch('volunteers.subscription_services.send_sms')
    def test_registration_subscription_sms_length_with_long_name_and_long_id(self, mock_sms):
        """Registration subscription SMS with 14-char ID & long Bengali name must be <= 134 UCS-2 units."""
        vol = Volunteer.objects.create(
            full_name="মোহাম্মদ আব্দুল্লাহ আল মামুন",
            phone="01712003344",
            member_id="HN-TM-2024-001",
            status="approved",
            contribution_frequency="monthly",
            contribution_amount=500.0,
        )
        send_member_registration_notification(vol)
        self.assertTrue(mock_sms.called)
        sent_sms = mock_sms.call_args[0][1]
        self.assertLessEqual(len(sent_sms), 134)
        ucs2_units = len(sent_sms.encode('utf-16-be')) // 2
        self.assertLessEqual(ucs2_units, 134)

    @patch('volunteers.subscription_services.send_sms')
    def test_monthly_reminder_sms_length_with_long_name_and_long_id(self, mock_sms):
        """Monthly dues reminder SMS with 15-char ID & long Bengali name must be <= 134 UCS-2 units."""
        vol = Volunteer.objects.create(
            full_name="মোহাম্মদ আব্দুল্লাহ আল মামুন",
            phone="01712003344",
            member_id="HN-TM-2024-0012",
            status="approved",
            contribution_frequency="monthly",
            contribution_amount=1500.0,
        )
        send_member_monthly_reminder(vol, force=True)
        self.assertTrue(mock_sms.called)
        sent_sms = mock_sms.call_args[0][1]
        self.assertLessEqual(len(sent_sms), 134)
        ucs2_units = len(sent_sms.encode('utf-16-be')) // 2
        self.assertLessEqual(ucs2_units, 134)
