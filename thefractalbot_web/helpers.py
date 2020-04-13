from dataclasses import dataclass
from datetime import datetime
from math import log10
from pathlib import Path
from typing import List

from brocoli.fractal import Fractal
from brocoli.processing.random_fractal import random_fractal
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


def _daily_fractal(date):

    today = date.strftime("%d %b %Y")
    fractal = random_fractal(seed=today)

    return fractal


def ensure_daily_exists(date, small=True):
    static = Path(__file__).parent / "static"
    path = static / "df"
    path /= "small" if small else "big"

    # Make sure the directory exists
    path.mkdir(exist_ok=True)

    path /= date.strftime(f"%Y-%m-%d.png")

    if not path.exists():
        fractal = _daily_fractal(date)
        fractal.camera.size = (16*12, 9*12) if small else (16*80, 9*80)
        img = fractal.render(True)
        img.save(path)

    return path.relative_to(static)


def ensure_seed_exists(seed, small=True):
    static = Path(__file__).parent / "static"
    path = static / "df"
    path /= "small" if small else "big"

    # Make sure the directory exists
    path.mkdir(exist_ok=True)

    path /= seed + ".png"

    if not path.exists():
        fractal = random_fractal((16*12, 9*12) if small else (16*80, 9*80))
        fractal.render(True).save(path)

    return path.relative_to(static)
