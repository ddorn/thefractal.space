from dataclasses import dataclass
from typing import List

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse


@dataclass
class Info:
    label: str
    value: str
    hint: str = None


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

    def infos(self) -> List[Info]:
        infos = []

        infos.append(Info("Seed", self.seed, "What was used to generate it."))

        infos.append(Info("Likes", self.likes.count(), "How many people liked it."))

        return infos

        if self.julia is not None:
            infos.append(
                Info(
                    "Julia",
                    f"{round(self.julia.real, 4)} {round(self.julia.imag, 4) :+}i",
                    "Constant of the Julia set",
                )
            )

        zoom = 1.0 / self.camera.height
        # rounding: the 3 decimal places after important part
        r = round(log10(zoom)) + 3

        pos = self.camera.center
        infos.append(
            Info(
                "Position",
                f"{round(pos.real, r)} {round(pos.imag, r) :+}i",
                "Center of the fractal",
            )
        )

        infos.append(Info("Zoom", Markup(f"&times;{int(zoom)}"),))

        infos.append(Info("Technique", self.kind.value.title()))

        infos.append(
            Info(
                "Limit", str(self.limit), "Maximum number of steps calculated per pixel"
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
