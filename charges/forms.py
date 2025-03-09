from django import forms
from charges.models import ChargeType, ChargeSchedule


class ChargeTypeForm(forms.ModelForm):
    class Meta:
        model = ChargeType
        fields = ['code','name','bkge_class','bkge_class_filter','producer_filter']
        widgets = {'class': 'form-control'}


class ChargeScheduleForm(forms.ModelForm):
    class Meta:
        model = ChargeSchedule
        fields = ['charge_type','paying_agent','receiving_agent','frequency','allow_partial_payment',
                  'roll_balance','status','priority','start_date','end_date','amount','gst']
        widgets = {'class': 'form-control'}
