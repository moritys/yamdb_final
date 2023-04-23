from django_filters.rest_framework import BaseInFilter, CharFilter, FilterSet

from reviews.models import Title


class CharInFilter(BaseInFilter, CharFilter):
    pass


class TitleFilter(FilterSet):
    genre = CharInFilter(
        field_name='genre__slug',
        lookup_expr='in',
    )
    category = CharInFilter(
        field_name='category__slug',
        lookup_expr='in',
    )

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year',)
