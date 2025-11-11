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

"""If there is one recurring theme in ``boltons``, it is that Python
has excellent datastructures that constitute a good foundation for
most quick manipulations, as well as building applications. However,
Python usage has grown much faster than builtin data structure
power. Python has a growing need for more advanced general-purpose
data structures which behave intuitively.

The :class:`Table` class is one example. When handed one- or
two-dimensional data, it can provide useful, if basic, text and HTML
renditions of small to medium sized data. It also heuristically
handles recursive data of various formats (lists, dicts, namedtuples,
objects).

For more advanced :class:`Table`-style manipulation check out the
`pandas`_ DataFrame.

.. _pandas: http://pandas.pydata.org/

"""


from html import escape as html_escape
import types
from itertools import islice
from collections.abc import Sequence, Mapping, MutableSequence

try:
    from .typeutils import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()

"""
Some idle feature thoughts:

* shift around column order without rearranging data
* gotta make it so you can add additional items, not just initialize with
* maybe a shortcut would be to allow adding of Tables to other Tables
* what's the perf of preallocating lists and overwriting items versus
  starting from empty?
* is it possible to effectively tell the difference between when a
  Table is from_data()'d with a single row (list) or with a list of lists?
* CSS: white-space pre-line or pre-wrap maybe?
* Would be nice to support different backends (currently uses lists
  exclusively). Sometimes large datasets come in list-of-dicts and
  list-of-tuples format and it's desirable to cut down processing overhead.

TODO: make iterable on rows?
"""

__all__ = ['Table']


def to_text(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def escape_html(obj, maxlen=None):
    text = to_text(obj, maxlen=maxlen)
    return html_escape(text, quote=True)


_DNR = {type(None), bool, complex, float, type(NotImplemented), slice,
        str, bytes, int,
        types.FunctionType, types.MethodType,
        types.BuiltinFunctionType, types.GeneratorType}


class UnsupportedData(TypeError):
    pass


class InputType:
    def __init__(self, *a, **kw):
        pass

    def get_entry_seq(self, data_seq, headers):
        return [self.get_entry(entry, headers) for entry in data_seq]


class DictInputType(InputType):
    def check_type(self, obj):
        return isinstance(obj, Mapping)

    def guess_headers(self, obj):
        return sorted(obj.keys())

    def get_entry(self, obj, headers):
        return [obj.get(h) for h in headers]

    def get_entry_seq(self, obj, headers):
        return [[ci.get(h) for h in headers] for ci in obj]


class ObjectInputType(InputType):
    def check_type(self, obj):
        return type(obj) not in _DNR and hasattr(obj, '__class__')

    def guess_headers(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def get_entry(self, obj, headers):
        values = []
        for h in headers:
            try:
                values.append(getattr(obj, h))
            except Exception:
                values.append(None)
        return values


# might be better to hardcode list support since it's so close to the
# core or might be better to make this the copy-style from_* importer
# and have the non-copy style be hardcoded in __init__
class ListInputType(InputType):
    def check_type(self, obj):
        return isinstance(obj, MutableSequence)

    def guess_headers(self, obj):
        return None

    def get_entry(self, obj, headers):
        return obj

    def get_entry_seq(self, obj_seq, headers):
        return obj_seq


class TupleInputType(InputType):
    def check_type(self, obj):
        return isinstance(obj, tuple)

    def guess_headers(self, obj):
        return None

    def get_entry(self, obj, headers):
        return list(obj)

    def get_entry_seq(self, obj_seq, headers):
        return [list(t) for t in obj_seq]


class NamedTupleInputType(InputType):
    def check_type(self, obj):
        return hasattr(obj, '_fields') and isinstance(obj, tuple)

    def guess_headers(self, obj):
        return list(obj._fields)

    def get_entry(self, obj, headers):
        return [getattr(obj, h, None) for h in headers]

    def get_entry_seq(self, obj_seq, headers):
        return [[getattr(obj, h, None) for h in headers] for obj in obj_seq]


class Table:
    """
    This Table class is meant to be simple, low-overhead, and extensible. Its
    most common use would be for translation between in-memory data
    structures and serialization formats, such as HTML and console-ready text.

    As such, it stores data in list-of-lists format, and *does not* copy
    lists passed in. It also reserves the right to modify those lists in a
    "filling" process, whereby short lists are extended to the width of
    the table (usually determined by number of headers). This greatly
    reduces overhead and processing/validation that would have to occur
    otherwise.

    General description of headers behavior:

    Headers describe the columns, but are not part of the data, however,
    if the *headers* argument is omitted, Table tries to infer header
    names from the data. It is possible to have a table with no headers,
    just pass in ``headers=None``.

    Supported inputs:

    * :class:`list` of :class:`list` objects
    * :class:`dict` (list/single)
    * :class:`object` (list/single)
    * :class:`collections.namedtuple` (list/single)
    * TODO: DB API cursor?
    * TODO: json

    Supported outputs:

    * HTML
    * Pretty text (also usable as GF Markdown)
    * TODO: CSV
    * TODO: json
    * TODO: json lines

    To minimize resident size, the Table data is stored as a list of lists.
    """

    # order definitely matters here
    _input_types = [DictInputType(), ListInputType(),
                    NamedTupleInputType(), TupleInputType(),
                    ObjectInputType()]

    _html_tr, _html_tr_close = '<tr>', '</tr>'
    _html_th, _html_th_close = '<th>', '</th>'
    _html_td, _html_td_close = '<td>', '</td>'
    _html_thead, _html_thead_close = '<thead>', '</thead>'
    _html_tbody, _html_tbody_close = '<tbody>', '</tbody>'

    # _html_tfoot, _html_tfoot_close = '<tfoot>', '</tfoot>'
    _html_table_tag, _html_table_tag_close = '<table>', '</table>'

    def __init__(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def extend(self, data):
        """
        Append the given data to the end of the Table.
        """
        if not data:
            return
        self._data.extend(data)
        self._set_width()
        self._fill()

    def _set_width(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = max([len(d) for d in self._data])

    def _fill(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 0:
                d.extend(filler * rem)
        return

    @classmethod
    def from_dict(cls, data, headers=_MISSING, max_depth=1, metadata=None):
        """Create a Table from a :class:`dict`. Operates the same as
        :meth:`from_data`, but forces interpretation of the data as a
        Mapping.
        """
        return cls.from_data(data=data, headers=headers,
                             max_depth=max_depth, _data_type=DictInputType(),
                             metadata=metadata)

    @classmethod
    def from_list(cls, data, headers=_MISSING, max_depth=1, metadata=None):
        """Create a Table from a :class:`list`. Operates the same as
        :meth:`from_data`, but forces the interpretation of the data
        as a Sequence.
        """
        return cls.from_data(data=data, headers=headers,
                             max_depth=max_depth, _data_type=ListInputType(),
                             metadata=metadata)

    @classmethod
    def from_object(cls, data, headers=_MISSING, max_depth=1, metadata=None):
        """Create a Table from an :class:`object`. Operates the same as
        :meth:`from_data`, but forces the interpretation of the data
        as an object. May be useful for some :class:`dict` and
        :class:`list` subtypes.
        """
        return cls.from_data(data=data, headers=headers,
                             max_depth=max_depth, _data_type=ObjectInputType(),
                             metadata=metadata)

    @classmethod
    def from_data(cls, data, headers=_MISSING, max_depth=1, **kwargs):

        """Create a Table from any supported data, heuristically
        selecting how to represent the data in Table format.

        Args:
            data (object): Any object or iterable with data to be
                imported to the Table.

            headers (iterable): An iterable of headers to be matched
                to the data. If not explicitly passed, headers will be
                guessed for certain datatypes.

            max_depth (int): The level to which nested Tables should
                be created (default: 1).

            _data_type (InputType subclass): For advanced use cases,
                do not guess the type of the input data, use this data
                type instead.
        """
        # TODO: seen/cycle detection/reuse ?
        # maxdepth follows the same behavior as find command
        # i.e., it doesn't work if max_depth=0 is passed in
        metadata = kwargs.pop('metadata', None)
        _data_type = kwargs.pop('_data_type', None)

        if max_depth < 1:
            # return data instead?
            return cls(headers=headers, metadata=metadata)
        is_seq = isinstance(data, Sequence)
        if is_seq:
            if not data:
                return cls(headers=headers, metadata=metadata)
            to_check = data[0]
            if not _data_type:
                for it in cls._input_types:
                    if it.check_type(to_check):
                        _data_type = it
                        break
                else:
                    # not particularly happy about this rewind-y approach
                    is_seq = False
                    to_check = data
        else:
            if type(data) in _DNR:
                # hmm, got scalar data.
                # raise an exception or make an exception, nahmsayn?
                return cls([[data]], headers=headers, metadata=metadata)
            to_check = data
        if not _data_type:
            for it in cls._input_types:
                if it.check_type(to_check):
                    _data_type = it
                    break
            else:
                raise UnsupportedData('unsupported data type %r'
                                      % type(data))
        if headers is _MISSING:
            headers = _data_type.guess_headers(to_check)
        if is_seq:
            entries = _data_type.get_entry_seq(data, headers)
        else:
            entries = [_data_type.get_entry(data, headers)]
        if max_depth > 1:
            new_max_depth = max_depth - 1
            for i, entry in enumerate(entries):
                for j, cell in enumerate(entry):
                    if type(cell) in _DNR:
                        # optimization to avoid function overhead
                        continue
                    try:
                        entries[i][j] = cls.from_data(cell,
                                                      max_depth=new_max_depth)
                    except UnsupportedData:
                        continue
        return cls(entries, headers=headers, metadata=metadata)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, idx):
        return self._data[idx]

    def __repr__(self):
        cn = self.__class__.__name__
        if self.headers:
            return f'{cn}(headers={self.headers!r}, data={self._data!r})'
        else:
            return f'{cn}({self._data!r})'

    def to_html(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def get_cell_html(self, value):
        """Called on each value in an HTML table. By default it simply escapes
        the HTML. Override this method to add additional conditions
        and behaviors, but take care to ensure the final output is
        HTML escaped.
        """
        return escape_html(value)

    def _add_horizontal_html_lines(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def _add_vertical_html_lines(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def to_text(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(cur) for cur in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)
