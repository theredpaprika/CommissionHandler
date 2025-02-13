from django import forms
from django.forms import inlineformset_factory
from .models import (Account, Journal, Entry, AccountSubtype)


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name','account_code','account_subtype']
        widgets = {'class': 'form-control'}

    def clean(self):
        data = self.cleaned_data
        account_code = data.get('account_code')
        qs = Account.objects.filter(account_code__icontains=account_code)
        if qs.exists():
            self.add_error('account_code', f'Account code {account_code} already exists')
        return data


class AccountSubtypeForm(forms.ModelForm):
    class Meta:
        model = AccountSubtype
        fields = ['account_type','account_subtype_code','is_cumulative','is_contra', 'name', 'description']
        widgets = {'class': 'form-control'}


class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['description', 'reference']
        widgets = {'class': 'form-control'}


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['account','description','amount','notes']
        widgets = {'class':'form-control'}


class BaseJournalEntryInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        net_credits = 0.0
        for form in self.forms:
            amount = form.cleaned_data.get('amount') or 0.0
            net_credits += float(amount)
        if net_credits != 0:
            raise forms.ValidationError('Credits and Debits must total to zero!')


JournalEntryInlineFormSet = inlineformset_factory(
    Journal,
    Entry,
    form=EntryForm,
    formset=BaseJournalEntryInlineFormSet,
    min_num=2,
    extra=0,
    can_delete=True,
)


CashEntryInlineFormSet = inlineformset_factory(
    Journal,
    Entry,
    form=EntryForm,
    formset=BaseJournalEntryInlineFormSet,
    min_num=2,
    extra=0,
    can_delete=False,
)