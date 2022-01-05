from django.urls import path
from movies.api.v1 import views

urlpatterns = [
    path('movies/', views.MoviesListView.as_view()),
    path('movies/<uuid:id>/', views.MoviesDetailApi.as_view()),
]