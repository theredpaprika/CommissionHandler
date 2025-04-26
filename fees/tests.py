import os
from pathlib import Path
import datetime as dt
import calendar
from dotenv import dotenv_values

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from fees.models import Agent, Deal, Producer, DealSplit, BkgeClass, Journal, JournalDetail, CommissionPeriod

# user model
User = get_user_model()

class DotenvTestCase(TestCase):

    def setUp(self):
        # create a user
        self.user = User.objects.create_user(username='test', password='pass')
        self.client.login(username='test', password='pass')

    def test_env_file_exists_and_has_secret_key(self):
        env_path = Path(settings.BASE_DIR) / '.env'
        self.assertTrue(env_path.exists(), f".env file is missing at {env_path}")

        env_vars = dotenv_values(env_path)
        self.assertIn('SECRET_KEY', env_vars, "SECRET_KEY not found in .env file")
        self.assertTrue(env_vars['SECRET_KEY'], "SECRET_KEY is empty in .env file")

    def test_secret_key_is_loaded_into_environment(self):
        secret = os.getenv('SECRET_KEY')
        self.assertTrue(secret, "SECRET_KEY is not set in the environment")

    def test_first_commission_period_created(self):
        # check that end of this month is used as first commission period
        period = CommissionPeriod.get_current_period()
        last_day = calendar.monthrange(period.end_date.year, period.end_date.month)[1]
        self.assertEqual(period.end_date, dt.date.today().replace(day=last_day))

    def test_next_commission_period_created(self):
        # check that the next period is the end of next month, and the old period is closed off
        new_period = CommissionPeriod.close_and_create_new_period()
        old_period = CommissionPeriod.objects.get(id=1)
        self.assertEqual(old_period.processed, True)
        self.assertEqual(old_period.end_date, new_period.end_date.replace(day=1)-dt.timedelta(1))

    def test_bkge_classes_created(self):
        data = {
            'code': 'MXO',
            'name': 'Mortgage Trail Ongoing'
        }
        path = reverse('fees:bkgeclass-create')
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, 302)
        data = {
            'code': 'MXI',
            'name': 'Mortgage Upfront'
        }
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BkgeClass.objects.count(), 2)

    def test_producer_created(self):
        data = {
            'code': 'SQ1',
            'name': 'Square One',
        }
        response = self.client.post(reverse('fees:producer-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Producer.objects.count(), 1)

    def test_agent_created(self):
        # check if 'head office' agent successfully creates when submitting form
        data = {
            'agent_code': 'HO1',
            'first_name': 'Head',
            'last_name': 'Office',
            'abn': '123456782',
            'address_1': '1 Happy Street',
            'email': 'headoffice@example.com',
            'suburb': 'HAPPYLAND',
            'postcode': '12345',
            'is_gst_exempt': False,
            'is_external': False
        }
        path = reverse('fees:agent-create')
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Agent.objects.count(), 1) # HO1

        data2 = {
            'agent_code': 'JON',
            'first_name': 'John',
            'last_name': 'Doe',
            'abn': '123456782',
            'address_1': '1 Happy Street',
            'email': 'headoffice@example.com',
            'suburb': 'HAPPYLAND',
            'postcode': '12345',
            'is_gst_exempt': False,
            'is_external': False
        }
        response = self.client.post(path, data=data2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Agent.objects.count(), 2) # JON

    def test_deal_created(self):
        agent = Agent.objects.filter(agent_code='JON').first()
        data = {
            'code': 'JONUF',
            'name': 'John Upfront Only',
            'agent_id': agent.id,
        }
        path = reverse('fees:deal-create')
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Deal.objects.count(), 1)

    def test_splits_created(self):
        deal = Deal.objects.filter(code='JONUF').first()
        data = {
            'code': 'JONUF',
            'name': 'John Upfront Only',
            'agent_id': agent.id,
        }
        path = reverse('fees:deal-create')
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Deal.objects.count(), 1)