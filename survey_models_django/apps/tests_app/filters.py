from django_filters import rest_framework as filters
from .models import Test


class TestFilter(filters.FilterSet):
    
    class Meta:
        model = Test
        fields = {
            'title': ['icontains'],
            'created_at': ['iexact', 'lte', 'gte']
        }