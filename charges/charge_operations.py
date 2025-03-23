
from .models import Charge, ChargeSchedule
from accounting.models import CommissionPeriod, Entry
from django.db.models import Q


def new_commission_period(commission_period:CommissionPeriod):
    # close out any outstanding charges that are not being rolled over
    outstanding_charges = Charge.objects.filter(status='OPEN').all().order_by(
        'schedule__paying_agent',
        'commission_period__id',
        'schedule__priority'
    )
    for charge in outstanding_charges:
        if not charge.schedule.roll_balance:
            charge.status = 'CLOSED'
            continue

    # get list of active charge schedules and create charge items for the new commission month
    schedules = (ChargeSchedule.objects.filter(
        ~Q(start_date__gte=commission_period.end_date)&~Q(end_date__lte=commission_period.end_date),
        status='OPEN').all())
    for schedule in schedules:
        new_charge = Charge(
                original_charge=None,
                schedule=schedule,
                outstanding_amount=schedule.amount,
                outstanding_gst=schedule.gst,
                total_amount=schedule.amount,
                total_gst=schedule.gst,
                commission_period=commission_period,
        )
        new_charge.save()


def process_outstanding_charges(commission_period:CommissionPeriod):
    outstanding_charges = Charge.objects.filter(status='OPEN').all().order_by(
        'schedule__paying_agent',
        'commission_period__id',
        'schedule__priority'
    )
