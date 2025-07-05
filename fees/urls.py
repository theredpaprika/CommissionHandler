
from django.urls import path
from .views import (agent_search_view, agent_create_view, journals_search_view,
    journals_create_view, deals_search_view,
    deals_create_view, agent_view, split_create_view, journal_view,
    journal_detail_create_view,
    client_create_view, client_search_view, client_edit_view, journal_commit_view,
    journal_delete_view,
    journal_detail_delete_view, journal_upload_view,
    AgentListView, AgentDetailView, AgentUpdateView, AgentCreateView, DealListView,
    DealDetailView, DealUpdateView,
    SplitUpdateView, SplitCreateView, SplitDeleteView, DealCreateView, JournalListView,
    JournalCreateView, JournalUpdateView, JournalDetailView, JournalDeleteView, JDCreateView,
    JDUpdateView, JDDeleteView, BkgeClassListView, BkgeClassCreateView, BkgeClassUpdateView,
    ProducerListView, ProducerUpdateView, ProducerCreateView, ProducerClientListView, ProducerClientCreateView,
    ProducerClientUpdateView
)

app_name = 'fees'

urlpatterns = [
    path('agents/', AgentListView.as_view(), name='agents'),
    path('agents/create', AgentCreateView.as_view(), name='agent-create'),
    path('agents/<int:pk>', AgentDetailView.as_view(), name='agent-detail'),
    path('agents/<int:pk>/edit', AgentUpdateView.as_view(), name='agent-edit'),
    path('clients/', ProducerClientListView.as_view(), name='clients'),
    path('clients/create', ProducerClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/edit', ProducerClientUpdateView.as_view(), name='client-edit'),
    path('deals/', DealListView.as_view(), name='deals'),
    path('agents/<int:agent_id>/deals/create', DealCreateView.as_view(), name='deal-create'),
    path('deals/<int:pk>', DealDetailView.as_view(), name='deal-detail'),
    path('deals/<int:pk>/edit', DealUpdateView.as_view(), name='deal-edit'),
    path('splits/<int:pk>/edit', SplitUpdateView.as_view(), name='split-edit'),
    path('deals/<int:deal_id>/splits/create', SplitCreateView.as_view(), name='split-create'),
    path('splits/<int:pk>/delete', SplitDeleteView.as_view(), name='split-delete'),
    path('journals/', JournalListView.as_view(), name='journals'),
    path('journals/create', JournalCreateView.as_view(), name='journal-create'),
    path('journals/<int:pk>', JournalDetailView.as_view(), name='journal-detail'),
    path('journals/<int:pk>/edit', JournalUpdateView.as_view(), name='journal-edit'),
    path('journals/<int:pk>/delete', JournalDeleteView.as_view(), name='journal-delete'),
    path('journals/<int:journal_id>/jds/create', JDCreateView.as_view(), name='jd-create'),
    path('journal-details/<int:pk>/edit', JDUpdateView.as_view(), name='jd-edit'),
    path('journal-details/<int:pk>/delete', JDDeleteView.as_view(), name='jd-delete'),
    path('journals/<int:pk>/upload', journal_upload_view, name='journal-upload'),
    path('journals/<int:pk>/commit', journal_commit_view, name='journal-commit'),
    path('bkgeclasses', BkgeClassListView.as_view(), name='bkgeclasses'),
    path('bkgeclasses/create', BkgeClassCreateView.as_view(), name='bkgeclass-create'),
    path('bkgeclasses/<int:pk>/edit', BkgeClassUpdateView.as_view(), name='bkgeclass-edit'),
    path('producers', ProducerListView.as_view(), name='producers'),
    path('producers/create', ProducerCreateView.as_view(), name='producer-create'),
    path('producers/<int:pk>/edit', ProducerUpdateView.as_view(), name='producer-edit'),

]