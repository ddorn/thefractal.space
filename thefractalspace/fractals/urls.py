from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("latest", views.Latest.as_view(), name="latest"),
    path("random", views.about, name="random"),
    path("brouse", views.FractalListView.as_view(), name="brouse"),
    path("fractal/<int:pk>", views.FractalDetailView.as_view(), name="fractal"),
    path("img/<path:pk>", views.img, name="img"),
    path("yaml_src/<path:pk>", views.yaml_src, name="yaml_src"),
]
