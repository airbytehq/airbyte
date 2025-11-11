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

"""`PEP 3101`_ introduced the :meth:`str.format` method, and what
would later be called "new-style" string formatting. For the sake of
explicit correctness, it is probably best to refer to Python's dual
string formatting capabilities as *bracket-style* and
*percent-style*. There is overlap, but one does not replace the
other.

  * Bracket-style is more pluggable, slower, and uses a method.
  * Percent-style is simpler, faster, and uses an operator.

Bracket-style formatting brought with it a much more powerful toolbox,
but it was far from a full one. :meth:`str.format` uses `more powerful
syntax`_, but `the tools and idioms`_ for working with
that syntax are not well-developed nor well-advertised.

``formatutils`` adds several functions for working with bracket-style
format strings:

  * :class:`DeferredValue`: Defer fetching or calculating a value
    until format time.
  * :func:`get_format_args`: Parse the positional and keyword
    arguments out of a format string.
  * :func:`tokenize_format_str`: Tokenize a format string into
    literals and :class:`BaseFormatField` objects.
  * :func:`construct_format_field_str`: Assists in programmatic
    construction of format strings.
  * :func:`infer_positional_format_args`: Converts anonymous
    references in 2.7+ format strings to explicit positional arguments
    suitable for usage with Python 2.6.

.. _more powerful syntax: https://docs.python.org/2/library/string.html#format-string-syntax
.. _the tools and idioms: https://docs.python.org/2/library/string.html#string-formatting
.. _PEP 3101: https://www.python.org/dev/peps/pep-3101/
"""
# TODO: also include percent-formatting utils?
# TODO: include lithoxyl.formatters.Formatter (or some adaptation)?


import re
from string import Formatter

__all__ = ['DeferredValue', 'get_format_args', 'tokenize_format_str',
           'construct_format_field_str', 'infer_positional_format_args',
           'BaseFormatField']


_pos_farg_re = re.compile('({{)|'         # escaped open-brace
                          '(}})|'         # escaped close-brace
                          r'({[:!.\[}])')  # anon positional format arg


def construct_format_field_str(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def split_format_str(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def infer_positional_format_args(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


# This approach is hardly exhaustive but it works for most builtins
_INTCHARS = 'bcdoxXn'
_FLOATCHARS = 'eEfFgGn%'
_TYPE_MAP = dict([(x, int) for x in _INTCHARS] +
                 [(x, float) for x in _FLOATCHARS])
_TYPE_MAP['s'] = str


def get_format_args(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def tokenize_format_str(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


class BaseFormatField:
    """A class representing a reference to an argument inside of a
    bracket-style format string. For instance, in ``"{greeting},
    world!"``, there is a field named "greeting".

    These fields can have many options applied to them. See the
    Python docs on `Format String Syntax`_ for the full details.

    .. _Format String Syntax: https://docs.python.org/2/library/string.html#string-formatting
    """
    def __init__(self, fname, fspec='', conv=None):
        self.set_fname(fname)
        self.set_fspec(fspec)
        self.set_conv(conv)

    def set_fname(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def set_fspec(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def set_conv(self, conv):
        """There are only two built-in converters: ``s`` and ``r``. They are
        somewhat rare and appearlike ``"{ref!r}"``."""
        # TODO
        self.conv = conv
        self.conv_func = None  # TODO

    @property
    def fstr(self):
        "The current state of the field in string format."
        return construct_format_field_str(self.fname, self.fspec, self.conv)

    def __repr__(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def __str__(self):
        return self.fstr


_UNSET = object()


class DeferredValue:
    """:class:`DeferredValue` is a wrapper type, used to defer computing
    values which would otherwise be expensive to stringify and
    format. This is most valuable in areas like logging, where one
    would not want to waste time formatting a value for a log message
    which will subsequently be filtered because the message's log
    level was DEBUG and the logger was set to only emit CRITICAL
    messages.

    The :class:``DeferredValue`` is initialized with a callable that
    takes no arguments and returns the value, which can be of any
    type. By default DeferredValue only calls that callable once, and
    future references will get a cached value. This behavior can be
    disabled by setting *cache_value* to ``False``.

    Args:

        func (function): A callable that takes no arguments and
            computes the value being represented.
        cache_value (bool): Whether subsequent usages will call *func*
            again. Defaults to ``True``.

    >>> import sys
    >>> dv = DeferredValue(lambda: len(sys._current_frames()))
    >>> output = "works great in all {0} threads!".format(dv)

    PROTIP: To keep lines shorter, use: ``from formatutils import
    DeferredValue as DV``
    """
    def __init__(self, func, cache_value=True):
        self.func = func
        self.cache_value = cache_value
        self._value = _UNSET

    def get_value(self):
        """Computes, optionally caches, and returns the value of the
        *func*. If ``get_value()`` has been called before, a cached
        value may be returned depending on the *cache_value* option
        passed to the constructor.
        """
        if self._value is not _UNSET and self.cache_value:
            value = self._value
        else:
            value = self.func()
            if self.cache_value:
                self._value = value
        return value

    def __int__(self):
        return int(self.get_value())

    def __float__(self):
        return float(self.get_value())

    def __str__(self):
        return str(self.get_value())

    def __unicode__(self):
        return str(self.get_value())

    def __repr__(self):
        return repr(self.get_value())

    def __format__(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

# end formatutils.py
