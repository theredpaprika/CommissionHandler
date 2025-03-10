from django import forms
from fees.models import Agent, Journal, Deal, DealSplit, JournalDetail, ProducerClient, BkgeClass
from django.contrib.auth import get_user_model

class AgentForm(forms.ModelForm):
    field_order = ['agent_code', 'first_name', 'last_name']
    class Meta:
        model = Agent
        fields = '__all__'
        widgets = {'class':'form-control'}


class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['period_end_date','description','reference','cash_amount','cash_account', 'producer']
        widgets = {'class': 'form-control'}


class JournalDetailForm(forms.ModelForm):
    class Meta:
        model = JournalDetail
        exclude = ['journal']
        widgets = {'class': 'form-control'}
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        producer = kwargs.pop('producer_context', None)
        print(producer)
        super().__init__(*args, **kwargs)
        self.fields['client_account_code'].queryset = ProducerClient.objects.filter(producer=producer).all()

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['code','name']
        widgets = {'class': 'form-control'}


class DealSplitForm(forms.ModelForm):
    class Meta:
        model = DealSplit
        fields = ['agent', 'percentage', 'producer_filter', 'bkge_class_filter']
        widgets = {'class': 'form-control'}


class ProducerClientForm(forms.ModelForm):
    class Meta:
        model = ProducerClient
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at']
        widgets = {'class': 'form-control'}


class BkgeClassForm(forms.ModelForm):
    class Meta:
        model = BkgeClass
        fields = ['code','name']
        widgets = {'class': 'form-control'}


class DeleteConfirmForm(forms.Form):
    confirm = forms.BooleanField(required=True)


class UploadFileForm(forms.Form):
    file = forms.FileField()


class JournalCommitConfirmForm(forms.ModelForm):

    confirm = forms.BooleanField(required=True)

    class Meta:
        model = Journal
        fields = []
        widgets = {'class': 'form-control'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        journal = self.instance
        _accounts_missing_deals = journal.details.filter(client_account_code__deal__isnull=True)
        if len(_accounts_missing_deals) > 0:
            raise forms.ValidationError('Some client account codes are missing deals.')
        if (journal.cash_amount - journal.total_credits() != 0):
            raise forms.ValidationError('Debits do not equal credits')
        return cleaned_data

