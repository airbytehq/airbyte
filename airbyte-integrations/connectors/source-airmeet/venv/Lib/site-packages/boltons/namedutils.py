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

"""\
The ``namedutils`` module defines two lightweight container types:
:class:`namedtuple` and :class:`namedlist`. Both are subtypes of built-in
sequence types, which are very fast and efficient. They simply add
named attribute accessors for specific indexes within themselves.

The :class:`namedtuple` is identical to the built-in
:class:`collections.namedtuple`, with a couple of enhancements,
including a ``__repr__`` more suitable to inheritance.

The :class:`namedlist` is the mutable counterpart to the
:class:`namedtuple`, and is much faster and lighter-weight than
full-blown :class:`object`. Consider this if you're implementing nodes
in a tree, graph, or other mutable data structure. If you want an even
skinnier approach, you'll probably have to look to C.
"""


import sys as _sys
from collections import OrderedDict
from keyword import iskeyword as _iskeyword
from operator import itemgetter as _itemgetter


__all__ = ['namedlist', 'namedtuple']

# Tiny templates

_repr_tmpl = '{name}=%r'

_imm_field_tmpl = '''\
    {name} = _property(_itemgetter({index:d}), doc='Alias for field {index:d}')
'''

_m_field_tmpl = '''\
    {name} = _property(_itemgetter({index:d}), _itemsetter({index:d}), doc='Alias for field {index:d}')
'''

#################################################################
### namedtuple
#################################################################

_namedtuple_tmpl = '''\
class {typename}(tuple):
    '{typename}({arg_list})'

    __slots__ = ()

    _fields = {field_names!r}

    def __new__(_cls, {arg_list}):  # TODO: tweak sig to make more extensible
        'Create new instance of {typename}({arg_list})'
        return _tuple.__new__(_cls, ({arg_list}))

    @classmethod
    def _make(cls, iterable, new=_tuple.__new__, len=len):
        'Make a new {typename} object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != {num_fields:d}:
            raise TypeError('Expected {num_fields:d}'
                            ' arguments, got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        tmpl = self.__class__.__name__ + '({repr_fmt})'
        return tmpl % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new {typename} object replacing field(s) with new values'
        result = _self._make(map(kwds.pop, {field_names!r}, _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    __dict__ = _property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'  # wat
        pass

{field_defs}
'''

def namedtuple(typename, field_names, verbose=False, rename=False):
    """Returns a new subclass of tuple with named fields.

    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with pos args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessible by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """

    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = [str(x) for x in field_names]
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not all(c.isalnum() or c == '_' for c in name)
                or _iskeyword(name)
                or not name
                or name[0].isdigit()
                or name.startswith('_')
                or name in seen):
                field_names[index] = '_%d' % index
            seen.add(name)
    for name in [typename] + field_names:
        if not all(c.isalnum() or c == '_' for c in name):
            raise ValueError('Type names and field names can only contain '
                             'alphanumeric characters and underscores: %r'
                             % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with '
                             'a number: %r' % name)
    seen = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)

    # Fill-in the class template
    fmt_kw = {'typename': typename}
    fmt_kw['field_names'] = tuple(field_names)
    fmt_kw['num_fields'] = len(field_names)
    fmt_kw['arg_list'] = repr(tuple(field_names)).replace("'", "")[1:-1]
    fmt_kw['repr_fmt'] = ', '.join(_repr_tmpl.format(name=name)
                                   for name in field_names)
    fmt_kw['field_defs'] = '\n'.join(_imm_field_tmpl.format(index=index, name=name)
                                     for index, name in enumerate(field_names))
    class_definition = _namedtuple_tmpl.format(**fmt_kw)

    if verbose:
        print(class_definition)

    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(_itemgetter=_itemgetter,
                     __name__='namedtuple_%s' % typename,
                     OrderedDict=OrderedDict,
                     _property=property,
                     _tuple=tuple)
    try:
        exec(class_definition, namespace)
    except SyntaxError as e:
        raise SyntaxError(e.msg + ':\n' + class_definition)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        frame = _sys._getframe(1)
        result.__module__ = frame.f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return result


#################################################################
### namedlist
#################################################################

_namedlist_tmpl = '''\
class {typename}(list):
    '{typename}({arg_list})'

    __slots__ = ()

    _fields = {field_names!r}

    def __new__(_cls, {arg_list}):  # TODO: tweak sig to make more extensible
        'Create new instance of {typename}({arg_list})'
        return _list.__new__(_cls, ({arg_list}))

    def __init__(self, {arg_list}):  # tuple didn't need this but list does
        return _list.__init__(self, ({arg_list}))

    @classmethod
    def _make(cls, iterable, new=_list, len=len):
        'Make a new {typename} object from a sequence or iterable'
        # why did this function exist? why not just star the
        # iterable like below?
        result = cls(*iterable)
        if len(result) != {num_fields:d}:
            raise TypeError('Expected {num_fields:d} arguments,'
                            ' got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        tmpl = self.__class__.__name__ + '({repr_fmt})'
        return tmpl % tuple(self)

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new {typename} object replacing field(s) with new values'
        result = _self._make(map(kwds.pop, {field_names!r}, _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain list.  Used by copy and pickle.'
        return tuple(self)

    __dict__ = _property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'  # wat
        pass

{field_defs}
'''


def namedlist(typename, field_names, verbose=False, rename=False):
    """Returns a new subclass of list with named fields.

    >>> Point = namedlist('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with pos args or keywords
    >>> p[0] + p[1]                     # indexable like a plain list
    33
    >>> x, y = p                        # unpack like a regular list
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessible by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """

    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = [str(x) for x in field_names]
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not all(c.isalnum() or c == '_' for c in name)
                or _iskeyword(name)
                or not name
                or name[0].isdigit()
                or name.startswith('_')
                or name in seen):
                field_names[index] = '_%d' % index
            seen.add(name)
    for name in [typename] + field_names:
        if not all(c.isalnum() or c == '_' for c in name):
            raise ValueError('Type names and field names can only contain '
                             'alphanumeric characters and underscores: %r'
                             % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with '
                             'a number: %r' % name)
    seen = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)

    # Fill-in the class template
    fmt_kw = {'typename': typename}
    fmt_kw['field_names'] = tuple(field_names)
    fmt_kw['num_fields'] = len(field_names)
    fmt_kw['arg_list'] = repr(tuple(field_names)).replace("'", "")[1:-1]
    fmt_kw['repr_fmt'] = ', '.join(_repr_tmpl.format(name=name)
                                   for name in field_names)
    fmt_kw['field_defs'] = '\n'.join(_m_field_tmpl.format(index=index, name=name)
                                     for index, name in enumerate(field_names))
    class_definition = _namedlist_tmpl.format(**fmt_kw)

    if verbose:
        print(class_definition)

    def _itemsetter(key):
        def _itemsetter(obj, value):
            obj[key] = value
        return _itemsetter

    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(_itemgetter=_itemgetter,
                     _itemsetter=_itemsetter,
                     __name__='namedlist_%s' % typename,
                     OrderedDict=OrderedDict,
                     _property=property,
                     _list=list)
    try:
        exec(class_definition, namespace)
    except SyntaxError as e:
        raise SyntaxError(e.msg + ':\n' + class_definition)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to
    # the frame where the named list is created.  Bypass this step in
    # environments where sys._getframe is not defined (Jython for
    # example) or sys._getframe is not defined for arguments greater
    # than 0 (IronPython).
    try:
        frame = _sys._getframe(1)
        result.__module__ = frame.f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return result
