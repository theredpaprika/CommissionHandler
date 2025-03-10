from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django_tables2 import SingleTableView, MultiTableMixin, SingleTableMixin
from django.urls import reverse_lazy, reverse

from .tables import ChargeTypeTable, ChargeScheduleTable, ChargeTable
from .models import ChargeType, ChargeSchedule, Charge
from .forms import ChargeTypeForm, ChargeScheduleForm


# -----------------------------------------------------------------
# GENERIC VIEWS


class ChargeBaseListView(SingleTableView):
    template_name = 'single_table_template.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.context_data)
        return context


class ChargeBaseCreateView(CreateView):
    related_field = None
    success_url_name = None
    template_name = 'single_form_template.html'
    form_kwargs = None

    def get_success_url(self):
        if not self.related_field:
            return reverse_lazy(self.success_url_name)
        related_object = getattr(self.object, self.related_field)
        return reverse(self.success_url_name, kwargs={'pk': related_object.id})

    def form_valid(self, form):
        # if no form kwargs, just submit form
        if not self.form_kwargs:
            return super().form_valid(form)
        else:
            form.save(commit=False)
            # update model instance with values from form_kwargs
            for key, value in self.form_kwargs.items():
                setattr(form.instance, key, self.kwargs.get(value))
            return super().form_valid(form)


class ChargeBaseUpdateView(UpdateView):
    related_field = None
    success_url_name = None
    template_name = 'single_form_template.html'

    def get_success_url(self):
        if not self.related_field:
            return reverse_lazy(self.success_url_name)
        related_object = getattr(self.object, self.related_field)
        return reverse(self.success_url_name, kwargs={'pk': related_object.id})


# -----------------------------------------------------------------
# LIST VIEWS

@method_decorator(login_required, name="dispatch")
class ChargeTypeListView(ChargeBaseListView):
    model = ChargeType
    table_class = ChargeTypeTable
    context_data = {
        'create_link': reverse_lazy('charges:type-create'),
        'title': 'Charge Types'
    }

@method_decorator(login_required, name="dispatch")
class ChargeScheduleListView(ChargeBaseListView):
    model = ChargeSchedule
    table_class = ChargeScheduleTable
    context_data = {
        'create_link': reverse_lazy('charges:schedule-create'),
        'title': 'Charge Schedule'
    }


@method_decorator(login_required, name="dispatch")
class ChargesListView(ChargeBaseListView):
    model = Charge
    table_class = ChargeTable
    context_data = {
        'title': 'Open Charges'
    }


# ------------------------------------------------------------------
# CREATE VIEWS


@method_decorator(login_required, name="dispatch")
class ChargeTypeCreateView(ChargeBaseCreateView):
    model = ChargeType
    form_class = ChargeTypeForm
    success_url_name = 'charges:types'
    extra_context = {'title':'Create Charge Type'}


@method_decorator(login_required, name="dispatch")
class ChargeScheduleCreateView(ChargeBaseCreateView):
    model = ChargeSchedule
    form_class = ChargeScheduleForm
    success_url_name = 'charges:schedules'
    extra_context = {'title':'Create Charge Schedule'}


# ------------------------------------------------------------------
# UPDATE VIEWS


@method_decorator(login_required, name="dispatch")
class ChargeTypeUpdateView(ChargeBaseUpdateView):
    model = ChargeType
    form_class = ChargeTypeForm
    extra_context = {'title':'Create Charge Type'}
    success_url_name = 'charges:types'


@method_decorator(login_required, name="dispatch")
class ChargeScheduleUpdateView(ChargeBaseUpdateView):
    model = ChargeSchedule
    form_class = ChargeScheduleForm
    success_url_name = 'charges:schedules'
    extra_context = {'title':'Update Charge Schedule'}