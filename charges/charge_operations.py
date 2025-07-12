
from .models import Charge, ChargeSchedule
from accounting.models import CommissionPeriod, Entry
from django.db.models import Q


def set_new_commission_period_charges(commission_period:CommissionPeriod):
    close_off_or_roll_outstanding_charges(commission_period)
    add_scheduled_charges(commission_period)


def get_outstanding_charges():
    outstanding_charges = Charge.objects.filter(
        status='OPEN'
        ).all().order_by(
        'schedule__paying_agent',
        'commission_period__id',
        'schedule__priority'
    )
    return outstanding_charges


def close_off_or_roll_outstanding_charges(commission_period:CommissionPeriod):
    outstanding_charges = get_outstanding_charges()
    for charge in outstanding_charges:
        if charge.schedule.roll_balance:
            new_charge = Charge(
                original_charge=charge,
                schedule=charge.schedule,
                outstanding_amount=charge.outstanding_amount,
                outstanding_gst=charge.outstanding_gst,
                receiving_agent=charge.receiving_agent,
                paying_agent=charge.paying_agent,
                commission_period=commission_period,
                status='OPEN'
            )
            new_charge.save()
        charge.status = 'DEFERRED'
        charge.save()


def add_scheduled_charges(commission_period:CommissionPeriod):
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
                receiving_agent=schedule.receiving_agent,
                paying_agent=schedule.paying_agent,
                commission_period=commission_period,
                status='OPEN'
        )
        new_charge.save()
