from django.urls import path
from .views import (ChargeTypeListView, ChargeTypeCreateView, ChargeTypeUpdateView,
                    ChargeScheduleListView, ChargeScheduleCreateView, ChargeScheduleUpdateView)

app_name = 'charges'

urlpatterns = [
    path('types', ChargeTypeListView.as_view(), name='charge-types'),
    path('types/create', ChargeTypeCreateView.as_view(), name='charge-type-create'),
    path('types/<int:pk>/edit', ChargeTypeUpdateView.as_view(), name='charge-type-edit'),
    path('schedules', ChargeScheduleListView.as_view(), name='schedules'),
    path('schedules/create', ChargeScheduleCreateView.as_view(), name='schedule-create'),
    path('schedules/<int:pk>/edit', ChargeScheduleUpdateView.as_view(), name='schedule-edit'),
]