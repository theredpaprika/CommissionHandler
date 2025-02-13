from django.db import models
from django.contrib.auth import get_user_model
from accounting.models import Account
from django.db.models import Sum
from django.urls import reverse

User = get_user_model()

# Create your models here.

class Agent(models.Model):
    agent_code = models.CharField(max_length=5, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    abn = models.CharField(max_length=100)
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50)
    address_3 = models.CharField(max_length=50)
    email = models.EmailField()
    suburb = models.CharField(max_length=50)
    postcode = models.CharField(max_length=5)
    payment_account_name = models.CharField(max_length=50)
    payment_account_bsb = models.CharField(max_length=6)
    payment_account_number = models.CharField(max_length=16)
    is_gst_exempt = models.BooleanField(default=False)
    is_external = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('fees:agent-detail', args=[str(self.id)])

class Deal(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='deals')

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_absolute_url(self):
        return reverse('fees:deal-detail', args=[str(self.id)])

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Deal._meta.fields]


class DealSplit(models.Model):
    deal = models.ForeignKey('Deal', on_delete=models.CASCADE, related_name='splits')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    producer_filter = models.ForeignKey('Producer', on_delete=models.CASCADE, null=True, blank=True)
    bkge_class_filter = models.ForeignKey('BkgeClass', on_delete=models.CASCADE, null=True, blank=True)
    percentage = models.FloatField()


class Producer(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class BkgeClass(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProducerClient(models.Model):
    client_code = models.CharField(max_length=50)
    producer = models.ForeignKey('Producer', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    deal = models.ForeignKey('Deal', on_delete=models.CASCADE, null=True, blank=True, related_name='accounts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='created_clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='updated_clients')
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('client_code','producer')

    def __str__(self):
        return f"{self.client_code} - {self.name}"


class Journal(models.Model):
    period_end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100)
    reference = models.CharField(max_length=50)
    cash_amount = models.FloatField()
    cash_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    committed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1)
    pass

    def __str__(self):
        return f"{self.period_end_date} - {self.reference} - {self.description}"

    def total_credits(self):
        return self.details.all().aggregate(total=(Sum('amount')+Sum('gst')))['total']  or 0

    def get_absolute_url(self):
        return reverse('fees:journal-detail', args=[str(self.id)])


class JournalDetail(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='details')
    client_account_code = models.ForeignKey(ProducerClient, on_delete=models.CASCADE, related_name='journal_details')
    bkge_class = models.ForeignKey(BkgeClass, on_delete=models.CASCADE)
    product = models.CharField(max_length=100)
    external_adviser = models.CharField(max_length=100)
    amount = models.FloatField()
    gst = models.FloatField()
    details = models.CharField(max_length=100)
    lender_amount = models.FloatField()
    lender_gst = models.FloatField()
    balance = models.FloatField()
    limit = models.FloatField()
    pass

    def splits(self):
        return self.client_account_code.deal.splits.all()


class Entry(models.Model):
    journal_detail = models.ForeignKey(JournalDetail, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    amount = models.FloatField()
    gst = models.FloatField()
    pass

