"""
Environement variables:
 - FRACTALS_DIR: path to save all the computed fractals.
"""

import random as _random
from datetime import datetime, timedelta

from brocoli.processing.random_fractal import random_fractal
from flask import Flask, render_template, request, send_from_directory

from .helpers import DateConverter, \
    infos, _daily_fractal, \
    path_for_seed, seed_for_date


from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': 'log',
            'maxBytes': 1024,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})

app = Flask(__name__)

app.url_map.converters['date'] = DateConverter


def fractal_page(fractal, title, seed, subtitle=None, date=None):
    i = infos(fractal)
    return render_template(
        'index.html',
        title=title,
        subtitle=subtitle,
        date=date,
        infos=i,
        gradient=fractal.gradient_points,
        one_day=timedelta(days=1),
        seed=seed,
    )


@app.route('/')
def home():
    return generate()


@app.route('/df/<date:date>')
def daily_fractal(date):
    return fractal_page(
        _daily_fractal(date),
        "Fractal of the day",
        date=date,
        seed=seed_for_date(date)
    )


@app.route('/df/latest')
def latest():
    return daily_fractal(datetime.today())


@app.route('/random')
def random():
    seed = hex(_random.randint(0, 16 ** 6 - 1))[2:]
    return fractal_page(random_fractal(seed=seed), "Random Fractal", seed, f"Seed - {seed}")


@app.route("/brouse")
def brouse():
    page = request.args.get("page", default=0, type=int)
    page = max(0, page)  # no negative pages

    fracs_per_page = 12
    one_day = timedelta(1)
    first = datetime.today() - fracs_per_page * page * one_day

    days = [first - i * one_day for i in range(fracs_per_page)]
    return render_template("brouse.html", days=days, title="Browse", page=page)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/generate")
def generate():
    seed = request.args.get("seed", type=str)
    if seed is None:
        return render_template("generate.html", title="Custom Fractal")
    return fractal_page(random_fractal(seed=seed), "Custom Fractal", seed, f"Seed: {seed}")


@app.route("/img/<path:seed>.png")
def img(seed):
    """The seed can be any string.
    Files are saved on the md5 hash of their name."""
    size = request.args.get("size", default=200, type=int)

    # Find a the next size that we provide that is bigger
    new = 1280
    for s in (1280, 640, 200):
        if size <= s:
            new = s
        else:
            break
    size = new

    path = path_for_seed(seed, size)

    # Make sure the directory exists
    path.parent.mkdir(exist_ok=True)

    if path.exists():
        app.logger.info("Using cache for seed '%s'", seed)
    else:
        size = size, size * 9 // 16
        fractal = random_fractal(size, seed=seed)
        app.logger.info("Rendering '%s', size=%s", seed, size)
        fractal.render(True).save(path)

    return send_from_directory(path.parent, path.name)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
