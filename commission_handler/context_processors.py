from accounting.models import CommissionPeriod

def commission_period_processor(request):
    if not request.user.is_authenticated:
        return {}
    commission_period = CommissionPeriod.get_current_period()
    return {
        'commission_period': commission_period
    }