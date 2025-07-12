from django.db import models
from django.db.models import GeneratedField

from fees.models import BkgeClass, Agent, Producer
from accounting.models import CommissionPeriod

# Create your models here.

class ChargeType(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    bkge_class = models.ForeignKey(BkgeClass, on_delete=models.CASCADE, related_name='charge_types')
    producer_filter = models.ForeignKey(Producer, on_delete=models.CASCADE, null=True, blank=True)
    bkge_class_filter = models.ForeignKey(
        BkgeClass, on_delete=models.CASCADE, related_name='charge_types_bkge_filter', null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class ChargeSchedule(models.Model):
    charge_type = models.ForeignKey(ChargeType, on_delete=models.CASCADE, related_name='schedules')
    paying_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='paying_schedules')
    receiving_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='receiving_schedules')
    frequency = models.CharField(max_length=10)
    allow_partial_payment = models.BooleanField()
    roll_balance = models.BooleanField()
    status = models.CharField(max_length=10)
    priority = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    amount = models.FloatField()
    gst = models.FloatField()

    def __str__(self):
        return f"{self.charge_type}: {self.paying_agent} > {self.receiving_agent}"


class Charge(models.Model):
    commission_period = models.ForeignKey(CommissionPeriod, on_delete=models.CASCADE, related_name='charges', null=True, blank=True, default=None)
    original_charge = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None)
    schedule = models.ForeignKey(ChargeSchedule, on_delete=models.CASCADE, related_name='charges')
    paying_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='paying_charges')
    receiving_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='receiving_charges')
    #total_amount = models.FloatField()
    #total_gst = models.FloatField()
    outstanding_amount = models.FloatField()
    outstanding_gst = models.FloatField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.schedule}: outstanding={self.outstanding_amount}, status={self.status}"

    def is_renewable(self):
        return self.status == 'OPEN' and self.schedule.roll_balance