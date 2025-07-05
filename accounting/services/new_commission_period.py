from accounting.models import CommissionPeriod

def new_commission_period():
    current_period = CommissionPeriod.objects.filter(processed=False).first()
    current_period.processed = True
    CommissionPeriod.get_next_period(current_period.end_date)