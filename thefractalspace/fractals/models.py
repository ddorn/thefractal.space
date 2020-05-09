from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse


class Fractal(models.Model):
    class Meta:
        ordering = ["-created_at"]

    name = models.CharField(max_length=30, unique=True)
    seed = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, models.PROTECT, related_name="fractals")
    likes = models.ManyToManyField(User)

    def __str__(self):
        return f"{self.name} by {self.created_by.username}"
