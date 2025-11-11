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

"""Python has a very powerful mapping type at its core: the :class:`dict`
type. While versatile and featureful, the :class:`dict` prioritizes
simplicity and performance. As a result, it does not retain the order
of item insertion [1]_, nor does it store multiple values per key. It
is a fast, unordered 1:1 mapping.

The :class:`OrderedMultiDict` contrasts to the built-in :class:`dict`,
as a relatively maximalist, ordered 1:n subtype of
:class:`dict`. Virtually every feature of :class:`dict` has been
retooled to be intuitive in the face of this added
complexity. Additional methods have been added, such as
:class:`collections.Counter`-like functionality.

A prime advantage of the :class:`OrderedMultiDict` (OMD) is its
non-destructive nature. Data can be added to an :class:`OMD` without being
rearranged or overwritten. The property can allow the developer to
work more freely with the data, as well as make more assumptions about
where input data will end up in the output, all without any extra
work.

One great example of this is the :meth:`OMD.inverted()` method, which
returns a new OMD with the values as keys and the keys as values. All
the data and the respective order is still represented in the inverted
form, all from an operation which would be outright wrong and reckless
with a built-in :class:`dict` or :class:`collections.OrderedDict`.

The OMD has been performance tuned to be suitable for a wide range of
usages, including as a basic unordered MultiDict. Special
thanks to `Mark Williams`_ for all his help.

.. [1] As of 2015, `basic dicts on PyPy are ordered
   <http://morepypy.blogspot.com/2015/01/faster-more-memory-efficient-and-more.html>`_,
   and as of December 2017, `basic dicts in CPython 3 are now ordered
   <https://mail.python.org/pipermail/python-dev/2017-December/151283.html>`_, as
   well.
.. _Mark Williams: https://github.com/markrwilliams

"""

from collections.abc import KeysView, ValuesView, ItemsView
from itertools import zip_longest

try:
    from .typeutils import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


PREV, NEXT, KEY, VALUE, SPREV, SNEXT = range(6)


__all__ = ['MultiDict', 'OMD', 'OrderedMultiDict', 'OneToOne', 'ManyToMany', 'subdict', 'FrozenDict']


class OrderedMultiDict(dict):
    """A MultiDict is a dictionary that can have multiple values per key
    and the OrderedMultiDict (OMD) is a MultiDict that retains
    original insertion order. Common use cases include:

      * handling query strings parsed from URLs
      * inverting a dictionary to create a reverse index (values to keys)
      * stacking data from multiple dictionaries in a non-destructive way

    The OrderedMultiDict constructor is identical to the built-in
    :class:`dict`, and overall the API constitutes an intuitive
    superset of the built-in type:

    >>> omd = OrderedMultiDict()
    >>> omd['a'] = 1
    >>> omd['b'] = 2
    >>> omd.add('a', 3)
    >>> omd.get('a')
    3
    >>> omd.getlist('a')
    [1, 3]

    Some non-:class:`dict`-like behaviors also make an appearance,
    such as support for :func:`reversed`:

    >>> list(reversed(omd))
    ['b', 'a']

    Note that unlike some other MultiDicts, this OMD gives precedence
    to the most recent value added. ``omd['a']`` refers to ``3``, not
    ``1``.

    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> omd.poplast('a')
    3
    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2)])
    >>> omd.pop('a')
    1
    >>> omd
    OrderedMultiDict([('b', 2)])

    If you want a safe-to-modify or flat dictionary, use
    :meth:`OrderedMultiDict.todict()`.

    >>> from pprint import pprint as pp  # preserve printed ordering
    >>> omd = OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> pp(omd.todict())
    {'a': 3, 'b': 2}
    >>> pp(omd.todict(multi=True))
    {'a': [1, 3], 'b': [2]}

    With ``multi=False``, items appear with the keys in to original
    insertion order, alongside the most-recently inserted value for
    that key.

    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).items(multi=False)
    [('a', 3), ('b', 2)]

    .. warning::

       ``dict(omd)`` changed behavior `in Python 3.7
       <https://bugs.python.org/issue34320>`_ due to changes made to
       support the transition from :class:`collections.OrderedDict` to
       the built-in dictionary being ordered. Before 3.7, the result
       would be a new dictionary, with values that were lists, similar
       to ``omd.todict(multi=True)`` (but only shallow-copy; the lists
       were direct references to OMD internal structures). From 3.7
       onward, the values became singular, like
       ``omd.todict(multi=False)``. For reliable cross-version
       behavior, just use :meth:`~OrderedMultiDict.todict()`.

    """
    def __new__(cls, *a, **kw):
        ret = super().__new__(cls)
        ret._clear_ll()
        return ret 
    
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)

    def __getstate__(self):
        return list(self.iteritems(multi=True))

    def __setstate__(self, state):
        self.clear()
        self.update_extend(state)

    def _clear_ll(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def _insert(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def add(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(k, v)
        values.append(v)

    def addlist(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def get(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(k, [default])[-1]

    def getlist(self, k, default=_MISSING):
        """Get all values for key *k* as a list, if *k* is in the
        dictionary, else *default*. The list returned is a copy and
        can be safely mutated. If *default* is not given, an empty
        :class:`list` is returned.
        """
        try:
            return super().__getitem__(k)[:]
        except KeyError:
            if default is _MISSING:
                return []
            return default

    def clear(self):
        "Empty the dictionary."
        super().clear()
        self._clear_ll()

    def setdefault(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super().__contains__(k):
            self[k] = None if default is _MISSING else default
        return self[k]

    def copy(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=True))

    @classmethod
    def fromkeys(cls, keys, default=None):
        """Create a dictionary from a list of keys, with all the values
        set to *default*, or ``None`` if *default* is not set.
        """
        return cls([(k, default) for k in keys])

    def update(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def update_extend(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def __setitem__(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__(k, [v])

    def __getitem__(self, k):
        return super().__getitem__(k)[-1]

    def __delitem__(self, k):
        super().__delitem__(k)
        self._remove_all(k)

    def __eq__(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def __ior__(self, other):
        self.update(other)
        return self

    def pop(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[-1]
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
        return default

    def popall(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def poplast(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def _remove(self, k):
        values = self._map[k]
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not values:
            del self._map[k]

    def _remove_all(self, k):
        values = self._map[k]
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def iteritems(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def iterkeys(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def itervalues(self, multi=False):
        """Iterate over the OMD's values in insertion order. By default,
        yields the most-recently inserted value per unique key.  Set
        *multi* to ``True`` to get all values according to insertion
        order.
        """
        for k, v in self.iteritems(multi=multi):
            yield v

    def todict(self, multi=False):
        """Gets a basic :class:`dict` of the items in this dictionary. Keys
        are the same as the OMD, values are the most recently inserted
        values for each key.

        Setting the *multi* arg to ``True`` is yields the same
        result as calling :class:`dict` on the OMD, except that all the
        value lists are copies that can be safely mutated.
        """
        if multi:
            return {k: self.getlist(k) for k in self}
        return {k: self[k] for k in self}

    def sorted(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), key=key, reverse=reverse))

    def sortedvalues(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def inverted(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__((v, k) for k, v in self.iteritems(multi=True))

    def counts(self):
        """Returns a mapping from key to number of values inserted under that
        key. Like :py:class:`collections.Counter`, but returns a new
        :class:`OrderedMultiDict`.
        """
        # Returns an OMD because Counter/OrderedDict may not be
        # available, and neither Counter nor dict maintain order.
        super_getitem = super().__getitem__
        return self.__class__((k, len(super_getitem(k))) for k in self)

    def keys(self, multi=False):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(self.iterkeys(multi=multi))

    def values(self, multi=False):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(self.itervalues(multi=multi))

    def items(self, multi=False):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
        return list(self.iteritems(multi=multi))

    def __iter__(self):
        return self.iterkeys()

    def __reversed__(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def __repr__(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=True)])
        return f'{cn}([{kvs}])'

    def viewkeys(self):
        "OMD.viewkeys() -> a set-like object providing a view on OMD's keys"
        return KeysView(self)

    def viewvalues(self):
        "OMD.viewvalues() -> an object providing a view on OMD's values"
        return ValuesView(self)

    def viewitems(self):
        "OMD.viewitems() -> a set-like object providing a view on OMD's items"
        return ItemsView(self)


# A couple of convenient aliases
OMD = OrderedMultiDict
MultiDict = OrderedMultiDict


class FastIterOrderedMultiDict(OrderedMultiDict):
    """An OrderedMultiDict backed by a skip list.  Iteration over keys
    is faster and uses constant memory but adding duplicate key-value
    pairs is slower. Brainchild of Mark Williams.
    """
    def _clear_ll(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root,
                        None, None,
                        self.root, self.root]

    def _insert(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def _remove(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def _remove_all(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def iteritems(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def iterkeys(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY]
            curr = curr[next_link]

    def __reversed__(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]


_OTO_INV_MARKER = object()
_OTO_UNIQUE_MARKER = object()


class OneToOne(dict):
    """Implements a one-to-one mapping dictionary. In addition to
    inheriting from and behaving exactly like the builtin
    :class:`dict`, all values are automatically added as keys on a
    reverse mapping, available as the `inv` attribute. This
    arrangement keeps key and value namespaces distinct.

    Basic operations are intuitive:

    >>> oto = OneToOne({'a': 1, 'b': 2})
    >>> print(oto['a'])
    1
    >>> print(oto.inv[1])
    a
    >>> len(oto)
    2

    Overwrites happens in both directions:

    >>> oto.inv[1] = 'c'
    >>> print(oto.get('a'))
    None
    >>> len(oto)
    2

    For a very similar project, with even more one-to-one
    functionality, check out `bidict <https://github.com/jab/bidict>`_.
    """
    __slots__ = ('inv',)

    def __init__(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    @classmethod
    def unique(cls, *a, **kw):
        """This alternate constructor for OneToOne will raise an exception
        when input values overlap. For instance:

        >>> OneToOne.unique({'a': 1, 'b': 1})
        Traceback (most recent call last):
        ...
        ValueError: expected unique values, got multiple keys for the following values: ...

        This even works across inputs:

        >>> a_dict = {'a': 2}
        >>> OneToOne.unique(a_dict, b=2)
        Traceback (most recent call last):
        ...
        ValueError: expected unique values, got multiple keys for the following values: ...
        """
        return cls(_OTO_UNIQUE_MARKER, *a, **kw)

    def __setitem__(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def __delitem__(self, key):
        dict.__delitem__(self.inv, self[key])
        dict.__delitem__(self, key)

    def clear(self):
        dict.clear(self)
        dict.clear(self.inv)

    def copy(self):
        return self.__class__(self)

    def pop(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(self, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def popitem(self):
        key, val = dict.popitem(self)
        dict.__delitem__(self.inv, val)
        return key, val

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def update(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def __repr__(self):
        cn = self.__class__.__name__
        dict_repr = dict.__repr__(self)
        return f"{cn}({dict_repr})"


# marker for the secret handshake used internally to set up the invert ManyToMany
_PAIRING = object()


class ManyToMany:
    """
    a dict-like entity that represents a many-to-many relationship
    between two groups of objects

    behaves like a dict-of-tuples; also has .inv which is kept
    up to date which is a dict-of-tuples in the other direction

    also, can be used as a directed graph among hashable python objects
    """
    def __init__(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return

    def get(self, key, default=frozenset()):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        return frozenset(self.data[key])

    def __setitem__(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def __delitem__(self, key):
        for val in self.data.pop(key):
            self.inv.data[val].remove(key)
            if not self.inv.data[val]:
                del self.inv.data[val]

    def update(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def add(self, key, val):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(val)
        if val not in self.inv.data:
            self.inv.data[val] = set()
        self.inv.data[val].add(key)

    def remove(self, key, val):
        self.data[key].remove(val)
        if not self.data[key]:
            del self.data[key]
        self.inv.data[val].remove(key)
        if not self.inv.data[val]:
            del self.inv.data[val]

    def replace(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key not in self.data:
            return
        self.data[newkey] = fwdset = self.data.pop(key)
        for val in fwdset:
            revset = self.inv.data[val]
            revset.remove(key)
            revset.add(newkey)

    def iteritems(self):
        for key in self.data:
            for val in self.data[key]:
                yield key, val

    def keys(self):
        return self.data.keys()

    def __contains__(self, key):
        return key in self.data

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return self.data.__len__()

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data

    def __repr__(self):
        cn = self.__class__.__name__
        return f'{cn}({list(self.iteritems())!r})'


def subdict(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


class FrozenHashError(TypeError):
    pass


class FrozenDict(dict):
    """An immutable dict subtype that is hashable and can itself be used
    as a :class:`dict` key or :class:`set` entry. What
    :class:`frozenset` is to :class:`set`, FrozenDict is to
    :class:`dict`.

    There was once an attempt to introduce such a type to the standard
    library, but it was rejected: `PEP 416 <https://www.python.org/dev/peps/pep-0416/>`_.

    Because FrozenDict is a :class:`dict` subtype, it automatically
    works everywhere a dict would, including JSON serialization.

    """
    __slots__ = ('_hash',)

    def updated(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = dict(self)
        data.update(*a, **kw)
        return type(self)(data)

    @classmethod
    def fromkeys(cls, keys, value=None):
        # one of the lesser known and used/useful dict methods
        return cls(dict.fromkeys(keys, value))

    def __repr__(self):
        cn = self.__class__.__name__
        return f'{cn}({dict.__repr__(self)})'

    def __reduce_ex__(self, protocol):
        return type(self), (dict(self),)

    def __hash__(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = hash(frozenset(self.items()))
            except Exception as e:
                ret = self._hash = FrozenHashError(e)

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def __copy__(self):
        return self  # immutable types don't copy, see tuple's behavior

    # block everything else
    def _raise_frozen_typeerror(self, *a, **kw):
        "raises a TypeError, because FrozenDicts are immutable"
        raise TypeError('%s object is immutable' % self.__class__.__name__)

    __ior__ = __setitem__ = __delitem__ = update = _raise_frozen_typeerror
    setdefault = pop = popitem = clear = _raise_frozen_typeerror

    del _raise_frozen_typeerror


# end dictutils.py
