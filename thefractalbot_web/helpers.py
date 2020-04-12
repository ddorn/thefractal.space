from dataclasses import dataclass
from datetime import datetime
from math import log10
from typing import List

from brocoli.fractal import Fractal
from markupsafe import Markup
from werkzeug.routing import BaseConverter, ValidationError


class DateConverter(BaseConverter):
    """Extracts a ISO8601 date from the path and validates it."""

    regex = r'\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')


@dataclass
class Info:
    label: str
    value: str
    hint: str = None


def infos(fractal: Fractal) -> List[Info]:
    infos = []

    if fractal.julia is not None:
        infos.append(Info(
            "Julia",
            f"{round(fractal.julia.real, 4)} {round(fractal.julia.imag, 4) :+}i",
            "Constant of the Julia set"
        ))

    zoom = 1.0 / fractal.camera.height
    # rounding: the 3 decimal places after important part
    r = round(log10(zoom)) + 3

    pos = fractal.camera.center
    infos.append(Info(
        "Position",
        f"{round(pos.real, r)} {round(pos.imag, r) :+}i",
        "Center of the fractal"
    ))

    infos.append(Info(
        "Zoom",
        Markup(f"&times;{int(zoom)}"),
    ))

    infos.append(Info(
        "Technique",
        fractal.kind.value.title()
    ))

    infos.append(Info(
        "Limit",
        str(fractal.limit),
        "Maximum number of steps calculated per pixel"
    ))

    infos.append(Info(
        "Gradient speed",
        str(fractal.gradient_speed),
        "Number of times the gradient loops"
    ))

    infos.append(Info(
        "Gradient shift",
        f"{int(fractal.gradient_offset * 100)} %",
        "Rotation of the gradient"
    ))

    return infos