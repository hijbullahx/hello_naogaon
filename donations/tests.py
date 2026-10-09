from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.core.cache import cache
from donations.models import ProgramDonation, FinancialTransaction
from donations.views import process_successful_payment
from donations.donation_notifications import notify_donor_donation_approved

class PaymentProcessingIdempotencyTests(TestCase):
    def setUp(self):
        cache.clear()
        self.donation = ProgramDonation.objects.create(
            donor_name="Karim Khan",
            donor_phone="01711998877",
            amount=Decimal("500.00"),
            payment_method="bKash",
            tran_id="HN_TEST_TXN_001",
            trx_id="TRX987654321",
            status="initiated",
            donation_type="general",
        )

    @patch('donations.donation_notifications.notify_donor_donation_approved')
    def test_process_successful_payment_first_run(self, mock_notify):
        """First call approves donation, creates exactly one FinancialTransaction, triggers notification on commit."""
        payment_data = {
            'transaction_id': 'TRX987654321',
            'payment_method': 'bKash',
            'amount': '500.00'
        }
        with self.captureOnCommitCallbacks(execute=True):
            result = process_successful_payment(
                donation=self.donation,
                payment_data=payment_data
            )

        self.assertEqual(result.status, 'approved')
        self.assertEqual(result.amount, Decimal('500.00'))
        self.assertTrue(mock_notify.called)

        # Verify ledger has exactly 1 entry
        ledger_count = FinancialTransaction.objects.filter(donation=self.donation).count()
        self.assertEqual(ledger_count, 1)

    @patch('donations.donation_notifications.notify_donor_donation_approved')
    def test_process_successful_payment_underpayment_rejected(self, mock_notify):
        """Underpayment in gateway callback must be rejected without creating ledger or approving donation."""
        payment_data = {
            'transaction_id': 'TRX987654321',
            'payment_method': 'bKash',
            'amount': '100.00'  # Expected 500.00, received only 100.00
        }
        with self.captureOnCommitCallbacks(execute=True):
            result = process_successful_payment(
                donation=self.donation,
                payment_data=payment_data
            )

        # Status must NOT be approved
        self.assertEqual(result.status, 'initiated')
        self.assertFalse(mock_notify.called)
        # Ledger must remain 0
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 0)

    @patch('donations.donation_notifications.notify_donor_donation_approved')
    def test_process_successful_payment_missing_or_malformed_amount_rejected(self, mock_notify):
        """Missing or malformed payment amount must be rejected without approval."""
        payment_data_malformed = {
            'transaction_id': 'TRX987654321',
            'payment_method': 'bKash',
            'amount': 'corrupt_amount'
        }
        result = process_successful_payment(self.donation, payment_data_malformed)
        self.assertEqual(result.status, 'initiated')
        self.assertFalse(mock_notify.called)
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 0)

    @patch('donations.donation_notifications.notify_donor_donation_approved')
    def test_duplicate_callback_idempotency(self, mock_notify):
        """Second call for already-approved donation is a safe no-op (no duplicate ledger, no duplicate notifications)."""
        payment_data = {
            'transaction_id': 'TRX987654321',
            'payment_method': 'bKash',
            'amount': '500.00'
        }
        # First execution
        with self.captureOnCommitCallbacks(execute=True):
            process_successful_payment(
                donation=self.donation,
                payment_data=payment_data
            )
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 1)
        mock_notify.reset_mock()

        # Second duplicate callback:
        with self.captureOnCommitCallbacks(execute=True):
            second_result = process_successful_payment(
                donation=self.donation,
                payment_data=payment_data
            )

        self.assertEqual(second_result.status, 'approved')
        # Ledger MUST still be exactly 1
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 1)
        # Notifications MUST NOT be dispatched again
        self.assertFalse(mock_notify.called)


class PaymentSuccessEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()
        self.donation = ProgramDonation.objects.create(
            donor_name="Hasan Ali",
            donor_phone="01712345678",
            amount=Decimal("500.00"),
            payment_method="Online Gateway",
            tran_id="HN_PS_TXN_500",
            status="initiated",
            donation_type="general",
        )

    def test_payment_success_without_identifier_rejects_gracefully(self):
        """Missing transaction identifier should redirect to error rather than approving an arbitrary record."""
        response = self.client.get('/donations/payment-success/')
        self.assertNotEqual(response.status_code, 500)
        # Ensure donation remains unapproved
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'initiated')

    @patch('donations.views.verify_paystation_payment')
    def test_payment_success_paystation_underpayment_rejected(self, mock_verify):
        """PayStation callback with amount less than expected must be rejected."""
        mock_verify.return_value = {
            'status_code': '200',
            'data': {
                'trx_status': 'success',
                'payment_amount': '50.00',  # Underpayment! Expected 500.00
                'trx_id': 'PS_TRX_9999',
                'payment_method': 'bkash'
            }
        }
        response = self.client.get(f'/donations/payment-success/?invoice_number=HN_PS_TXN_500')
        self.assertEqual(response.status_code, 302)
        self.donation.refresh_from_db()
        # Donation must NOT be approved
        self.assertEqual(self.donation.status, 'initiated')
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 0)

    @patch('donations.views.verify_paystation_payment')
    @patch('donations.donation_notifications.send_sms')
    def test_payment_success_paystation_valid_amount_approved(self, mock_sms, mock_verify):
        """PayStation callback with valid matching amount approves donation and records transaction."""
        mock_verify.return_value = {
            'status_code': '200',
            'data': {
                'trx_status': 'success',
                'payment_amount': '500.00',  # Valid matching amount
                'trx_id': 'PS_TRX_9999',
                'payment_method': 'bkash'
            }
        }
        response = self.client.get(f'/donations/payment-success/?invoice_number=HN_PS_TXN_500')
        self.assertEqual(response.status_code, 302)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'approved')
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 1)


class DonationDebounceTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    @patch('donations.donation_notifications.notify_admin_new_manual_donation')
    @patch('donations.donation_notifications.notify_donor_manual_submission')
    def test_manual_donation_duplicate_debounce(self, mock_notify_donor, mock_notify_admin):
        """Submitting identical manual payment within 60s is debounced."""
        post_data = {
            'donor_name': 'Hasan Ali',
            'donor_phone': '01712345678',
            'amount': '200',
            'payment_mode': 'manual',
            'manual_channel': 'bKash',
            'sender_account': '01712345678',
            'trx_id': 'TRX1234567890',
            'donor_identity_type': 'general',
        }
        # First submission
        resp1 = self.client.post('/donations/initiate-payment/', data=post_data)
        self.assertEqual(ProgramDonation.objects.filter(donor_phone='01712345678').count(), 1)

        # Immediate identical resubmission within 60s
        resp2 = self.client.post('/donations/initiate-payment/', data=post_data)
        # Should NOT create a second duplicate donation record
        self.assertEqual(ProgramDonation.objects.filter(donor_phone='01712345678').count(), 1)


class DonationSMSTemplateLengthTests(TestCase):
    @patch('donations.donation_notifications.send_sms')
    def test_approval_sms_length_within_two_segments(self, mock_send_sms):
        """General donation approval SMS must be <= 134 chars (2 segments UCS-2)."""
        donation = ProgramDonation(
            id=12,
            donor_name="হাসান মাহমুদ",
            donor_phone="01711223344",
            amount=Decimal("1000.00"),
            payment_method="bKash",
            trx_id="TXN12345678",
            tran_id="HN12",
            status="approved",
            donation_type="general",
        )
        notify_donor_donation_approved(donation)
        self.assertTrue(mock_send_sms.called)
        sent_sms = mock_send_sms.call_args[0][1]
        # Must fit within 2 segments (<= 134 chars UCS-2)
        self.assertLessEqual(len(sent_sms), 134)


class PayStationIPNVerificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()
        self.donation = ProgramDonation.objects.create(
            donor_name="Karim Khan",
            donor_phone="01712998877",
            amount=Decimal("500.00"),
            payment_method="PayStation",
            tran_id="HN_PS_IPN_500",
            status="initiated",
            donation_type="general",
        )

    @patch('donations.views.verify_paystation_payment')
    @patch('donations.donation_notifications.send_sms')
    def test_paystation_ipn_valid_server_verification_approves(self, mock_sms, mock_verify):
        """PayStation IPN verifies transaction with server-side status API and approves donation."""
        mock_verify.return_value = {
            'status_code': '200',
            'data': {
                'trx_status': 'success',
                'payment_amount': '500.00',
                'trx_id': 'PS_TRX_REAL_888',
                'payment_method': 'bkash',
            }
        }
        ipn_payload = {
            'invoice_number': 'HN_PS_IPN_500',
            'trx_status': 'success',
        }
        response = self.client.post('/donations/payment-ipn/', data=ipn_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'success')
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'approved')
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 1)

    @patch('donations.views.verify_paystation_payment')
    def test_paystation_ipn_fake_payload_rejected_by_server_verification(self, mock_verify):
        """Forged IPN payload that fails server-side verification must be rejected."""
        mock_verify.return_value = {
            'status_code': '400',
            'status': 'failed',
            'message': 'Transaction not found or invalid merchant',
        }
        ipn_payload = {
            'invoice_number': 'HN_PS_IPN_500',
            'trx_status': 'success',  # Attacker claims success in payload
        }
        response = self.client.post('/donations/payment-ipn/', data=ipn_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('status'), 'rejected')
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'initiated')
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 0)

    @patch('donations.views.verify_paystation_payment')
    def test_paystation_ipn_underpayment_rejected(self, mock_verify):
        """Underpayment reported by PayStation server must be rejected with 400."""
        mock_verify.return_value = {
            'status_code': '200',
            'data': {
                'trx_status': 'success',
                'payment_amount': '250.00',  # Underpaid! Expected 500.00
                'trx_id': 'PS_TRX_UNDER',
                'payment_method': 'bkash',
            }
        }
        ipn_payload = {
            'invoice_number': 'HN_PS_IPN_500',
            'trx_status': 'success',
        }
        response = self.client.post('/donations/payment-ipn/', data=ipn_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('status'), 'rejected')
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'initiated')
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 0)

    @patch('donations.views.verify_paystation_payment')
    def test_paystation_ipn_retried_idempotency(self, mock_verify):
        """Retrying PayStation IPN for an already approved donation is a safe no-op."""
        mock_verify.return_value = {
            'status_code': '200',
            'data': {
                'trx_status': 'success',
                'payment_amount': '500.00',
                'trx_id': 'PS_TRX_IDEMP',
                'payment_method': 'bkash',
            }
        }
        ipn_payload = {'invoice_number': 'HN_PS_IPN_500'}

        # First call
        resp1 = self.client.post('/donations/payment-ipn/', data=ipn_payload)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 1)

        # Retry IPN call
        resp2 = self.client.post('/donations/payment-ipn/', data=ipn_payload)
        self.assertEqual(resp2.status_code, 200)
        # Financial ledger count remains exactly 1
        self.assertEqual(FinancialTransaction.objects.filter(donation=self.donation).count(), 1)
