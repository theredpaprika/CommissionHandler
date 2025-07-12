from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Account, Journal, Entry, AccountSubtype
from .forms import AccountForm, JournalForm, JournalEntryInlineFormSet, AccountSubtypeForm, CashEntryInlineFormSet
from .services.new_commission_period import new_commission_period



#TODO: CONSIDER DELETING THE BELOW

@login_required
def new_commission_period_view(request):
    new_commission_period()
    return redirect('home')


@login_required
def account_create_view(request, id=None):
    template = 'accounting/account_create.html'
    form = AccountForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        obj = form.save()
        return redirect('accounting:accounts')
    return render(request, template, context=context)


@login_required
def account_search_view(request):
    template = 'accounting/account_search.html'
    objs = Account.objects.all()
    context = {'objs': objs}
    return render(request, template, context=context)


@login_required
def account_view(request, account_code):
    template = 'accounting/account.html'
    account = Account.objects.filter(account_code=account_code).first()
    entries = account.entries.all()
    context = {'entries': entries, 'acc': account}
    return render(request, template, context=context)


@login_required
def journal_search_view(request):
    template = 'accounting/journal_search.html'
    objs = Journal.objects.all()
    context = {'objs': objs}
    return render(request, template, context=context)


@login_required
def journal_view(request, id=None):
    template = 'accounting/journal.html'
    journal = Journal.objects.get(pk=id)
    entries = journal.entries.all()
    context = {'objs': entries}
    return render(request, template, context=context)


@login_required
def journal_create_view(request, id=None):
    template = 'accounting/journal_create.html'
    form = JournalForm(request.POST or None)
    formset = JournalEntryInlineFormSet(request.POST or None, instance=form.instance)
    context = {'form': form, 'formset': formset}
    if form.is_valid() and formset.is_valid():
        print('submitted')
        main_form = form.save()
        formset_instances = formset.save(commit=False)
        for instance in formset_instances:
            print(instance)
            instance.main_form = main_form
        formset.save()
        return redirect('accounting:journals')
    else:
        print('form',form.error_class)
        print('formset',formset.error_messages)
    return render(request, template, context=context)


@login_required
def journal_create_cash_topup_view(request, id=None):
    template = 'accounting/cash_create.html'
    form = JournalForm(request.POST or None)
    formset = CashEntryInlineFormSet(request.POST or None, instance=form.instance)
    formset[0].fields['account'].queryset = Account.objects.filter(account_subtype__account_subtype_code='CASH')
    formset[1].fields['account'].queryset = Account.objects.filter(account_subtype__account_subtype_code='SUSPENSE')

    context = {'form': form, 'formset': formset}
    if form.is_valid() and formset.is_valid():
        print('submitted')
        main_form = form.save()
        formset_instances = formset.save(commit=False)
        for instance in formset_instances:
            print(instance)
            instance.main_form = main_form
        formset.save()
        return redirect('accounting:journals')
    else:
        print('form',form.error_class)
        print('formset',formset.error_messages)
    return render(request, template, context=context)


@login_required
def account_subtype_create_view(request, id=None):
    template = 'accounting/account_subtype_create.html'
    form = AccountSubtypeForm(request.POST or None)
    subtypes = AccountSubtype.objects.all()
    context = {'form': form, 'subtypes':subtypes}
    if form.is_valid():
        obj = form.save()
        return redirect('home')
    return render(request, template, context=context)
