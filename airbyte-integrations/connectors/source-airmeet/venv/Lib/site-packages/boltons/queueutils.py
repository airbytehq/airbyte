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

"""Python comes with a many great data structures, from :class:`dict`
to :class:`collections.deque`, and no shortage of serviceable
algorithm implementations, from :func:`sorted` to :mod:`bisect`. But
priority queues are curiously relegated to an example documented in
:mod:`heapq`. Even there, the approach presented is not full-featured
and object-oriented. There is a built-in priority queue,
:class:`Queue.PriorityQueue`, but in addition to its austere API, it
carries the double-edged sword of threadsafety, making it fine for
multi-threaded, multi-consumer applications, but high-overhead for
cooperative/single-threaded use cases.

The ``queueutils`` module currently provides two Queue
implementations: :class:`HeapPriorityQueue`, based on a heap, and
:class:`SortedPriorityQueue`, based on a sorted list. Both use a
unified API based on :class:`BasePriorityQueue` to facilitate testing
the slightly different performance characteristics on various
application use cases.

>>> pq = PriorityQueue()
>>> pq.add('low priority task', 0)
>>> pq.add('high priority task', 2)
>>> pq.add('medium priority task 1', 1)
>>> pq.add('medium priority task 2', 1)
>>> len(pq)
4
>>> pq.pop()
'high priority task'
>>> pq.peek()
'medium priority task 1'
>>> len(pq)
3

"""


from heapq import heappush, heappop
from bisect import insort
import itertools

try:
    from .typeutils import make_sentinel
    _REMOVED = make_sentinel(var_name='_REMOVED')
except ImportError:
    _REMOVED = object()

try:
    from .listutils import BList
    # see BarrelList docstring for notes
except ImportError:
    BList = list


__all__ = ['PriorityQueue', 'BasePriorityQueue',
           'HeapPriorityQueue', 'SortedPriorityQueue']


# TODO: make Base a real abstract class
# TODO: add uniqueification


class BasePriorityQueue:
    """The abstract base class for the other PriorityQueues in this
    module. Override the ``_backend_type`` class attribute, as well as
    the :meth:`_push_entry` and :meth:`_pop_entry` staticmethods for
    custom subclass behavior. (Don't forget to use
    :func:`staticmethod`).

    Args:
        priority_key (callable): A function that takes *priority* as
            passed in by :meth:`add` and returns a real number
            representing the effective priority.

    """
    # negating priority means larger numbers = higher priority
    _default_priority_key = staticmethod(lambda p: -float(p or 0))
    _backend_type = list

    def __init__(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    @staticmethod
    def _push_entry(backend, entry):
        pass  # abstract

    @staticmethod
    def _pop_entry(backend):
        pass  # abstract

    def add(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def remove(self, task):
        """Remove a task from the priority queue. Raises :exc:`KeyError` if
        the *task* is absent.
        """
        entry = self._entry_map.pop(task)
        entry[-1] = _REMOVED

    def _cull(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def peek(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = self._pq[0]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('peek on empty queue')
        return task

    def pop(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = self._pop_entry(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('pop on empty queue')
        return task

    def __len__(self):
        "Return the number of tasks in the queue."
        return len(self._entry_map)


class HeapPriorityQueue(BasePriorityQueue):
    """A priority queue inherited from :class:`BasePriorityQueue`,
    backed by a list and based on the :func:`heapq.heappop` and
    :func:`heapq.heappush` functions in the built-in :mod:`heapq`
    module.
    """
    @staticmethod
    def _pop_entry(backend):
        return heappop(backend)

    @staticmethod
    def _push_entry(backend, entry):
        heappush(backend, entry)


class SortedPriorityQueue(BasePriorityQueue):
    """A priority queue inherited from :class:`BasePriorityQueue`, based
    on the :func:`bisect.insort` approach for in-order insertion into
    a sorted list.
    """
    _backend_type = BList

    @staticmethod
    def _pop_entry(backend):
        return backend.pop(0)

    @staticmethod
    def _push_entry(backend, entry):
        insort(backend, entry)


PriorityQueue = SortedPriorityQueue
