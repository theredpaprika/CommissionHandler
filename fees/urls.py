
from django.urls import path
from .views import (agent_search_view, agent_create_view, journals_search_view,
                           journals_create_view, deals_search_view,
                           deals_create_view, agent_view, split_create_view, journal_view,
                           journal_detail_create_view,
                           client_create_view, client_search_view, client_edit_view, journal_commit_view,
                           journal_delete_view,
                           journal_detail_delete_view, journal_upload_view, \
                           AgentListView, AgentDetailView, AgentUpdateView, AgentCreateView, DealListView,
                           DealDetailView, DealUpdateView,
                           SplitUpdateView, SplitCreateView, SplitDeleteView, DealCreateView, JournalListView,
                           JournalCreateView, JournalUpdateView, JournalDetailView, JDCreateView,
                           JDUpdateView, JDDeleteView)

app_name = 'fees'

urlpatterns = [
    # LOOKING TO REPLACE THESE WITH CBVs
    path('clients/', client_search_view, name='clients'),
    path('clients/<str:client_code>/edit', client_edit_view, name='clientedit'),
    #path('agents/', agent_search_view, name='agents'),
    #path('agents/create', agent_create_view, name='agentcreate'),
    #path('agents/<str:agent_code>', agent_view, name='agent'),
    #path('agents/<str:agent_code>/edit', agent_create_view, name='agentedit'),
    #path('agents/<str:agent_code>/deals/', deals_search_view, name='deals'),
    #path('agents/<str:agent_code>/deals/create/', deals_create_view, name='dealcreate'),
    #path('agents/<str:agent_code>/deals/<str:deal_code>', deal_view, name='deal'),
    #path('agents/<str:agent_code>/deals/<str:deal_code>/edit', deals_create_view, name='dealedit'),
    #path('agents/<str:agent_code>/deals/<str:deal_code>/splits/create', split_create_view, name='splitcreate'),
    #path('agents/<str:agent_code>/deals/<str:deal_code>/splits/<str:split_id>/edit', split_create_view,
    #     name='splitedit'),
    #path('agents/<str:agent_code>/producerclient/create', client_create_view, name='agentclientcreate'),
    path('mjournals/', journals_search_view, name='mjournals'),
    path('mjournals/create/', journals_create_view, name='mjournalcreate'),
    path('mjournals/<int:journal_id>', journal_view, name='mjournal'),
    path('mjournals/<int:journal_id>/commit', journal_commit_view, name='mjournalcommit'),
    path('mjournals/<int:journal_id>/delete', journal_delete_view, name='mjournaldelete'),
    path('mjournals/<int:journal_id>/upload', journal_upload_view, name='mjournaldetailupload'),
    path('mjournals/<int:journal_id>/edit', journals_create_view, name='mjournaledit'),
    path('mjournals/<int:journal_id>/details/create', journal_detail_create_view, name='mjournaldetailcreate'),
    path('mjournals/<int:journal_id>/details/<int:id>/edit', journal_detail_create_view,
         name='mjournaldetailedit'),
    path('mjournals/<int:journal_id>/details/<int:detail_id>/delete', journal_detail_delete_view,
         name='mjournaldetaildelete'),


    # (mostly) CBVs
    path('agents/', AgentListView.as_view(), name='agents'),
    path('agents/create', AgentCreateView.as_view(), name='agent-create'),
    path('agents/<int:pk>', AgentDetailView.as_view(), name='agent-detail'),
    path('agents/<int:pk>/edit', AgentUpdateView.as_view(), name='agent-edit'),
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
    path('journals/<int:journal_id>/jds/create', JDCreateView.as_view(), name='jd-create'),
    path('journal-details/<int:pk>/edit', JDUpdateView.as_view(), name='jd-edit'),
    path('journal-details/<int:pk>/delete', JDDeleteView.as_view(), name='jd-delete'),
]