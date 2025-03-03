from django.shortcuts import render
from .tables import ChargeTypeTable
from .models import ChargeType
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django_tables2 import SingleTableView, MultiTableMixin, SingleTableMixin
# Create your views here.


class ChargesListView(SingleTableView):
    template_name = 'single_table_template.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super(ChargesListView, self).get_context_data(**kwargs)
        context.update(self.context_data)
        return context


@method_decorator(login_required, name="dispatch")
class ChargeTypeListView(ChargesListView):
    model = ChargeType
    table_class = ChargeTypeTable
    context_data = {
        'title': 'Charge Types'
    }
