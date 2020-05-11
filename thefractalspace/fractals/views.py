from pathlib import Path

from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, FileResponse
from django.urls import reverse
from django.views import generic
from django.views.generic import RedirectView

from .models import FractalModel


def brouse(request):
    count = FractalModel.objects.count()
    names = [fr.name for fr in FractalModel.objects.all()]

    context = {"num_fractals": count}
    return render(request, "fractals/brouse.html", context)


def home(request):
    return render(request, "fractals/index.html",)


def about(request):
    context = {"reverse": reverse}
    return render(request, "fractals/about.html", context)


def yaml_src(request, pk):
    f = get_object_or_404(FractalModel, id=pk)
    return HttpResponse(f.yaml(), content_type="yaml/yaml")


class Latest(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        f = FractalModel.objects.all()[0]
        return reverse("fractal", kwargs=dict(pk=f.id))


class FractalListView(generic.ListView):
    model = FractalModel
    context_object_name = "fractals"
    template_name = "fractals/brouse.html"


class FractalDetailView(generic.DetailView):
    model = FractalModel
    context_object_name = "f"
    template_name = "fractals/fractal.html"


def img(request, pk):
    with open(Path(__file__).parent.parent / "static" / "logo.png", "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")
