import io
from pathlib import Path

import yaml
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
    stream = io.StringIO()

    stream.write("# You can regenerate the fractal with brocoli\n")
    stream.write("# https://gitlab.com/ddorn/brocoli by running \n")
    stream.write(f'# brocoli gen --yaml "{f.name}.yaml"\n')
    stream.write("# You can also tweek every parameter (size/color...)\n")
    stream.write("# And make it look even better!\n")
    stream.write("# Have fun ! Diego\n")
    yaml.dump(f.to_brocoli(), stream)
    stream.seek(0)

    response = HttpResponse(stream, content_type="yaml/yaml",)
    response["Content-Disposition"] = f'attachment; filename="{f.name}.yaml"'
    return response


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
