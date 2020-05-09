from django.urls import path
from . import views

urlpatterns = [
    path("brouse", views.FractalListView.as_view(), name="brouse"),
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("latest", views.about, name="latest"),
    path("random", views.about, name="random"),
    path("fractal", views.about, name="fractal"),
    path("img/<path:id>", views.img, name="img"),
]
