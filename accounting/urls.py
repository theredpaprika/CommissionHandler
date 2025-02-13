
from django.urls import path
from .views import (account_search_view, account_create_view, account_view, journal_search_view, journal_view,
                           journal_create_view, account_subtype_create_view, journal_create_cash_topup_view)

app_name = 'accounting'

urlpatterns = [
    path('accountsubtype/', account_subtype_create_view),
    path('accounts/', account_search_view, name='accounts'),
    path('accounts/create/', account_create_view, name='account-create'),
    path('accounts/<str:account_code>/', account_view, name='account'),
    path('journals/', journal_search_view, name='journals'),
    path('journals/create', journal_create_view, name='journal-create'),
    path('journals/<int:id>/', journal_view, name='journal'),
    path('journals/cash', journal_create_cash_topup_view, name='add-cash'),
    path('journals/<int:id>/', journal_view),
]