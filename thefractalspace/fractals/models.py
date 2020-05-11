from dataclasses import dataclass
from math import log10
from typing import List

from brocoli.processing.colors import hex2rgb
from colorfield.fields import ColorField
from brocoli.processing import SimpleCamera, Coloration
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse
from brocoli.fractal import Fractal
from markupsafe import Markup


TRI_TO_KIND = {
    "ESC": Coloration.TIME,
    "SMO": Coloration.SMOOTH_TIME,
    "ANG": Coloration.ANGLE,
    "TRI": Coloration.AVG_TRIANGLE_INEQUALITY,
    "CUR": Coloration.AVG_CURVATURE,
    "STR": Coloration.AVG_STRIDE,
}

KIND_TO_TRI = {value: key for key, value in TRI_TO_KIND.items()}


@dataclass
class Info:
    label: str
    value: str
    hint: str = None


class FractalModel(models.Model):
    class Meta:
        ordering = ["-created_at"]

    name = models.CharField(max_length=30)
    seed = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, models.PROTECT, related_name="fractals")
    likes = models.ManyToManyField(User, blank=True)

    fractal_kinds = [(tri, kind.value) for tri, kind in TRI_TO_KIND.items()]

    # Fractal parameters
    center_x = models.FloatField()
    center_y = models.FloatField()
    camera_height = models.FloatField()
    limit = models.PositiveSmallIntegerField(default=100)
    kind = models.CharField(max_length=3, choices=fractal_kinds)
    bound = models.FloatField(default=20_000)
    normalize_quantiles = models.BooleanField(default=False)
    gradient_loop = models.BooleanField(default=True)
    gradient_speed = models.FloatField(default=1.0)
    gradient_offset = models.FloatField(default=0.0)
    steps_power = models.FloatField(default=1.0)

    inside_color = ColorField(default="#000000")
    gradient_points = models.CharField(max_length=42, default="#000000-#ffffff")

    def __str__(self):
        return f"{self.name} by {self.created_by.username}"

    @classmethod
    def from_brocoli(cls, bfractal: Fractal):
        return cls(
            center_x=bfractal.camera.center.real,
            center_y=bfractal.camera.center.imag,
            camera_height=bfractal.camera.height,
            limit=bfractal.limit,
            kind=KIND_TO_TRI[bfractal.kind],
            bound=bfractal.bound,
            normalize_quantiles=bfractal.normalize_quantiles,
            gradient_loop=bfractal.gradient_loop,
            gradient_speed=bfractal.gradient_speed,
            gradient_offset=bfractal.gradient_offset,
            steps_power=bfractal.steps_power,
        )

    def to_brocoli(self, size=(1920, 1080)):
        camera = SimpleCamera(
            size, complex(self.center_x, self.center_y), self.camera_height
        )
        return Fractal(
            camera,
            kind=self.brocoli_kind,
            limit=self.limit,
            bound=self.bound,
            normalize_quantiles=self.normalize_quantiles,
            steps_power=self.steps_power,
            gradient_loop=self.gradient_loop,
            gradient_speed=self.gradient_speed,
            gradient_offset=self.gradient_offset,
            gradient_points=self.gradient,
        )

    @property
    def gradient(self):
        return [hex2rgb(c) for c in self.gradient_points.split("-")]

    @property
    def brocoli_kind(self):
        return TRI_TO_KIND[self.kind]

    @property
    def url(self):
        return reverse("fractal", kwargs={"id": self.id})

    def infos(self) -> List[Info]:
        infos = []

        if self.seed:
            infos.append(Info("Seed", self.seed, "What was used to generate it."))

        infos.append(Info("Likes", self.likes.count(), "How many people liked it."))

        zoom = 1.0 / self.camera_height
        # rounding: the 3 decimal places after important part
        r = round(log10(zoom)) + 3

        infos.append(
            Info(
                "Position",
                f"{round(self.center_x, r)} {round(self.center_y, r) :+}i",
                "Center of the fractal",
            )
        )

        infos.append(Info("Zoom", Markup(f"&times;{int(zoom)}"),))

        infos.append(
            Info(
                "Limit", str(self.limit), "Maximum number of steps calculated per pixel"
            )
        )

        infos.append(Info("Technique", str(self.kind).title()))

        infos.append(
            Info(
                "Gradient speed",
                str(self.gradient_speed),
                "Number of times the gradient loops",
            )
        )

        infos.append(
            Info(
                "Gradient shift",
                f"{int(self.gradient_offset * 100)} %",
                "Rotation of the gradient",
            )
        )

        return infos

        if self.julia is not None:
            infos.append(
                Info(
                    "Julia",
                    f"{round(self.julia.real, 4)} {round(self.julia.imag, 4) :+}i",
                    "Constant of the Julia set",
                )
            )

        return infos

    def yaml(self):
        return "yaml"
