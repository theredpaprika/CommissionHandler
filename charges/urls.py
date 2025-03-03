from django.urls import path
from .views import (ChargeTypeListView)

app_name = 'charges'

urlpatterns = [
    path('types', ChargeTypeListView.as_view(), name='charge-types'),
]