from django import forms
from charges.models import ChargeType

class ChargeTypeForm(forms.ModelForm):

    class Meta:
        model = ChargeType
        fields = ['code','name','bkge_class','bkge_class_filter','producer_filter']
        widgets = {'class': 'form-control'}