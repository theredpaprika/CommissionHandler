
from django.urls import path
from .views import (journal_upload)

app_name = 'files'

urlpatterns = [
    path('journals/<int:pk>/upload', journal_upload, name='journal-upload'),
]