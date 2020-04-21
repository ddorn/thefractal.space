"""
Environement variables:
 - FRACTALS_DIR: path to save all the computed fractals.
"""
import io
import brocoli.brocoli
import random as _random
from datetime import datetime, timedelta
from logging.config import dictConfig

import yaml
from brocoli.processing.random_fractal import random_fractal
from flask import Flask, render_template, request, send_from_directory, Response

from .helpers import DateConverter, \
    infos, _daily_fractal, \
    path_for_seed, seed_for_date, ensure_exists, my_log

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
    path = ensure_exists(seed, size, app.logger)

    my_log(seed, size, request)

    return send_from_directory(path.parent, path.name)


@app.route("/img/<path:seed>.yaml")
def yaml_src(seed):
    fractal = random_fractal(seed=seed)
    stream = io.StringIO()
    stream.write("# You can regenerate the fractal with brocoli\n")
    stream.write("# https://gitlab/ddorn/brocoli by running \n")
    stream.write(f"# brocoli gen --yaml \"{seed}.yaml\"\n")
    stream.write("# You can also tweek every parameter (size/color)\n")
    stream.write("# And make it look even better!\n")
    stream.write("# Have fun ! Diego\n")
    yaml.dump(fractal, stream)
    stream.seek(0)
    return Response(stream, mimetype='text/yaml')


@app.route("/build-cache")
def build_cache():
    app.logger.info("Completing cache for small images in generate.")
    for i in range(1000):
        ensure_exists(str(i), 200, app.logger)
    app.logger.info("Cache built!")
    return "Cache built!"

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
