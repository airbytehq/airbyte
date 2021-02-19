import datetime

from jinja2 import Environment

environment = Environment()
environment.globals['now_local'] = datetime.datetime.now
environment.globals['now_utc'] = lambda: datetime.datetime.now(datetime.timezone.utc)


def extrapolate(input_str, context):
    if isinstance(input_str, str):
        return environment.from_string(input_str).render(**context)
    return input_str


def extrapolate_bool(input_str, context):
    return str(extrapolate(input_str, context)) in ('True', 'true')
