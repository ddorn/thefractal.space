import inspect

from django.templatetags.static import static
from django.urls import reverse, resolve
from django.utils.http import urlencode

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)

    def better_reverse(viewname, *args, **kwargs):
        url = reverse(viewname, args=args, kwargs=kwargs)
        return url

    def get(**kwargs):
        return f"?{urlencode(kwargs)}"

    env.globals.update({"static": static, "url": better_reverse, "get": get})
    return env
