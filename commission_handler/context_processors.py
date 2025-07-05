import datetime as dt
from accounting.models import CommissionPeriod

def commission_period_processor(request):
    if not request.user.is_authenticated:
        return {}
    commission_period = CommissionPeriod.get_existing_period()
    is_next_month = commission_period.end_date < dt.datetime.today().date()
    return {
        'commission_period': commission_period,
        'is_next_month': is_next_month
    }