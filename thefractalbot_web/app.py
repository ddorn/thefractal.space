from datetime import datetime

from flask import Flask, render_template, redirect, url_for
from werkzeug.routing import BaseConverter, ValidationError


app = Flask(__name__)


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


app.url_map.converters['date'] = DateConverter


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/df/<date:date>')
def daily_fractal(date):
    return str(date)


@app.route('/df/latest')
def latest():
    return redirect(url_for("daily_fractal", date=datetime.today()))

if __name__ == '__main__':
    app.run(debug=True)
