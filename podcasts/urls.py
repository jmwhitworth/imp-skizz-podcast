from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/podcasts', views.PodcastViews.api_podcasts, name='api_podcasts'),
]
