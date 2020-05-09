from pathlib import Path

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, FileResponse
from django.urls import reverse
from django.views import generic

from .models import Fractal


def brouse(request):
    count = Fractal.objects.count()
    names = [fr.name for fr in Fractal.objects.all()]

    context = {"num_fractals": count}
    return render(request, "fractals/brouse.html", context)


def home(request):
    return render(request, "fractals/index.html",)


def about(request):
    context = {"reverse": reverse}
    return render(request, "fractals/about.html", context)


class FractalListView(generic.ListView):
    model = Fractal
    context_object_name = "fractals"
    template_name = "fractals/brouse.html"


class FractalDetailView(generic.DetailView):
    model = Fractal
    context_object_name = "f"
    template_name = "fractals/fractal.html"


def img(request, id):
    with open(Path(__file__).parent.parent / "static" / "logo.png", "rb") as f:
        print("ok")
        return HttpResponse(f.read(), content_type="image/png")
