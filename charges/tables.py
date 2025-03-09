from django_tables2 import Table, Column, TemplateColumn
from .models import ChargeType, ChargeSchedule


class ChargeTypeTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'charges:type-edit' record.pk %}>Edit</a>")
    class Meta:
        model = ChargeType
        fields = ('code','name','bkge_class','bkge_class_filter','producer_filter')
        orderable = True


class ChargeScheduleTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'charges:schedule-edit' record.pk %}>Edit</a>")
    class Meta:
        model = ChargeSchedule
        fields = ['charge_type','paying_agent','receiving_agent','frequency','allow_partial_payment',
                  'roll_balance','status','priority','start_date','end_date','amount','gst']
        orderable = True
