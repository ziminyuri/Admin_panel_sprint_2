from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    @staticmethod
    def render_to_response(context):
        return JsonResponse(context, json_dumps_params={'indent': ' '})

    @staticmethod
    def get_queryset():
        return FilmWork.objects.all().prefetch_related('genre', 'person').\
            values('id', 'title', 'description', 'creation_date', 'rating', 'type').\
            annotate(genres=ArrayAgg("genres__name", distinct=True)). \
            annotate(actors=ArrayAgg("persons__full_name", distinct=True,
                                     filter=Q(filmworkperson__role="actor"))).\
            annotate(directors=ArrayAgg("persons__full_name", distinct=True,
                                        filter=Q(filmworkperson__role="director"))).\
            annotate(writers=ArrayAgg("persons__full_name", distinct=True,
                                      filter=Q(filmworkperson__role="writer")))


class Movies(MoviesApiMixin, BaseListView):

    def get_context_data(self, **kwargs):
        paginator = Paginator(self.get_queryset(), 50)
        page_number = self.request.GET.get('page', '1')
        page_number = str(paginator.num_pages) if page_number == 'last' else page_number
        page_obj = paginator.get_page(page_number)
        page = paginator.page(page_number)

        return {
            'results': list(page_obj),
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'next': int(page_number) + 1 if page.has_next() else None,
            'prev': int(page_number) - 1 if page.has_previous() else None
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        return super().get_context_data().get('object')
