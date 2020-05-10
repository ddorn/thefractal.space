from dataclasses import dataclass
from math import log10
from typing import List

from brocoli.processing import SimpleCamera, Coloration
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse
from brocoli.fractal import Fractal
from markupsafe import Markup


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
    likes = models.ManyToManyField(User)

    class FractalKind(models.TextChoices):
        "All text must be the value of the Coloration enum."
        TIME = "ESC", "escape time"
        SMOOTH_TIME = "SMO", "smooth escape time"
        ANGLE = "ANG", "angle"
        AVG_TRIANGLE_INEQUALITY = "TRI", "average triangle inequality"
        AVG_CURVATURE = "CUR", "average curvature"
        AVG_STRIDE = "STR", "stride coloring"

        def to_brocoli(self):
            return Coloration(self.label)

    # Fractal parameters
    center_x = models.FloatField()
    center_y = models.FloatField()
    camera_height = models.FloatField()
    limit = models.PositiveSmallIntegerField()
    kind = models.CharField(max_length=3, choices=FractalKind)

    def __str__(self):
        return f"{self.name} by {self.created_by.username}"

    @classmethod
    def from_brocoli(cls, bfractal: Fractal):
        return cls(
            center_x=bfractal.camera.center.real,
            center_y=bfractal.camera.center.imag,
            camera_height=bfractal.camera.height,
        )

    def to_brocoli(self, size=(1920, 1080)):
        camera = SimpleCamera(
            size, complex(self.center_x, self.center_y), self.camera_height
        )
        return Fractal(camera, kind=self.kind.to_brocoli())

    @property
    def url(self):
        return reverse("fractal", kwargs={"id": self.id})

    def infos(self) -> List[Info]:
        infos = []

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

        return infos

        if self.julia is not None:
            infos.append(
                Info(
                    "Julia",
                    f"{round(self.julia.real, 4)} {round(self.julia.imag, 4) :+}i",
                    "Constant of the Julia set",
                )
            )

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

    def yaml(self):
        return "yaml"
