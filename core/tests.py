import json
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.core.cache import cache
from core.sms_utils import send_sms, evaluate_low_balance_alert

class InboundSMSWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/sms/inbound/'

    @override_settings(AUTOMAS_WEBHOOK_SECRET='test_secret_12345')
    def test_webhook_unauthorized_without_secret(self):
        """Unauthorized webhook call without secret must return 401."""
        response = self.client.post(
            self.url,
            data=json.dumps({"sender": "01700000000", "message": "Test message"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Unauthorized", response.content.decode())

    @override_settings(AUTOMAS_WEBHOOK_SECRET='test_secret_12345')
    def test_webhook_unauthorized_with_wrong_secret(self):
        """Webhook with incorrect secret must return 401."""
        response = self.client.post(
            f"{self.url}?token=wrong_secret",
            data=json.dumps({"sender": "01700000000", "message": "Test message"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    @override_settings(AUTOMAS_WEBHOOK_SECRET='')
    def test_webhook_fail_closed_when_secret_unset_in_settings(self):
        """When AUTOMAS_WEBHOOK_SECRET is not configured, webhook must fail closed (401)."""
        response = self.client.post(
            f"{self.url}?token=any_token",
            data={"sender": "01700000000", "message": "Test"},
        )
        self.assertEqual(response.status_code, 401)

    @override_settings(AUTOMAS_WEBHOOK_SECRET='test_secret_12345')
    @patch('core.email_utils.send_system_email')
    @patch('core.views_sms.send_sms')
    def test_webhook_authorized_via_header(self, mock_send_sms, mock_send_email):
        """Webhook with valid token passed via X-Webhook-Token header succeeds."""
        mock_send_sms.return_value = True
        mock_send_email.return_value = True
        response = self.client.post(
            self.url,
            data={"sender": "01712345678", "message": "Emergency assistance"},
            HTTP_X_WEBHOOK_TOKEN='test_secret_12345'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_send_sms.called)

    @override_settings(AUTOMAS_WEBHOOK_SECRET='test_secret_12345')
    @patch('core.email_utils.send_system_email')
    @patch('core.views_sms.send_sms')
    def test_webhook_authorized_success(self, mock_send_sms, mock_send_email):
        """Webhook with valid token succeeds, sends SMS forward to admin <= 70 chars."""
        mock_send_sms.return_value = True
        mock_send_email.return_value = True
        response = self.client.post(
            f"{self.url}?token=test_secret_12345",
            data={"sender": "01712345678", "message": "Emergency help needed"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_send_sms.called)
        # Verify forwarded SMS is concise (1 segment <= 70 chars)
        sent_msg = mock_send_sms.call_args[0][1]
        self.assertLessEqual(len(sent_msg), 70)


class ComplaintAbusePreventionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/submit-complaint/'
        cache.clear()

    @patch('core.email_utils.send_system_email')
    @patch('core.sms_utils.send_sms')
    def test_honeypot_trapping(self, mock_send_sms, mock_send_email):
        """Bots filling the hidden website_hp field are trapped without SMS or email."""
        post_data = {
            'name': 'Spam Bot',
            'phone': '01711111111',
            'subject_type': 'অন্যান্য',
            'details': 'Buy cheap crypto now',
            'website_hp': 'http://spambot.com',  # Bot filled honeypot
        }
        response = self.client.post(
            self.url,
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        # Must NOT dispatch any SMS or email
        self.assertFalse(mock_send_sms.called)
        self.assertFalse(mock_send_email.called)

    @patch('core.email_utils.send_system_email')
    @patch('core.sms_utils.send_sms')
    def test_valid_complaint_and_cooldown_throttling(self, mock_send_sms, mock_send_email):
        """Valid complaint succeeds, but immediate repeated submission triggers phone cooldown."""
        mock_send_sms.return_value = True
        mock_send_email.return_value = True
        post_data = {
            'name': 'Rahim Uddin',
            'phone': '01711223344',
            'subject_type': 'অনিয়ম ও দুর্নীতি',
            'details': 'Road construction corruption in Mohadevpur',
            'website_hp': '',
        }
        # First submission: success (200)
        resp1 = self.client.post(
            self.url,
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertTrue(data1.get('success'))
        self.assertTrue(mock_send_sms.called)

        # Immediate second submission with same phone: throttled by cooldown (429)
        resp2 = self.client.post(
            self.url,
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp2.status_code, 429)
        data2 = resp2.json()
        self.assertFalse(data2.get('success'))
        self.assertIn('অনুগ্রহ করে', data2.get('message', ''))


class SMSBalanceAlertTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch('core.email_utils.send_system_email')
    @patch('core.sms_utils.send_sms')
    def test_sms_balance_alert_cooldown(self, mock_send_sms, mock_send_email):
        """Alert is sent when balance is low, but cached cooldown prevents repeated spamming."""
        mock_send_sms.return_value = True
        mock_send_email.return_value = True

        # First trigger at 8.0 BDT (below tier 10.0)
        evaluate_low_balance_alert(8.0)
        self.assertTrue(mock_send_sms.called)
        first_call_count = mock_send_sms.call_count

        # Second trigger shortly after at 7.5 BDT (same tier 10.0): should be suppressed by cooldown
        evaluate_low_balance_alert(7.5)
        self.assertEqual(mock_send_sms.call_count, first_call_count)


class PaymentLinkRoutingTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()
        from volunteers.models import Volunteer
        self.vol = Volunteer.objects.create(
            full_name="Mahmud Hasan",
            phone="01711002233",
            member_id="26100804",
            status="approved",
            payment_status="paid",
        )

    def test_route_with_short_m_parameter(self):
        """Visiting homepage with ?m=26100804 renders 200, includes donate modal and handles m parameter."""
        response = self.client.get('/?m=26100804')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('directDonateModal', content)
        self.assertIn("urlParams.get('m')", content)
        self.assertIn('data-member-id="26100804"', content)

    def test_route_with_member_id_parameter(self):
        """Visiting homepage with ?member_id=26100804 renders 200 and includes modal with member data."""
        response = self.client.get('/?member_id=26100804')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('directDonateModal', content)
        self.assertIn('data-member-id="26100804"', content)

    def test_route_with_donate_parameter(self):
        """Visiting homepage with ?donate=1 renders 200 and includes donate modal."""
        response = self.client.get('/?donate=1')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('directDonateModal', content)

    def test_route_with_invalid_member_id(self):
        """Visiting with an invalid/non-existent member ID gracefully loads page and includes alert element."""
        response = self.client.get('/?m=INVALID_NONEXISTENT_999')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('directDonateModal', content)
        self.assertIn('noMemberFoundAlert', content)


class DashboardHomeTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_dashboard_home_loads_without_unbound_local_error(self):
        """Accessing /dashboard/ by staff user calculates aggregations without UnboundLocalError for Sum."""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
