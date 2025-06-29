from typing import Any
import datetime as dt

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.db import transaction

from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django_tables2 import SingleTableView, MultiTableMixin, SingleTableMixin
from django.urls import reverse_lazy, reverse

from .models import Fee, Agent, Journal, Deal, DealSplit, ProducerClient, JournalDetail, Producer, Fee, BkgeClass
from .forms import (AgentForm, JournalForm, DealForm, DealSplitForm, JournalDetailForm, BkgeClassForm,
                    ProducerClientForm, DeleteConfirmForm, UploadFileForm, JournalCommitConfirmForm, ProducerForm)
from .tables import (AgentTable, DealTable, DealSplitTable, JournalTable,
                     ProducerClientTable, JDTable, BkgeClassTable, ProducerTable)
from accounting.models import CommissionPeriod
from .filters import ProducerClientFilter, JournalFilter

from files.producer_dispatcher import ProducerCleanerRegistry
from .services.journal_upload import add_missing_accounts, create_journal_details
from .services.journal_commit import FeeGenerator

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
class JournalListView(TemplateView):
    template_name = 'single_table_template.html'
    context_object_name = 'object'
    context_data = {
        'create_link': reverse_lazy('fees:journal-create'),
        'title': 'Open Journals'
    }

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['table'] = JournalTable(Journal.objects.filter(status='OPEN').all())
        context.update(self.context_data)
        return context


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
class JournalDetailView(DetailView):
    model = Journal
    context_object_name = 'journal'
    #context_table_name = 'table'
    template_name = 'fees/journal_detail.html'
    #table_class = JDTable
    table_pagination = {"per_page": 20}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_heading'] = 'Journal Details'
        context['title'] = f'Journal {self.object}'
        context['create_link'] = reverse('fees:jd-create', kwargs={'journal_id':self.object.id}  )
        context['upload_link'] = reverse('fees:journal-upload', kwargs={'pk':self.object.id})
        context['unallocated_accounts_table'] = ProducerClientTable(self.get_unallocated_accounts_data())
        context['jd_table'] = JDTable(self.object.details.all())
        return context

    def get_unallocated_accounts_data(self):
        return self.object.get_accounts_with_null_deal()


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

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        print("Raw next URL:", next_url)  # Debugging line

        # Force the next URL to be a relative URL only
        if next_url and next_url.startswith('/'):
            print("Redirecting to:", next_url)
            return next_url

        # Default to producer client list if no 'next' parameter or if invalid
        print("Redirecting to default list view.")
        return reverse(self.success_url_name)

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



# CREATE VIEWS **************************************************************************************

class FeesCreateView(CreateView):
    related_field = None
    success_url_name = None
    template_name = 'single_form_template.html'
    initial_model_attrs = {}

    def _initial_model_attrs(self):
        # override on child class with changes you want to make to model instance field
        return None

    def get_success_url(self):
        if not self.related_field:
            return reverse_lazy(self.success_url_name)
        related_object = getattr(self.object, self.related_field)
        return reverse(self.success_url_name, kwargs={'pk': related_object.id})

    def form_valid(self, form):
        # check if child class specifies amendments to model fields
        if extra_model_attrs := self._initial_model_attrs():
            obj = form.save(commit=False)
            # edit fields
            for field, value in extra_model_attrs.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)
            obj.save()
        return super().form_valid(form)


class ProducerClientCreateView(FeesCreateView):
    model = ProducerClient
    form_class = ProducerClientForm
    success_url_name = 'fees:clients'
    extra_context = {'title': 'Create Client'}

    def _initial_model_attrs(self):
        return {'created_by_id': self.request.user.id}

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

    def _initial_model_attrs(self):
        return {'agent_id': self.kwargs.get('agent_id')}


@method_decorator(login_required, name="dispatch")
class SplitCreateView(FeesCreateView):
    model = DealSplit
    form_class = DealSplitForm
    success_url_name = 'fees:deal-detail'
    related_field = 'deal'
    extra_context = {'title':'Create Split'}

    def _initial_model_attrs(self):
        return {'deal_id': self.kwargs.get('deal_id')}


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
    cancel_link_name = 'fees:journals'

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
    journal = get_object_or_404(Journal, id=pk)
    form = UploadFileForm(request.POST or None, request.FILES)

    if not form.is_valid():
        return render(request, 'files/file_upload.html', {'form': form, 'journal': journal})

    uploaded_file = request.FILES['file']
    df = ProducerCleanerRegistry.clean(journal.producer.code, uploaded_file)
    add_missing_accounts(df, journal, request.user)
    create_journal_details(df, journal_id=pk, producer_id=journal.producer.id)

    return redirect('fees:journal-detail', pk=pk)


@login_required
def journal_commit_view(request, pk):
    journal = Journal.objects.get(id=pk)
    if journal and journal.status == 'OPEN':
        try:
            with transaction.atomic():
                journal.commission_period = CommissionPeriod.get_current_period()
                fee_generator = FeeGenerator()
                fee_generator.get_journal_details(journal)
                fee_generator.generate_fees()
                Fee.objects.bulk_create(fee_generator.fees)
                journal.status = 'CLOSED'
                journal.save()
        except Exception as e:
            print(e)
    return redirect('fees:journals')



