from typing import Any
import datetime as dt

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django_tables2 import SingleTableView, MultiTableMixin, SingleTableMixin
from django.urls import reverse_lazy, reverse

from .models import Agent, Journal, Deal, DealSplit, ProducerClient, JournalDetail, Producer, Entry, BkgeClass
from .forms import (AgentForm, JournalForm, DealForm, DealSplitForm, JournalDetailForm, BkgeClassForm,
                    ProducerClientForm, DeleteConfirmForm, UploadFileForm, JournalCommitConfirmForm, ProducerForm)
from .tables import (AgentTable, DealTable, DealSplitTable, JournalTable,
                     ProducerClientTable, JDTable, BkgeClassTable, ProducerTable)
from accounting.models import CommissionPeriod
from .filters import ProducerClientFilter

from files import file_manager

from django.contrib import messages


# Create your views here.

@login_required
def agent_search_view(request):
    template = 'fees/agent_search.html'
    objs = Agent.objects.all()
    context = {'objs': objs}
    return render(request, template, context=context)

@login_required
def agent_create_view(request, agent_code=None):
    template = 'fees/agent_create.html'
    instance = get_object_or_404(Agent, agent_code=agent_code) if agent_code else None
    form = AgentForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        obj = form.save()
        return redirect('fees:agents')
    else:
        print(form.errors)
    return render(request, template, context=context)


@login_required
def agent_view(request, agent_code=None):
    template = 'fees/agent.html'
    agent = Agent.objects.get(agent_code=agent_code)
    deals = agent.deals.all()
    clients = ProducerClient.objects.filter(deal__agent=agent)
    context = {'agent': agent, 'deals': deals, 'clients': clients}
    return render(request, template, context)


@login_required
def journals_search_view(request, context=None):
    template = 'fees/journals_search.html'
    objs = Journal.objects.filter(status='open').all()
    if not context:
        context = {}
        context['notify'] = ''
    context['objs'] = objs
    return render(request, template, context=context)


@login_required
def journals_create_view(request, journal_id=None):
    template = 'fees/journals_create.html'
    instance = Journal.objects.get(id=journal_id) if journal_id else None
    form = JournalForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        if journal_id is None:
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.status = 'open'
            obj.save()
        else:
            obj = form.save()
        return redirect('fees:mjournals')
    else:
        print(form.errors)
    return render(request, template, context=context)


@login_required
def journal_detail_create_view(request, journal_id, id=None):
    template = 'fees/journal_detail_create.html'
    instance = get_object_or_404(JournalDetail, id=id) if id else None
    journal = Journal.objects.get(id=journal_id)
    form = JournalDetailForm(journal_item=journal, data=request.POST or None, instance=instance)
    context = {'form': form, 'journal': journal}
    if form.is_valid():
        if id is None:
            obj = form.save(commit=False)
            obj.journal = journal
            obj = form.save()
        else:
            obj = form.save()
        return redirect('fees:mjournal', journal_id=journal_id)
    else:
        print(form.errors)
    return render(request, template, context=context)


@login_required
def journal_view(request, journal_id):
    template = 'fees/journal.html'
    journal = Journal.objects.get(id=journal_id)
    credits = journal.total_credits()
    objs = journal.details.all()
    context = {'objs': objs, 'journal': journal, 'credits': credits}
    return render(request, template, context=context)



#TODO
# create a commit journal form with validation in the clean method
# must ensure all accounts have been assigned to a deal, and if not, redirect
@login_required
def journal_commit_view(request, journal_id):
    template = 'fees/journal_commit.html'
    journal = Journal.objects.get(id=journal_id)
    form = JournalCommitConfirmForm(request.POST or None, instance=journal)
    context = {'form': form}
    if form.is_valid():
        journal.status = 'closed'
        execute_commit_journal(journal)
        journal.save()
        return redirect('fees:mjournals')

    return render(request, template, context=context)


@login_required
def journal_delete_view(request, journal_id):
    template = 'fees/delete_template.html'
    journal = Journal.objects.get(id=journal_id)
    form = DeleteConfirmForm(request.POST or None)
    context = {'form': form, 'obj': journal}
    if form.is_valid():
        if form.cleaned_data['confirm']:
            journal.delete()
        return redirect('fees:mjournals')
    return render(request, template, context=context)


@login_required
def journal_detail_delete_view(request, journal_id, detail_id):
    template = 'fees/delete_template.html'
    journal_detail = JournalDetail.objects.get(id=detail_id)
    form = DeleteConfirmForm(request.POST or None)
    context = {'form': form, 'obj': journal_detail}
    if form.is_valid():
        if form.cleaned_data['confirm']:
            journal_detail.delete()
        return redirect('fees:mjournal', journal_id=journal_id)
    return render(request, template, context=context)


@login_required
def deals_search_view(request, agent_code):
    template = 'fees/deals_search.html'
    agent = Agent.objects.get(agent_code=agent_code)
    objs = agent.deals.all()
    context = {'objs': objs}
    return render(request, template, context=context)


@login_required
def deals_create_view(request, agent_code, deal_code=None):
    template = 'fees/deals_create.html'
    instance = get_object_or_404(Deal, code=deal_code) if deal_code else None
    form = DealForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        if not deal_code:
            obj = form.save(commit=False)
            obj.agent = Agent.objects.get(agent_code=agent_code)
            obj.save()
        else:
            obj = form.save()
        return redirect('fees:agent', agent_code=agent_code)
    return render(request, template, context=context)

"""
@login_required
def deal_view(request, agent_code, deal_code):
    template = 'fees/x_deal.html'
    agent = Agent.objects.get(agent_code=agent_code)
    deal = Deal.objects.get(code=deal_code)
    splits = deal.splits.all()
    context = {'splits': splits, 'deal':deal, 'agent': agent }
    return render(request, template, context=context)
"""

@login_required
def split_create_view(request, agent_code, deal_code, split_id=None):
    template = 'fees/split_create.html'
    instance = get_object_or_404(DealSplit, id=split_id) if split_id else None
    agent = Agent.objects.get(agent_code=agent_code)
    deal = Deal.objects.get(code=deal_code)
    form = DealSplitForm(request.POST or None, instance=instance)
    context = {'form': form, 'deal': deal, 'agent': agent}
    if form.is_valid():
        if not split_id:
            obj = form.save(commit=False)
            obj.deal = deal
            obj.save()
        else:
            obj = form.save()
        return redirect('fees:deal', agent_code=agent_code, deal_code=deal_code)
    return render(request, template, context=context)

@login_required
def client_create_view(request, agent_code=None, client_id=None):
    template = 'fees/client_create.html'
    if agent_code:
        agent = Agent.objects.get(agent_code=agent_code)
        deals = agent.deals.all()
    else:
        deals = Deal.objects.all()
    instance = get_object_or_404(ProducerClient, id=client_id) if client_id else None
    form = ProducerClientForm(request.POST or None, instance=instance)
    form.fields['deal'].queryset = deals
    context = {'form': form}
    if form.is_valid():
        if client_id is None:
            obj = form.save(commit=False)
            obj.save()
        else:
            obj = form.save()
        return redirect('home')
    return render(request, template, context=context)


@login_required
def client_edit_view(request, client_code):
    template = 'fees/client_create.html'
    instance = get_object_or_404(ProducerClient, client_code=client_code)
    form = ProducerClientForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        obj = form.save()
        return redirect('fees:clients')
    return render(request, template, context=context)


@login_required
def client_search_view(request):
    template = 'fees/producer_clients_search.html'
    objs = ProducerClient.objects.all()
    context = {
        'unallocated_clients': objs.filter(deal__isnull=True),
        'allocated_clients': objs.filter(deal__isnull=False)
    }
    return render(request, template, context=context)


def check_unallocated_accounts(account_list: list, producer: Producer):
    """
    Checks a list of producer client accounts (account_list) against ProducerClient.client_code
    and returns a subset of producer client accounts that are not in the database.

    example:
    If ProducerClient contains accounts: ['100', '101', '102'] under producer "ABC":
    check_unallocated_accounts(['100', '101', '102', '103'], "ABC") returns ['103']
    """
    # get list from db filtered by account list provided
    _existing_clients = (
        ProducerClient
        .objects
        .filter(
            producer=producer,
            client_code__in=account_list
        )
        .all()
        .values_list('client_code', flat=True)
    )
    return list(set(account_list) - set(_existing_clients))


def execute_commit_journal(journal: Journal):
    assert journal.status == 'closed'
    """
    logic for calculating revenue splits on details associated with a committed journal
    :param journal: 
    :return: 
    """
    fees = []
    for detail in journal.details.all():
        fees = fees + entries_from_journal_detail(detail)
    for fee in fees:
        fee.save()


#TODO
# handling percentage sums over 100%
def entries_from_journal_detail(detail: JournalDetail):

    entries = []
    percentage_sum = 0
    splits = detail.splits()

    for split in splits:
        gst_exempt = split.agent.is_gst_exempt
        producer_filter = split.producer_filter
        if split.bkge_class_filter and split.bkge_class_filter != detail.bkge_class:
            continue
        if split.producer_filter and split.producer_filter != detail.journal.producer:
            continue
        percentage_sum += split.percentage
        entries.append(
            Entry(
                journal_detail=detail,
                agent=split.agent,
                amount=detail.amount * split.percentage / 100,
                gst=detail.gst * split.percentage / 100
            )
        )

    if percentage_sum < 100:
        entries.append(
            Entry(
                journal_detail=detail,
                agent=detail.client_account_code.deal.agent,
                amount=detail.amount * (100 - percentage_sum) / 100,
                gst=detail.gst * (100 - percentage_sum) / 100
            )
        )

    return entries


#*****************************************************************************
# CLASS BASED VIEWS
#*****************************************************************************


# LIST VIEWS **************************************************************************************

class FeesListView(SingleTableView):
    template_name = 'single_table_template.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super(FeesListView, self).get_context_data(**kwargs)
        context.update(self.context_data)
        return context


@method_decorator(login_required, name="dispatch")
class AgentListView(FeesListView):
    model = Agent
    table_class = AgentTable
    context_data = {
        'create_link': reverse_lazy('fees:agent-create'),
        'title': 'Agents'
    }


@method_decorator(login_required, name="dispatch")
class ProducerClientListView(TemplateView):
    template_name = 'fees/producer_clients_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unassigned_clients = ProducerClient.objects.filter(deal=None).all()
        clients_qs = ProducerClient.objects.filter(deal__isnull=False).all()
        client_filter = ProducerClientFilter(self.request.GET, queryset=clients_qs)
        context['title'] = 'Producer Clients'
        context['unassigned_clients_table'] = ProducerClientTable(unassigned_clients)
        context['client_filter'] = client_filter
        context['clients_table'] = ProducerClientTable(client_filter.qs)
        context['create_link'] = reverse('fees:client-create')
        return context


@method_decorator(login_required, name="dispatch")
class DealListView(FeesListView):
    model = Deal
    table_class = DealTable
    context_data = {
        'create_link': reverse_lazy('fees:deal-create'),
        'title': 'Agents'
    }

@method_decorator(login_required, name="dispatch")
class JournalListView(FeesListView):
    model = Journal
    table_class = JournalTable
    context_data = {
        'create_link': reverse_lazy('fees:journal-create'),
        'title': 'Journals'
    }

@method_decorator(login_required, name="dispatch")
class BkgeClassListView(FeesListView):
    model = BkgeClass
    table_class = BkgeClassTable
    context_data = {
        'create_link': reverse_lazy('fees:bkgeclass-create'),
        'title': 'Brokerage Classes'
    }

@method_decorator(login_required, name="dispatch")
class ProducerListView(FeesListView):
    model = Producer
    table_class = ProducerTable
    context_data = {
        'create_link': reverse_lazy('fees:producer-create'),
        'title': 'Producer'
    }


# DETAIL VIEWS **************************************************************************************

# view agent
@method_decorator(login_required, name="dispatch")
class AgentDetailView(SingleTableMixin, DetailView):
    model = Agent
    context_object_name = 'agent'
    context_table_name = 'table'
    template_name = 'fees/agent_detail.html'
    table_class = DealTable

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['table_heading'] = 'Deals'
        context['title'] = f'Agent {self.object}'
        context['create_link'] = reverse('fees:deal-create', kwargs={'agent_id':self.object.id}  )
        return context

    def get_table_data(self):
        return self.object.deals.all()


# view deal
@method_decorator(login_required, name="dispatch")
class DealDetailView(SingleTableMixin, DetailView):
    model = Deal
    context_object_name = 'deal'
    context_table_name = 'table'
    template_name = 'fees/deal_detail.html'
    table_class = DealSplitTable

    def get_context_data(self, **kwargs):
        context = super(DealDetailView, self).get_context_data(**kwargs)
        context['table_heading'] = 'Splits'
        context['title'] = f'Deal {self.object}'
        context['create_link'] = reverse('fees:split-create', kwargs={'deal_id':self.object.id}  )
        return context

    def get_table_data(self):
        return self.object.splits.all()


@method_decorator(login_required, name="dispatch")
class JournalDetailView(SingleTableMixin, DetailView):
    model = Journal
    context_object_name = 'journal'
    context_table_name = 'table'
    template_name = 'fees/journal_detail.html'
    table_class = JDTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_heading'] = 'Journal Details'
        context['title'] = f'Journal {self.object}'
        context['create_link'] = reverse('fees:jd-create', kwargs={'journal_id':self.object.id}  )
        context['upload_link'] = reverse('fees:journal-upload', kwargs={'pk':self.object.id}  )
        return context

    def get_table_data(self):
        return self.object.details.all()


# UPDATE VIEWS **************************************************************************************

class FeesUpdateView(UpdateView):
    related_field = None
    success_url_name = None
    template_name = 'single_form_template.html'

    def get_success_url(self):
        if not self.related_field:
            return reverse_lazy(self.success_url_name)
        related_object = getattr(self.object, self.related_field)
        return reverse(self.success_url_name, kwargs={'pk': related_object.id})


@method_decorator(login_required, name="dispatch")
class ProducerClientUpdateView(FeesUpdateView):
    model = ProducerClient
    form_class = ProducerClientForm
    success_url_name = 'fees:clients'
    extra_context = {'title': 'Edit Producer Client'}


# edit agent
@method_decorator(login_required, name="dispatch")
class AgentUpdateView(FeesUpdateView):
    model = Agent
    form_class = AgentForm
    success_url_name = 'fees:agents'


# edit deal
@method_decorator(login_required, name="dispatch")
class DealUpdateView(FeesUpdateView):
    model = Deal
    form_class = DealForm
    success_url_name = 'fees:agent-detail'
    related_field = 'agent'
    extra_context = {'form_type': 'Edit'}


@method_decorator(login_required, name="dispatch")
class JournalUpdateView(FeesUpdateView):
    model = Journal
    form_class = JournalForm
    extra_context = {'title': 'Edit Journal'}
    success_url_name = 'fees:journals'


@method_decorator(login_required, name="dispatch")
class SplitUpdateView(FeesUpdateView):
    model = DealSplit
    form_class = DealSplitForm
    success_url_name = 'fees:deal-detail'
    related_field = 'deal'
    extra_context = {'title': 'Edit Split'}


@method_decorator(login_required, name="dispatch")
class JDUpdateView(FeesUpdateView):
    model = JournalDetail
    form_class = JournalDetailForm
    success_url_name = 'fees:journal-detail'
    related_field = 'journal'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        producer = self.object.journal.producer
        kwargs['producer_context'] = producer
        return kwargs


@method_decorator(login_required, name="dispatch")
class BkgeClassUpdateView(FeesUpdateView):
    model = BkgeClass
    form_class = BkgeClassForm
    success_url_name = 'fees:bkgeclasses'
    extra_context = {'title': 'Edit Brokerage Class'}


@method_decorator(login_required, name="dispatch")
class ProducerUpdateView(FeesUpdateView):
    model = Producer
    form_class = ProducerForm
    success_url_name = 'fees:producers'
    extra_context = {'title': 'Edit Producer'}


#TODO
# create a commit journal form with validation in the clean method
# must ensure all accounts have been assigned to a deal, and if not, redirect
@login_required
def minerva_journal_commit_view(request, pk):
    template = 'fees/journal_commit.html'
    journal = Journal.objects.get(id=pk)
    form = JournalCommitConfirmForm(request.POST or None, instance=journal)
    context = {'form': form}
    if form.is_valid():
        journal.status = 'closed'
        execute_commit_journal(journal)
        journal.save()
        return redirect('fees:journals')
    return render(request, template, context=context)


# CREATE VIEWS **************************************************************************************

class FeesCreateView(CreateView):
    related_field = None
    success_url_name = None
    template_name = 'single_form_template.html'
    initial_model_attrs = {}

    def get_success_url(self):
        if not self.related_field:
            return reverse_lazy(self.success_url_name)
        related_object = getattr(self.object, self.related_field)
        return reverse(self.success_url_name, kwargs={'pk': related_object.id})

    def form_valid(self, form):
        obj = form.save(commit=False)

        for field, source in self.initial_model_attrs.items():
            value = self._resolve_source(source)
            if hasattr(obj, field):
                setattr(obj, field, value)
        obj.save()
        return super().form_valid(form)

    def _resolve_source(self, source):
        """Helper to resolve different types of sources."""
        if isinstance(source, str):
            return self.kwargs.get(source)
        elif callable(source):
            return source(self)
        return source


class ProducerClientCreateView(FeesCreateView):
    model = ProducerClient
    form_class = ProducerClientForm
    success_url_name = 'fees:clients'
    extra_context = {'title': 'Create Client'}
    form_kwargs = {'created_by': lambda self: self.request.user, }

    #def dispatch(self, request, *args, **kwargs):
    #    # adds request user to form_kwargs before executing form_valid
    #    self.form_kwargs = {'created_by': request.user}


@method_decorator(login_required, name="dispatch")
class AgentCreateView(FeesCreateView):
    model = Agent
    form_class = AgentForm
    success_url_name = 'fees:agents'
    extra_context = {'title':'Create Agent'}


@method_decorator(login_required, name="dispatch")
class DealCreateView(FeesCreateView):
    model = Deal
    form_class = DealForm
    success_url_name = 'fees:agent-detail'
    related_field = 'agent'
    extra_context = {'title':'Create Deal'}
    form_kwargs = {'agent_id': 'agent_id'}


@method_decorator(login_required, name="dispatch")
class SplitCreateView(FeesCreateView):
    model = DealSplit
    form_class = DealSplitForm
    success_url_name = 'fees:deal-detail'
    related_field = 'deal'
    extra_context = {'title':'Create Split'}
    form_kwargs = {'deal_id': 'deal_id'}


@method_decorator(login_required, name="dispatch")
class JournalCreateView(FeesCreateView):
    model = Journal
    form_class = JournalForm
    success_url_name = 'fees:journals'
    extra_context = {'title': 'Create Journal'}


@method_decorator(login_required, name="dispatch")
class JDCreateView(FeesCreateView):
    model = JournalDetail
    form_class = JournalDetailForm
    success_url_name = 'fees:journal-detail'
    related_field = 'journal'
    extra_context = {'title': 'Create Journal Detail'}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        journal_id = self.kwargs.get('journal_id')
        journal = Journal.objects.get(id=journal_id)
        kwargs['journal'] = journal
        kwargs['producer_context'] = journal.producer
        return kwargs


@method_decorator(login_required, name="dispatch")
class BkgeClassCreateView(FeesCreateView):
    model = BkgeClass
    form_class = BkgeClassForm
    success_url_name = 'fees:bkgeclasses'
    extra_context = {'title': 'Create Brokerage Class'}


@method_decorator(login_required, name="dispatch")
class ProducerCreateView(FeesCreateView):
    model = Producer
    form_class = ProducerForm
    success_url_name = 'fees:producers'
    extra_context = {'title': 'Create Producer'}


# DELETE VIEWS **************************************************************************************

class FeesDeleteView(DeleteView):
    related_field = None
    success_url_name = None
    context_object_name = 'object'
    template_name = 'delete_template.html'
    cancel_link_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.related_field:
            context['cancel_link'] = reverse_lazy(self.cancel_link_name)
        else:
            related_object = getattr(self.object, self.related_field)
            context['cancel_link'] = reverse(self.cancel_link_name, kwargs={'pk': related_object.id})
        return context

    def get_success_url(self):
        if not self.related_field:
            return reverse_lazy(self.success_url_name)
        related_object = getattr(self.object, self.related_field)
        return reverse(self.success_url_name, kwargs={'pk': related_object.id})


@method_decorator(login_required, name="dispatch")
class JournalDeleteView(FeesDeleteView):
    model = Journal
    success_url_name = 'fees:journals'


@method_decorator(login_required, name="dispatch")
class SplitDeleteView(FeesDeleteView):
    model = DealSplit
    success_url_name = 'fees:deal-detail'
    related_field = 'deal'
    cancel_link_name = 'fees:deal-detail'


@method_decorator(login_required, name="dispatch")
class JDDeleteView(FeesDeleteView):
    model = JournalDetail
    success_url_name = 'fees:journal-detail'
    related_field = 'journal'
    cancel_link_name = 'fees:journal-detail'


# ----------------------- OTHER VIEWS ------------------------------------


@method_decorator(login_required, name="dispatch")
class JournalCommitView(UpdateView):
    model = Journal
    form_class = JournalForm


@login_required
def journal_upload_view(request, pk):

    template = 'files/file_upload.html'
    journal = Journal.objects.get(id=pk)
    form = UploadFileForm(request.POST or None, request.FILES)
    context = {'form': form, 'journal': journal}

    if form.is_valid():
        file = request.FILES['file']
        df = file_manager.clean_file(journal.producer.code, file)
        accounts = df.account_code.unique().tolist()

        context['df'] = df

        # get list of accounts missing from DB
        missing_accounts = (
            df.loc[df.account_code.isin(check_unallocated_accounts(accounts, journal.producer)),
            ['account_code', 'name']].drop_duplicates()
        )
        missing_accounts = list(missing_accounts.itertuples(index=False))

        """
        # add missing accounts into DB with NULL deal code
        for missing_account in missing_accounts:
            ProducerClient.objects.create(
                producer=journal.producer,
                client_code=missing_account[0],
                name=missing_account[1],
                deal=None,
                created_by=request.user,
                updated_by=request.user
            )
        """

    return render(request, template, context=context)


@login_required
def journal_commit(request, pk):
    journal = Journal.objects.get(id=pk)
    if journal and journal.status == 'OPEN':
        journal.commission_period = CommissionPeriod.get_current_period()
        journal.status = 'CLOSED'


