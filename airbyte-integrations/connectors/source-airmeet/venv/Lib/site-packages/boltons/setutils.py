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

The :class:`set` type brings the practical expressiveness of
set theory to Python. It has a very rich API overall, but lacks a
couple of fundamental features. For one, sets are not ordered. On top
of this, sets are not indexable, i.e, ``my_set[8]`` will raise an
:exc:`TypeError`. The :class:`IndexedSet` type remedies both of these
issues without compromising on the excellent complexity
characteristics of Python's built-in set implementation.
"""


from bisect import bisect_left
from collections.abc import MutableSet
from itertools import chain, islice
import operator

try:
    from .typeutils import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


__all__ = ['IndexedSet', 'complement']


_COMPACTION_FACTOR = 8

# TODO: inherit from set()
# TODO: .discard_many(), .remove_many()
# TODO: raise exception on non-set params?
# TODO: technically reverse operators should probably reverse the
# order of the 'other' inputs and put self last (to try and maintain
# insertion order)


class IndexedSet(MutableSet):
    """``IndexedSet`` is a :class:`collections.MutableSet` that maintains
    insertion order and uniqueness of inserted elements. It's a hybrid
    type, mostly like an OrderedSet, but also :class:`list`-like, in
    that it supports indexing and slicing.

    Args:
        other (iterable): An optional iterable used to initialize the set.

    >>> x = IndexedSet(list(range(4)) + list(range(8)))
    >>> x
    IndexedSet([0, 1, 2, 3, 4, 5, 6, 7])
    >>> x - set(range(2))
    IndexedSet([2, 3, 4, 5, 6, 7])
    >>> x[-1]
    7
    >>> fcr = IndexedSet('freecreditreport.com')
    >>> ''.join(fcr[:fcr.index('.')])
    'frecditpo'

    Standard set operators and interoperation with :class:`set` are
    all supported:

    >>> fcr & set('cash4gold.com')
    IndexedSet(['c', 'd', 'o', '.', 'm'])

    As you can see, the ``IndexedSet`` is almost like a ``UniqueList``,
    retaining only one copy of a given value, in the order it was
    first added. For the curious, the reason why IndexedSet does not
    support setting items based on index (i.e, ``__setitem__()``),
    consider the following dilemma::

      my_indexed_set = [A, B, C, D]
      my_indexed_set[2] = A

    At this point, a set requires only one *A*, but a :class:`list` would
    overwrite *C*. Overwriting *C* would change the length of the list,
    meaning that ``my_indexed_set[2]`` would not be *A*, as expected with a
    list, but rather *D*. So, no ``__setitem__()``.

    Otherwise, the API strives to be as complete a union of the
    :class:`list` and :class:`set` APIs as possible.
    """
    def __init__(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        self._compactions = 0
        self._c_max_size = 0
        if other:
            self.update(other)

    # internal functions
    @property
    def _dead_index_count(self):
        return len(self.item_list) - len(self.item_index_map)

    def _compact(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def _cull(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def _get_real_index(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def _get_apparent_index(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def _add_dead(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    # common operations (shared by set and list)
    def __len__(self):
        return len(self.item_index_map)

    def __contains__(self, item):
        return item in self.item_index_map

    def __iter__(self):
        return (item for item in self.item_list if item is not _MISSING)

    def __reversed__(self):
        item_list = self.item_list
        return (item for item in reversed(item_list) if item is not _MISSING)

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self)!r})'

    def __eq__(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        try:
            return set(self) == set(other)
        except TypeError:
            return False

    @classmethod
    def from_iterable(cls, it):
        "from_iterable(it) -> create a set from an iterable"
        return cls(it)

    # set operations
    def add(self, item):
        "add(item) -> add item to the set"
        if item not in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(item)

    def remove(self, item):
        "remove(item) -> remove item from the set, raises if not present"
        try:
            didx = self.item_index_map.pop(item)
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = _MISSING
        self._add_dead(didx)
        self._cull()

    def discard(self, item):
        "discard(item) -> discard item from the set (does not raise)"
        try:
            self.remove(item)
        except KeyError:
            pass

    def clear(self):
        "clear() -> empty the set"
        del self.item_list[:]
        del self.dead_indices[:]
        self.item_index_map.clear()

    def isdisjoint(self, other):
        "isdisjoint(other) -> return True if no overlap with other"
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return True

    def issubset(self, other):
        "issubset(other) -> return True if other contains this set"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def issuperset(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def union(self, *others):
        "union(*others) -> return a new set containing this set and others"
        return self.from_iterable(chain(self, *others))

    def iter_intersection(self, *others):
        "iter_intersection(*others) -> iterate over elements also in others"
        for k in self:
            for other in others:
                if k not in other:
                    break
            else:
                yield k
        return

    def intersection(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def iter_difference(self, *others):
        "iter_difference(*others) -> iterate over elements not in others"
        for k in self:
            for other in others:
                if k in other:
                    break
            else:
                yield k
        return

    def difference(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def symmetric_difference(self, *others):
        "symmetric_difference(*others) -> XOR set of this and others"
        ret = self.union(*others)
        return ret.difference(self.intersection(*others))

    __or__  = __ror__  = union
    __and__ = __rand__ = intersection
    __sub__ = difference
    __xor__ = __rxor__ = symmetric_difference

    def __rsub__(self, other):
        vals = [x for x in other if x not in self]
        return type(other)(vals)

    # in-place set operations
    def update(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    def intersection_update(self, *others):
        "intersection_update(*others) -> discard self.difference(*others)"
        for val in self.difference(*others):
            self.discard(val)

    def difference_update(self, *others):
        "difference_update(*others) -> discard self.intersection(*others)"
        if self in others:
            self.clear()
        for val in self.intersection(*others):
            self.discard(val)

    def symmetric_difference_update(self, other):  # note singular 'other'
        "symmetric_difference_update(other) -> in-place XOR with other"
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(val)

    def __ior__(self, *others):
        self.update(*others)
        return self

    def __iand__(self, *others):
        self.intersection_update(*others)
        return self

    def __isub__(self, *others):
        self.difference_update(*others)
        return self

    def __ixor__(self, *others):
        self.symmetric_difference_update(*others)
        return self

    def iter_slice(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    # list operations
    def __getitem__(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    def pop(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def count(self, val):
        "count(val) -> count number of instances of value (0 or 1)"
        if val in self.item_index_map:
            return 1
        return 0

    def reverse(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = list(reversed(self))
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def sort(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(self, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def index(self, val):
        "index(val) -> get the index of a value, raises if not present"
        try:
            return self._get_apparent_index(self.item_index_map[val])
        except KeyError:
            cn = self.__class__.__name__
            raise ValueError(f'{val!r} is not in {cn}')


def complement(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=set(wrapped))


def _norm_args_typeerror(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def _norm_args_notimplemented(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        return NotImplemented, None
    return inc, exc


class _ComplementSet:
    """
    helper class for complement() that implements the set methods
    """
    __slots__ = ('_included', '_excluded')

    def __init__(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def __repr__(self):
        if self._included is None:
            return f'complement({repr(self._excluded)})'
        return f'complement(complement({repr(self._included)}))'

    def complemented(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    __invert__ = complemented

    def complement(self):
        '''convert the current set to its complement in-place'''
        self._included, self._excluded = self._excluded, self._included

    def __contains__(self, item):
        if self._included is None:
            return not item in self._excluded
        return item in self._included

    def add(self, item):
        if self._included is None:
            if item in self._excluded:
                self._excluded.remove(item)
        else:
            self._included.add(item)

    def remove(self, item):
        if self._included is None:
            self._excluded.add(item)
        else:
            self._included.remove(item)

    def pop(self):
        if self._included is None:
            raise NotImplementedError  # self.missing.add(random.choice(gc.objects()))
        return self._included.pop()

    def intersection(self, other):
        try:
            return self & other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def __and__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    __rand__ = __and__

    def __iand__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def union(self, other):
        try:
            return self | other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def __or__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    __ror__ = __or__

    def __ior__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def update(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def discard(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def symmetric_difference(self, other):
        try:
            return self ^ other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def __xor__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    __rxor__ = __xor__

    def symmetric_difference_update(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def isdisjoint(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def issubset(self, other):
        '''everything missing from other is also missing from self'''
        try:
            return self <= other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def __le__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def __lt__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def issuperset(self, other):
        '''everything missing from self is also missing from super'''
        try:
            return self >= other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def __ge__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def __gt__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def difference(self, other):
        try:
            return self - other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def __sub__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def __rsub__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def difference_update(self, other):
        try:
            self -= other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def __isub__(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def __hash__(self):
        return hash(self._included) ^ hash(self._excluded)

    def __len__(self):
        if self._included is not None:
            return len(self._included)
        raise NotImplementedError('complemented sets have undefined length')

    def __iter__(self):
        if self._included is not None:
            return iter(self._included)
        raise NotImplementedError('complemented sets have undefined contents')

    def __bool__(self):
        if self._included is not None:
            return bool(self._included)
        return True

