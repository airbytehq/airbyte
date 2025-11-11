# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Python's :mod:`datetime` module provides some of the most complex
and powerful primitives in the Python standard library. Time is
nontrivial, but thankfully its support is first-class in
Python. ``dateutils`` provides some additional tools for working with
time.

Additionally, timeutils provides a few basic utilities for working
with timezones in Python. The Python :mod:`datetime` module's
documentation describes how to create a
:class:`~datetime.datetime`-compatible :class:`~datetime.tzinfo`
subtype. It even provides a few examples.

The following module defines usable forms of the timezones in those
docs, as well as a couple other useful ones, :data:`UTC` (aka GMT) and
:data:`LocalTZ` (representing the local timezone as configured in the
operating system). For timezones beyond these, as well as a higher
degree of accuracy in corner cases, check out `pytz`_ and `dateutil`_.

.. _pytz: https://pypi.python.org/pypi/pytz
.. _dateutil: https://dateutil.readthedocs.io/en/stable/index.html
"""

import re
import time
import bisect
import operator
from datetime import tzinfo, timedelta, date, datetime, timezone


# For legacy compatibility.
# boltons used to offer an implementation of total_seconds for Python <2.7
total_seconds = timedelta.total_seconds


def dt_to_timestamp(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt - EPOCH_AWARE
    else:
        td = dt.replace(tzinfo=timezone.utc) - EPOCH_AWARE
    return timedelta.total_seconds(td)


_NONDIGIT_RE = re.compile(r'\D')


def isoparse(iso_str):
    """Parses the limited subset of `ISO8601-formatted time`_ strings as
    returned by :meth:`datetime.datetime.isoformat`.

    >>> epoch_dt = datetime.fromtimestamp(0, timezone.utc).replace(tzinfo=None)
    >>> iso_str = epoch_dt.isoformat()
    >>> print(iso_str)
    1970-01-01T00:00:00
    >>> isoparse(iso_str)
    datetime.datetime(1970, 1, 1, 0, 0)

    >>> utcnow = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> utcnow == isoparse(utcnow.isoformat())
    True

    For further datetime parsing, see the `iso8601`_ package for strict
    ISO parsing and `dateutil`_ package for loose parsing and more.

    .. _ISO8601-formatted time: https://en.wikipedia.org/wiki/ISO_8601
    .. _iso8601: https://pypi.python.org/pypi/iso8601
    .. _dateutil: https://pypi.python.org/pypi/python-dateutil

    """
    dt_args = [int(p) for p in _NONDIGIT_RE.split(iso_str)]
    return datetime(*dt_args)


_BOUNDS = [(0, timedelta(seconds=1), 'second'),
           (1, timedelta(seconds=60), 'minute'),
           (1, timedelta(seconds=3600), 'hour'),
           (1, timedelta(days=1), 'day'),
           (1, timedelta(days=7), 'week'),
           (2, timedelta(days=30), 'month'),
           (1, timedelta(days=365), 'year')]
_BOUNDS = [(b[0] * b[1], b[1], b[2]) for b in _BOUNDS]
_BOUND_DELTAS = [b[0] for b in _BOUNDS]

_FLOAT_PATTERN = r'[+-]?\ *(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
_PARSE_TD_RE = re.compile(r"((?P<value>%s)\s*(?P<unit>\w)\w*)" % _FLOAT_PATTERN)
_PARSE_TD_KW_MAP = {unit[0]: unit + 's'
                         for _, _, unit in reversed(_BOUNDS[:-2])}


def parse_timedelta(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


parse_td = parse_timedelta  # legacy alias


def _cardinalize_time_unit(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value == 1:
        return unit
    return unit + 's'


def decimal_relative_time(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def relative_time(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def strpdate(string, format):
    """Parse the date string according to the format in `format`.  Returns a
    :class:`date` object.  Internally, :meth:`datetime.strptime` is used to
    parse the string and thus conversion specifiers for time fields (e.g. `%H`)
    may be provided;  these will be parsed but ignored.

    Args:
        string (str): The date string to be parsed.
        format (str): The `strptime`_-style date format string.
    Returns:
        datetime.date

    .. _`strptime`: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

    >>> strpdate('2016-02-14', '%Y-%m-%d')
    datetime.date(2016, 2, 14)
    >>> strpdate('26/12 (2015)', '%d/%m (%Y)')
    datetime.date(2015, 12, 26)
    >>> strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    datetime.date(2015, 12, 31)
    >>> strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    datetime.date(2016, 1, 1)
    """
    whence = datetime.strptime(string, format)
    return whence.date()


def daterange(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


# Timezone support (brought in from tzutils)


ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class ConstantTZInfo(tzinfo):
    """
    A :class:`~datetime.tzinfo` subtype whose *offset* remains constant
    (no daylight savings).

    Args:
        name (str): Name of the timezone.
        offset (datetime.timedelta): Offset of the timezone.
    """
    def __init__(self, name="ConstantTZ", offset=ZERO):
        self.name = name
        self.offset = offset

    @property
    def utcoffset_hours(self):
        return timedelta.total_seconds(self.offset) / (60 * 60)

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        cn = self.__class__.__name__
        return f'{cn}(name={self.name!r}, offset={self.offset!r})'


UTC = ConstantTZInfo('UTC')
EPOCH_AWARE = datetime.fromtimestamp(0, UTC)


class LocalTZInfo(tzinfo):
    """The ``LocalTZInfo`` type takes data available in the time module
    about the local timezone and makes a practical
    :class:`datetime.tzinfo` to represent the timezone settings of the
    operating system.

    For a more in-depth integration with the operating system, check
    out `tzlocal`_. It builds on `pytz`_ and implements heuristics for
    many versions of major operating systems to provide the official
    ``pytz`` tzinfo, instead of the LocalTZ generalization.

    .. _tzlocal: https://pypi.python.org/pypi/tzlocal
    .. _pytz: https://pypi.python.org/pypi/pytz

    """
    _std_offset = timedelta(seconds=-time.timezone)
    _dst_offset = _std_offset
    if time.daylight:
        _dst_offset = timedelta(seconds=-time.altzone)

    def is_dst(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 0

    def utcoffset(self, dt):
        if self.is_dst(dt):
            return self._dst_offset
        return self._std_offset

    def dst(self, dt):
        if self.is_dst(dt):
            return self._dst_offset - self._std_offset
        return ZERO

    def tzname(self, dt):
        return time.tzname[self.is_dst(dt)]

    def __repr__(self):
        return '%s()' % self.__class__.__name__


LocalTZ = LocalTZInfo()


def _first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


# US DST Rules
#
# This is a simplified (i.e., wrong for a few cases) set of rules for US
# DST start and end times. For a complete and up-to-date set of DST rules
# and timezone definitions, visit the Olson Database (or try pytz):
# http://www.twinsun.com/tz/tz-link.htm
# http://sourceforge.net/projects/pytz/ (might not be up-to-date)
#
# In the US, since 2007, DST starts at 2am (standard time) on the second
# Sunday in March, which is the first Sunday on or after Mar 8.
DSTSTART_2007 = datetime(1, 3, 8, 2)
# and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
DSTEND_2007 = datetime(1, 11, 1, 1)
# From 1987 to 2006, DST used to start at 2am (standard time) on the first
# Sunday in April and to end at 2am (DST time; 1am standard time) on the last
# Sunday of October, which is the first Sunday on or after Oct 25.
DSTSTART_1987_2006 = datetime(1, 4, 1, 2)
DSTEND_1987_2006 = datetime(1, 10, 25, 1)
# From 1967 to 1986, DST used to start at 2am (standard time) on the last
# Sunday in April (the one on or after April 24) and to end at 2am (DST time;
# 1am standard time) on the last Sunday of October, which is the first Sunday
# on or after Oct 25.
DSTSTART_1967_1986 = datetime(1, 4, 24, 2)
DSTEND_1967_1986 = DSTEND_1987_2006


class USTimeZone(tzinfo):
    """Copied directly from the Python docs, the ``USTimeZone`` is a
    :class:`datetime.tzinfo` subtype used to create the
    :data:`Eastern`, :data:`Central`, :data:`Mountain`, and
    :data:`Pacific` tzinfo types.
    """
    def __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO


Eastern = USTimeZone(-5, "Eastern",  "EST", "EDT")
Central = USTimeZone(-6, "Central",  "CST", "CDT")
Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific = USTimeZone(-8, "Pacific",  "PST", "PDT")
