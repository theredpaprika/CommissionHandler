import datetime as dt
from accounting.models import CommissionPeriod
from charges.charge_operations import set_new_commission_period_charges

def new_commission_period():
    new_period = CommissionPeriod.close_and_create_new_period()
    set_new_commission_period_charges(new_period)