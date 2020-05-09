from django.urls import path
from . import views

urlpatterns = [
    path("brouse", views.brouse, name="brouse"),
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("latest", views.about, name="latest"),
    path("random", views.about, name="random"),
]
