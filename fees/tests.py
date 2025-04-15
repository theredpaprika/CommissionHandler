
import datetime as dt
import calendar

from django.test import TestCase
from django.urls import reverse
from tenants.models import User
from fees.models import Agent, Deal, Producer, DealSplit, BkgeClass, Journal, JournalDetail, CommissionPeriod


# Create your tests here.

class AgentTestCase(TestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(username='test', password='pass')

        # producers
        self.producer = Producer.objects.create(name='SQ1', code='SQ1')

        # bkge classes
        self.mxi = BkgeClass.objects.create(name='MXI', code='MXI')
        self.mxo = BkgeClass.objects.create(name='MXO', code='MXO')

        # deals
        self.bob_deal = Deal.objects.create(code='BOB', name='Bob Only', agent=self.bob)
        self.jane_deal = Deal.objects.create(code='JANE', name='Jane Only', agent=self.jane)
        self.bob_uftr_deal = Deal.objects.create(code='BUF60', name='Bob 60UF-80TR', agent=self.bob)
        self.bob_sq1_deal = Deal.objects.create(code='BSQ1', name='Bob SQ1 Special', agent=self.bob)

        # splits
        DealSplit.objects.create(agent=self.ho, percentage=40, deal=self.bob_uftr_deal, bkge_class_filter=self.mxi)
        DealSplit.objects.create(agent=self.ho, percentage=20, deal=self.bob_uftr_deal)
        DealSplit.objects.create(agent=self.ho, percentage=50, deal=self.bob_sq1_deal, producer_filter=self.producer)

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




