
import datetime as dt
import calendar


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from fees.models import Agent, Deal, Producer, DealSplit, BkgeClass, Journal, JournalDetail, CommissionPeriod


# Create your tests here.
User = get_user_model()


class AgentTestCase(TestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(username='test', password='pass')

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

    def test_agent_created(self):
        self.client.login(username='test', password='pass')
        data = {
            'agent_code': 'HO1',
            'first_name': 'Head',
            'last_name': 'Office',
            'is_gst_exempt': False
        }
        path = reverse('fees:agent-create')
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Agent.objects.count(), 1) # HO1




