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

FRACTALS_DIR = Path(
    os.environ.get("FRACTALS_DIR", Path(__file__).parent / "static" / "df")
)


class DateConverter(BaseConverter):
    """Extracts a ISO8601 date from the path and validates it."""

    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return value.strftime("%Y-%m-%d")


def _daily_fractal(date):
    return random_fractal(seed=seed_for_date(date))


def path_for_seed(seed, size):
    """Get the path for a given fractal.

    Please only pass a size that we do have fractals for.
    """

    assert size in (1920, 1366, 640, 200), size

    hashed = hashlib.md5(seed.encode()).hexdigest()

    path = FRACTALS_DIR / str(size)
    path /= hashed + ".png"
    return path


def ensure_exists(seed, size, logger):
    # Find a the next size that we provide that is bigger
    new = 1920
    for s in (1920, 1366, 640, 200):
        if size <= s:
            new = s
        else:
            break
    size = new

    path = path_for_seed(seed, size)

    # Make sure the directory exists
    path.parent.mkdir(exist_ok=True)

    if path.exists():
        logger.debug("Using cache for seed '%s'", seed)
    else:
        size = size, size * 9 // 16
        fractal = random_fractal(size, seed=seed)
        logger.info("Rendering '%s', size=%s", seed, size)
        fractal.render(True).save(path)

    return path


def seed_for_date(date):
    return date.strftime("%Y-%m-%d")


def my_log(seed, size, request):
    if size <= 200:
        # Don't want to log the fractals from home page
        return

    ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.environ["REMOTE_ADDR"])

    log = f"{ip} - {seed} - {size}\n"
    with open("seeds_log", "at") as f:
        f.write(log)
