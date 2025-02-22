
from django_tables2 import Table, Column, TemplateColumn

from .models import Agent, Deal, DealSplit, Journal, JournalDetail

class AgentTable(Table):
    agent_code = Column(linkify=True)
    edit = TemplateColumn(template_code="<a href={% url 'fees:agent-edit' record.pk %}>Edit</a>")
    class Meta:
        model = Agent
        fields = ('agent_code','first_name','last_name','abn','is_gst_exempt','edit')
        orderable = True


class DealTable(Table):
    code = Column(linkify=True)
    edit = TemplateColumn(template_code="<a href={% url 'fees:deal-edit' record.pk %}>Edit</a>")
    class Meta:
        model = Deal
        fields = ('code', 'name', 'agent', 'edit')
        orderable = True


class DealSplitTable(Table):
    #code = Column(linkify=True)
    edit = TemplateColumn(template_code="<a href={% url 'fees:split-edit' record.pk %}>Edit</a>")
    delete = TemplateColumn(template_code="<a class=split-delete href={% url 'fees:split-delete' record.pk %}>Delete</a>")
    class Meta:
        model = DealSplit
        fields = ('deal', 'agent', 'producer_filter', 'bkge_class_filter', 'percentage','edit', 'delete')
        orderable = True


class JournalTable(Table):
    id = Column(linkify=True)
    edit = TemplateColumn(template_code="<a href={% url 'fees:journal-edit' record.pk %}>Edit</a>")
    delete = TemplateColumn(template_code="<a class=journal-delete href={% url 'fees:journal-delete' record.pk %}>Delete</a>")
    class Meta:
        model = Journal
        fields = ('id', 'period_end_date', 'description', 'reference', 'cash_amount', 'producer', 'cash_account')
        orderable = True


class JDTable(Table):
    edit = TemplateColumn(template_code="<a href={% url 'fees:jd-edit' record.pk %}>Edit</a>")
    delete = TemplateColumn(template_code="<a class=jd-delete href={% url 'fees:jd-delete' record.pk %}>Delete</a>")
    class Meta:
        model = JournalDetail
        fields = ('id', 'amount', 'gst', 'details', 'lender_amount', 'lender_gst', 'balance', 'limit', 'bkge_class', 'client_account_code')
        orderable = True