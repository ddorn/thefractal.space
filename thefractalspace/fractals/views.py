from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.urls import reverse

from .models import Fractal


def brouse(request):
    count = Fractal.objects.count()
    names = [fr.name for fr in Fractal.objects.all()]

    context = {"num_fractals": count, "reverse": reverse}
    return render(request, "../templates/fractals/brouse.html", context)


def home(request):
    return HttpResponse("Home !")


def about(request):
    context = {"reverse": reverse}
    return render(request, "fractals/about.html", context)
