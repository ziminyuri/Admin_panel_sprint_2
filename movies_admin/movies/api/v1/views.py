from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork, FilmWorkPerson


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    @staticmethod
    def render_to_response(context):
        return JsonResponse(context, json_dumps_params={'indent': ' '})

    @classmethod
    def get_queryset(cls):
        return FilmWork.objects.all().prefetch_related('genre', 'person').\
            values('id', 'title', 'description', 'creation_date', 'rating', 'type').\
            annotate(genres=ArrayAgg("genres__name", distinct=True),
                     actors=cls._aggregate_person(role=FilmWorkPerson.Role.ACTOR),
                     directors=cls._aggregate_person(role=FilmWorkPerson.Role.DIRECTOR),
                     writers=cls._aggregate_person(role=FilmWorkPerson.Role.WRITER))

    @classmethod
    def _aggregate_person(cls, role):
        return ArrayAgg("persons__full_name", distinct=True, filter=Q(filmworkperson__role=role))


class MoviesListView(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )

        return {
            'results': list(queryset.values()),
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'next': page.next_page_number() if page.has_next() else None,
            'prev': page.previous_page_number() if page.has_previous() else None
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs).get('object')
