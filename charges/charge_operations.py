
from .models import Charge, ChargeSchedule
from accounting.models import CommissionPeriod
from django.db.models import Q

def new_commission_period(commission_period:CommissionPeriod):
    outstanding_charges = Charge.objects.filter(status='OPEN').all()
    for charge in outstanding_charges:
        if charge.schedule.roll_balance:
            new_charge = Charge(
                original_charge=charge,
                schedule=charge.schedule,
                outstanding_amount=charge.outstanding_amount,
                outstanding_gst=charge.outstanding_gst,
                total_amount=charge.outstanding_amount,
                total_gst=charge.outstanding_gst,
                commission_period=commission_period,
            )
            new_charge.save()
        charge.status = 'CLOSED'
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
