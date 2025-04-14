from django import forms
from fees.models import Agent, Journal, Deal, DealSplit, JournalDetail, ProducerClient, BkgeClass, Producer
from django.contrib.auth import get_user_model


class FeesForm(forms.ModelForm):

    class Meta:
        model = None

    def set_field(self, field_name, value):
        if hasattr(self.instance, field_name):
            setattr(self.instance, field_name, value)


class AgentForm(FeesForm):
    field_order = ['agent_code', 'first_name', 'last_name']
    class Meta:
        model = Agent
        fields = '__all__'
        widgets = {'class':'form-control'}


class JournalForm(FeesForm):
    class Meta:
        model = Journal
        fields = ['period_end_date','description','reference','cash_amount','cash_account', 'producer']
        widgets = {'class': 'form-control'}


class JournalDetailForm(FeesForm):
    class Meta:
        model = JournalDetail
        exclude = ['related_charge','journal']
        widgets = {'class': 'form-control'}
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        self.journal = kwargs.pop('journal', None)
        producer = kwargs.pop('producer_context', None)
        super().__init__(*args, **kwargs)
        self.fields['client_account_code'].queryset = ProducerClient.objects.filter(producer=producer).all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.journal:
            instance.journal = self.journal
        if commit:
            instance.save()
        return instance


class DealForm(FeesForm):
    class Meta:
        model = Deal
        fields = ['code','name']
        widgets = {'class': 'form-control'}


class DealSplitForm(FeesForm):
    class Meta:
        model = DealSplit
        fields = ['agent', 'percentage', 'producer_filter', 'bkge_class_filter']
        widgets = {'class': 'form-control'}


class ProducerClientForm(FeesForm):
    class Meta:
        model = ProducerClient
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at']
        widgets = {'class': 'form-control'}


class BkgeClassForm(FeesForm):
    class Meta:
        model = BkgeClass
        fields = ['code','name']
        widgets = {'class': 'form-control'}


class ProducerForm(FeesForm):
    class Meta:
        model = Producer
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

