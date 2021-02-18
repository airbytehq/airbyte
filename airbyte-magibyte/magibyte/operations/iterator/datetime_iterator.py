import operator
from datetime import timedelta
import re

import arrow

from .base_pagination import BasePagination


class DatetimeIterator(BasePagination):
    def __init__(self, **kwargs):
        super(DatetimeIterator, self).__init__(**kwargs)

    def iterate(self, context):
        start_date = arrow.get(self.extrapolate(self.options.get('start_date'), context))
        end_date = arrow.get(self.extrapolate(self.options.get('end_date'), context))
        step = parse_timedelta(self.extrapolate(self.options.get('step'), context))
        start_inclusive = str(self.extrapolate(self.options.get('start_inclusive', True), context)) == 'True'
        end_inclusive = str(self.extrapolate(self.options.get('end_inclusive', True), context)) == 'True'

        current_date = start_date
        if not start_inclusive:
            current_date += step

        comp = operator.le
        if not end_inclusive:
            comp = operator.lt

        while comp(current_date, end_date):
            yield {'current_date': current_date}
            current_date = current_date + step


timedelta_regex = re.compile(
                   r'((?P<weeks>[\.\d]+?)w)?'
                   r'((?P<days>[\.\d]+?)d)?'
                   r'((?P<hours>[\.\d]+?)h)?'
                   r'((?P<minutes>[\.\d]+?)m)?'
                   r'((?P<seconds>[\.\d]+?)s)?'
                   r'((?P<microseconds>[\.\d]+?)ms)?'
                   r'((?P<milliseconds>[\.\d]+?)us)?$'
                   )


def parse_timedelta(time_str):
    """
    Parse a time string e.g. (2h13m) into a timedelta object.

    Modified from virhilo's answer at https://stackoverflow.com/a/4628148/851699

    :param time_str: A string identifying a duration. (eg. 2h13m)
    :return datetime.timedelta: A datetime.timedelta object
    """
    parts = timedelta_regex.match(time_str)

    assert parts is not None

    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)
