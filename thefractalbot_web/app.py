import random as _random
from datetime import datetime, timedelta

from brocoli.processing.random_fractal import random_fractal
from flask import Flask, render_template

from thefractalbot_web.helpers import DateConverter, infos

app = Flask(__name__)

app.url_map.converters['date'] = DateConverter


def fractal_page(fractal, title, subtitle=None, date=None):
    i = infos(fractal)
    return render_template(
        'index.html',
        title=title,
        subtitle=subtitle,
        date=date,
        infos=i,
        gradient=fractal.gradient_points,
        one_day=timedelta(days=1)
    )


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/df/<date:date>')
def daily_fractal(date):
    today = date.strftime("%d %b %Y")
    fractal = random_fractal(seed=today)
    return fractal_page(fractal, "Fractal of the day", date=date)


@app.route('/df/latest')
def latest():
    return daily_fractal(datetime.today())



@app.route('/random')
def random():
    seed = hex(_random.randint(0, 16**6 - 1))[2:]
    return fractal_page(random_fractal(seed=seed), "Random Fractal", f"Seed - {seed}")


if __name__ == '__main__':
    app.run(debug=True)
