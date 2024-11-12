from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/podcasts', views.PodcastView.v1_get_podcasts, name='v1_api_podcasts'),
    path('api/v2/podcasts', views.PodcastView.v2_get_podcasts, name='v2_api_podcasts'),
]
