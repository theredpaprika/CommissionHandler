from django_tables2 import Table, Column, TemplateColumn
from .models import ChargeType

class ChargeTypeTable(Table):
    class Meta:
        model = ChargeType
        fields = ('code','name','bkge_class','bkge_class_filter','producer_filter')
        orderable = True