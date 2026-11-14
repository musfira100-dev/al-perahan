from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/checkout/", views.api_checkout, name="api_checkout"),
    path("api/track/", views.api_track, name="api_track"),
    path("api/bespoke/", views.api_bespoke, name="api_bespoke"),
    path("api/newsletter/", views.api_newsletter, name="api_newsletter"),
]
