
from django_tables2 import Table, Column, TemplateColumn
from django.utils.html import format_html
from .models import Agent, Deal, DealSplit, Journal, JournalDetail, BkgeClass, Producer, ProducerClient

class AgentTable(Table):
    agent_code = Column(linkify=True)
    edit = TemplateColumn(template_code="<a href={% url 'fees:agent-edit' record.pk %}>Edit</a>", orderable=False)
    class Meta:
        model = Agent
        fields = ('agent_code','first_name','last_name','abn','is_gst_exempt','edit')
        orderable = True


class DealTable(Table):
    code = Column(linkify=True)
    edit = TemplateColumn(template_code="<a href={% url 'fees:deal-edit' record.pk %}>Edit</a>", orderable=False)
    class Meta:
        model = Deal
        fields = ('code', 'name', 'agent', 'edit')
        orderable = True


class DealSplitTable(Table):
    #code = Column(linkify=True)
    edit = TemplateColumn(template_code="<a href={% url 'fees:split-edit' record.pk %}>Edit</a>", orderable=False)
    delete = TemplateColumn(template_code="<a class=split-delete href={% url 'fees:split-delete' record.pk %}>Delete</a>", orderable=False)
    class Meta:
        model = DealSplit
        fields = ('deal', 'agent', 'producer_filter', 'bkge_class_filter', 'percentage','edit', 'delete')
        orderable = True


class JournalTable(Table):
    id = Column(linkify=True)
    journal_amount = Column(orderable=False, accessor='total_credits')
    check_result = Column(orderable=False, empty_values=())
    edit = TemplateColumn(template_code="<a href={% url 'fees:journal-edit' record.pk %}>Edit</a>", orderable=False)
    delete = TemplateColumn(template_code="<a class=journal-delete href={% url 'fees:journal-delete' record.pk %}>Delete</a>", orderable=False)
    commit = TemplateColumn(template_code="<a class=journal-commit href={% url 'fees:journal-commit' record.pk %}>Commit</a>", orderable=False)

    class Meta:
        model = Journal
        sequence = ('id', 'period_end_date', 'description', 'reference', 'cash_amount', 'journal_amount', 'check_result', 'producer', 'cash_account', 'status',)
        exclude = ('commission_period',)
        orderable = True

    def render_check_result(self, record):
        # Render a tick or cross if cash amount matches journal credits
        credit = record.total_credits()
        if record.cash_amount == record.total_credits():
            return format_html('<span style="color:green;">&#10003;</span>')  # ✓
        else:
            return format_html('<span style="color:red;">&#10007;</span>')    # ✗



class JDTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'fees:jd-edit' record.pk %}>Edit</a>", orderable=False)
    delete = TemplateColumn(template_code="<a class=jd-delete href={% url 'fees:jd-delete' record.pk %}>Delete</a>", orderable=False)
    class Meta:
        model = JournalDetail
        fields = ('id', 'amount', 'gst', 'details', 'lender_amount', 'lender_gst', 'balance', 'limit', 'bkge_class', 'client_account')
        orderable = True


class BkgeClassTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'fees:bkgeclass-edit' record.pk %}>Edit</a>", orderable=False)
    class Meta:
        model = BkgeClass
        fields = ('code','name')
        orderable = True


class ProducerTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'fees:producer-edit' record.pk %}>Edit</a>", orderable=False)
    class Meta:
        model = Producer
        fields = ('code','name')
        orderable = True


class ProducerClientTable(Table):
    edit = TemplateColumn(
        template_code='<a href="{% url \'fees:client-edit\' record.pk %}?next={{ request.path|urlencode }}">Edit</a>',
        orderable=False)
    class Meta:
        model = ProducerClient
        fields = ('client_code','producer', 'name', 'deal')
        orderable = True