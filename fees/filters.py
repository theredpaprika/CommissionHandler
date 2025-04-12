import django_filters
from .models import ProducerClient

class ProducerClientFilter(django_filters.FilterSet):
    class Meta:
        model = ProducerClient
        fields = ['producer','client_code','deal']
