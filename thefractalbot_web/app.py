import random as _random
from datetime import datetime, timedelta

from brocoli.processing.random_fractal import random_fractal
from flask import Flask, render_template

from thefractalbot_web.helpers import DateConverter, infos, ensure_daily_exists, _daily_fractal, ensure_seed_exists

app = Flask(__name__)

app.url_map.converters['date'] = DateConverter


def fractal_page(fractal, title, src, subtitle=None, date=None):
    i = infos(fractal)
    return render_template(
        'index.html',
        title=title,
        subtitle=subtitle,
        date=date,
        infos=i,
        gradient=fractal.gradient_points,
        one_day=timedelta(days=1),
        fractal_src=src,
    )


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/df/<date:date>')
def daily_fractal(date):
    fractal_src = ensure_daily_exists(date, small=False)
    return fractal_page(_daily_fractal(date), "Fractal of the day", date=date, src=fractal_src)


@app.route('/df/latest')
def latest():
    return daily_fractal(datetime.today())


@app.route('/random')
def random():
    seed = hex(_random.randint(0, 16 ** 6 - 1))[2:]
    src = ensure_seed_exists(seed, small=False)
    return fractal_page(random_fractal(seed=seed), "Random Fractal", src, f"Seed - {seed}")


@app.route("/brouse")
def brouse():
    today = datetime.today()
    one_day = timedelta(1)
    days = [today - i * one_day for i in range(20)]
    for day in days:
        ensure_daily_exists(day)
    return render_template("brouse.html", days=days)


if __name__ == '__main__':
    app.run(debug=True)
