from django.urls import path
from . import views

urlpatterns = [
    path('', views.PodcastViews.index, name='index'),
    path('filter/', views.PodcastViews.filter_podcasts, name='filter_podcasts'),
]
