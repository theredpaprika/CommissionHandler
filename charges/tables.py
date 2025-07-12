from django_tables2 import Table, Column, TemplateColumn
from .models import ChargeType, ChargeSchedule, Charge


class ChargeTypeTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'charges:type-edit' record.pk %}>Edit</a>", orderable=False)
    class Meta:
        model = ChargeType
        fields = ('code','name','bkge_class','bkge_class_filter','producer_filter')
        orderable = True


class ChargeScheduleTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'charges:schedule-edit' record.pk %}>Edit</a>", orderable=False)
    class Meta:
        model = ChargeSchedule
        fields = ['charge_type','paying_agent','receiving_agent','frequency','allow_partial_payment',
                  'roll_balance','status','priority','start_date','end_date','amount','gst']
        orderable = True


class ChargeTable(Table):
    charge_type = Column(accessor='schedule.charge_type.name', verbose_name='Charge Type')
    priority = Column(accessor='schedule.priority', verbose_name='Priority')
    class Meta:
        model = Charge
        sequence = ('charge_type','paying_agent','receiving_agent',
                  'outstanding_amount','outstanding_gst', 'commission_period', 'priority')
        exclude = ('schedule','original_charge','id','status')
        orderable = True

