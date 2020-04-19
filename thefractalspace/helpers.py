import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from math import log10
from pathlib import Path
from typing import List

from brocoli.fractal import Fractal
from brocoli.processing.random_fractal import random_fractal
from markupsafe import Markup
from werkzeug.routing import BaseConverter, ValidationError

FRACTALS_DIR = Path(os.environ.get("FRACTALS_DIR", Path(__file__).parent / "static" / "df"))


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


def _daily_fractal(date):
    return random_fractal(seed=seed_for_date(date))


def path_for_seed(seed, size):
    """Get the path for a given fractal.

    Please only pass a size that we do have fractals for.
    """

    assert size in (1280, 640, 200), size

    hashed = hashlib.md5(seed.encode()).hexdigest()

    path = FRACTALS_DIR / str(size)
    path /= hashed + ".png"
    return path


def seed_for_date(date):
    return date.strftime("%Y-%m-%d")
