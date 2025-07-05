import django_filters
from .models import ProducerClient, Journal

class ProducerClientFilter(django_filters.FilterSet):
    class Meta:
        model = ProducerClient
        fields = ['producer','client_code','deal']


class JournalFilter(django_filters.FilterSet):
    class Meta:
        model = Journal
        fields = ['status']
