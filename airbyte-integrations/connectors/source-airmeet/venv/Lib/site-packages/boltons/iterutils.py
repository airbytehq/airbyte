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

""":mod:`itertools` is full of great examples of Python generator
usage. However, there are still some critical gaps. ``iterutils``
fills many of those gaps with featureful, tested, and Pythonic
solutions.

Many of the functions below have two versions, one which
returns an iterator (denoted by the ``*_iter`` naming pattern), and a
shorter-named convenience form that returns a list. Some of the
following are based on examples in itertools docs.
"""

import os
import math
import time
import codecs
import random
import itertools
from itertools import zip_longest
from collections.abc import Mapping, Sequence, Set, ItemsView, Iterable


try:
    from .typeutils import make_sentinel
    _UNSET = make_sentinel('_UNSET')
    _REMAP_EXIT = make_sentinel('_REMAP_EXIT')
except ImportError:
    _REMAP_EXIT = object()
    _UNSET = object()


def is_iterable(obj):
    """Similar in nature to :func:`callable`, ``is_iterable`` returns
    ``True`` if an object is `iterable`_, ``False`` if not.

    >>> is_iterable([])
    True
    >>> is_iterable(object())
    False

    .. _iterable: https://docs.python.org/2/glossary.html#term-iterable
    """
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def is_scalar(obj):
    """A near-mirror of :func:`is_iterable`. Returns ``False`` if an
    object is an iterable container type. Strings are considered
    scalar as well, because strings are more often treated as whole
    values as opposed to iterables of 1-character substrings.

    >>> is_scalar(object())
    True
    >>> is_scalar(range(10))
    False
    >>> is_scalar('hello')
    True
    """
    return not is_iterable(obj) or isinstance(obj, (str, bytes))


def is_collection(obj):
    """The opposite of :func:`is_scalar`.  Returns ``True`` if an object
    is an iterable other than a string.

    >>> is_collection(object())
    False
    >>> is_collection(range(10))
    True
    >>> is_collection('hello')
    False
    """
    return is_iterable(obj) and not isinstance(obj, (str, bytes))


def split(src, sep=None, maxsplit=None):
    """Splits an iterable based on a separator. Like :meth:`str.split`,
    but for all iterables. Returns a list of lists.

    >>> split(['hi', 'hello', None, None, 'sup', None, 'soap', None])
    [['hi', 'hello'], ['sup'], ['soap']]

    See :func:`split_iter` docs for more info.
    """
    return list(split_iter(src, sep, maxsplit))


def split_iter(src, sep=None, maxsplit=None):
    """Splits an iterable based on a separator, *sep*, a max of
    *maxsplit* times (no max by default). *sep* can be:

      * a single value
      * an iterable of separators
      * a single-argument callable that returns True when a separator is
        encountered

    ``split_iter()`` yields lists of non-separator values. A separator will
    never appear in the output.

    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None, 'soap', None]))
    [['hi', 'hello'], ['sup'], ['soap']]

    Note that ``split_iter`` is based on :func:`str.split`, so if
    *sep* is ``None``, ``split()`` **groups** separators. If empty lists
    are desired between two contiguous ``None`` values, simply use
    ``sep=[None]``:

    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None]))
    [['hi', 'hello'], ['sup']]
    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None], sep=[None]))
    [['hi', 'hello'], [], ['sup'], []]

    Using a callable separator:

    >>> falsy_sep = lambda x: not x
    >>> list(split_iter(['hi', 'hello', None, '', 'sup', False], falsy_sep))
    [['hi', 'hello'], [], ['sup'], []]

    See :func:`split` for a list-returning version.

    """
    if not is_iterable(src):
        raise TypeError('expected an iterable')

    if maxsplit is not None:
        maxsplit = int(maxsplit)
        if maxsplit == 0:
            yield [src]
            return

    if callable(sep):
        sep_func = sep
    elif not is_scalar(sep):
        sep = frozenset(sep)
        def sep_func(x): return x in sep
    else:
        def sep_func(x): return x == sep

    cur_group = []
    split_count = 0
    for s in src:
        if maxsplit is not None and split_count >= maxsplit:
            def sep_func(x): return False
        if sep_func(s):
            if sep is None and not cur_group:
                # If sep is none, str.split() "groups" separators
                # check the str.split() docs for more info
                continue
            split_count += 1
            yield cur_group
            cur_group = []
        else:
            cur_group.append(s)

    if cur_group or sep is not None:
        yield cur_group
    return


def lstrip(iterable, strip_value=None):
    """Strips values from the beginning of an iterable. Stripped items will
    match the value of the argument strip_value. Functionality is analogous
    to that of the method str.lstrip. Returns a list.

    >>> lstrip(['Foo', 'Bar', 'Bam'], 'Foo')
    ['Bar', 'Bam']

    """
    return list(lstrip_iter(iterable, strip_value))


def lstrip_iter(iterable, strip_value=None):
    """Strips values from the beginning of an iterable. Stripped items will
    match the value of the argument strip_value. Functionality is analogous
    to that of the method str.lstrip. Returns a generator.

    >>> list(lstrip_iter(['Foo', 'Bar', 'Bam'], 'Foo'))
    ['Bar', 'Bam']

    """
    iterator = iter(iterable)
    for i in iterator:
        if i != strip_value:
            yield i
            break
    for i in iterator:
        yield i


def rstrip(iterable, strip_value=None):
    """Strips values from the end of an iterable. Stripped items will
    match the value of the argument strip_value. Functionality is analogous
    to that of the method str.rstrip. Returns a list.

    >>> rstrip(['Foo', 'Bar', 'Bam'], 'Bam')
    ['Foo', 'Bar']

    """
    return list(rstrip_iter(iterable, strip_value))


def rstrip_iter(iterable, strip_value=None):
    """Strips values from the end of an iterable. Stripped items will
    match the value of the argument strip_value. Functionality is analogous
    to that of the method str.rstrip. Returns a generator.

    >>> list(rstrip_iter(['Foo', 'Bar', 'Bam'], 'Bam'))
    ['Foo', 'Bar']

    """
    iterator = iter(iterable)
    for i in iterator:
        if i == strip_value:
            cache = list()
            cache.append(i)
            broken = False
            for i in iterator:
                if i == strip_value:
                    cache.append(i)
                else:
                    broken = True
                    break
            if not broken:  # Return to caller here because the end of the
                return     # iterator has been reached
            yield from cache
        yield i


def strip(iterable, strip_value=None):
    """Strips values from the beginning and end of an iterable. Stripped items
    will match the value of the argument strip_value. Functionality is
    analogous to that of the method str.strip. Returns a list.

    >>> strip(['Fu', 'Foo', 'Bar', 'Bam', 'Fu'], 'Fu')
    ['Foo', 'Bar', 'Bam']

    """
    return list(strip_iter(iterable, strip_value))


def strip_iter(iterable, strip_value=None):
    """Strips values from the beginning and end of an iterable. Stripped items
    will match the value of the argument strip_value. Functionality is
    analogous to that of the method str.strip. Returns a generator.

    >>> list(strip_iter(['Fu', 'Foo', 'Bar', 'Bam', 'Fu'], 'Fu'))
    ['Foo', 'Bar', 'Bam']

    """
    return rstrip_iter(lstrip_iter(iterable, strip_value), strip_value)


def chunked(src, size, count=None, **kw):
    """Returns a list of *count* chunks, each with *size* elements,
    generated from iterable *src*. If *src* is not evenly divisible by
    *size*, the final chunk will have fewer than *size* elements.
    Provide the *fill* keyword argument to provide a pad value and
    enable padding, otherwise no padding will take place.

    >>> chunked(range(10), 3)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    >>> chunked(range(10), 3, fill=None)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]
    >>> chunked(range(10), 3, count=2)
    [[0, 1, 2], [3, 4, 5]]

    See :func:`chunked_iter` for more info.
    """
    chunk_iter = chunked_iter(src, size, **kw)
    if count is None:
        return list(chunk_iter)
    else:
        return list(itertools.islice(chunk_iter, count))


def _validate_positive_int(value, name, strictly_positive=True):
    value = int(value)
    if value < 0 or (strictly_positive and value == 0):
        raise ValueError('expected a positive integer ' + name)
    return value


def chunked_iter(src, size, **kw):
    """Generates *size*-sized chunks from *src* iterable. Unless the
    optional *fill* keyword argument is provided, iterables not evenly
    divisible by *size* will have a final chunk that is smaller than
    *size*.

    >>> list(chunked_iter(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    >>> list(chunked_iter(range(10), 3, fill=None))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]

    Note that ``fill=None`` in fact uses ``None`` as the fill value.
    """
    # TODO: add count kwarg?
    if not is_iterable(src):
        raise TypeError('expected an iterable')
    size = _validate_positive_int(size, 'chunk size')
    do_fill = True
    try:
        fill_val = kw.pop('fill')
    except KeyError:
        do_fill = False
        fill_val = None
    if kw:
        raise ValueError('got unexpected keyword arguments: %r' % kw.keys())
    if not src:
        return

    def postprocess(chk): return chk
    if isinstance(src, (str, bytes)):
        def postprocess(chk, _sep=type(src)()): return _sep.join(chk)
        if isinstance(src, bytes):
            def postprocess(chk): return bytes(chk)
    src_iter = iter(src)
    while True:
        cur_chunk = list(itertools.islice(src_iter, size))
        if not cur_chunk:
            break
        lc = len(cur_chunk)
        if lc < size and do_fill:
            cur_chunk[lc:] = [fill_val] * (size - lc)
        yield postprocess(cur_chunk)
    return


def chunk_ranges(input_size, chunk_size, input_offset=0, overlap_size=0, align=False):
    """Generates *chunk_size*-sized chunk ranges for an input with length *input_size*.
    Optionally, a start of the input can be set via *input_offset*, and
    and overlap between the chunks may be specified via *overlap_size*.
    Also, if *align* is set to *True*, any items with *i % (chunk_size-overlap_size) == 0*
    are always at the beginning of the chunk.

    Returns an iterator of (start, end) tuples, one tuple per chunk.

    >>> list(chunk_ranges(input_offset=10, input_size=10, chunk_size=5))
    [(10, 15), (15, 20)]
    >>> list(chunk_ranges(input_offset=10, input_size=10, chunk_size=5, overlap_size=1))
    [(10, 15), (14, 19), (18, 20)]
    >>> list(chunk_ranges(input_offset=10, input_size=10, chunk_size=5, overlap_size=2))
    [(10, 15), (13, 18), (16, 20)]

    >>> list(chunk_ranges(input_offset=4, input_size=15, chunk_size=5, align=False))
    [(4, 9), (9, 14), (14, 19)]
    >>> list(chunk_ranges(input_offset=4, input_size=15, chunk_size=5, align=True))
    [(4, 5), (5, 10), (10, 15), (15, 19)]

    >>> list(chunk_ranges(input_offset=2, input_size=15, chunk_size=5, overlap_size=1, align=False))
    [(2, 7), (6, 11), (10, 15), (14, 17)]
    >>> list(chunk_ranges(input_offset=2, input_size=15, chunk_size=5, overlap_size=1, align=True))
    [(2, 5), (4, 9), (8, 13), (12, 17)]
    >>> list(chunk_ranges(input_offset=3, input_size=15, chunk_size=5, overlap_size=1, align=True))
    [(3, 5), (4, 9), (8, 13), (12, 17), (16, 18)]
    """
    input_size = _validate_positive_int(
        input_size, 'input_size', strictly_positive=False)
    chunk_size = _validate_positive_int(chunk_size, 'chunk_size')
    input_offset = _validate_positive_int(
        input_offset, 'input_offset', strictly_positive=False)
    overlap_size = _validate_positive_int(
        overlap_size, 'overlap_size', strictly_positive=False)

    input_stop = input_offset + input_size

    if align:
        initial_chunk_len = chunk_size - \
            input_offset % (chunk_size - overlap_size)
        if initial_chunk_len != overlap_size:
            yield (input_offset, min(input_offset + initial_chunk_len, input_stop))
            if input_offset + initial_chunk_len >= input_stop:
                return
            input_offset = input_offset + initial_chunk_len - overlap_size

    for i in range(input_offset, input_stop, chunk_size - overlap_size):
        yield (i, min(i + chunk_size, input_stop))

        if i + chunk_size >= input_stop:
            return


def pairwise(src, end=_UNSET):
    """Convenience function for calling :func:`windowed` on *src*, with
    *size* set to 2.

    >>> pairwise(range(5))
    [(0, 1), (1, 2), (2, 3), (3, 4)]
    >>> pairwise([])
    []

    Unless *end* is set, the number of pairs is always one less than 
    the number of elements in the iterable passed in, except on an empty input, 
    which will return an empty list.

    With *end* set, a number of pairs equal to the length of *src* is returned,
    with the last item of the last pair being equal to *end*.

    >>> list(pairwise(range(3), end=None))
    [(0, 1), (1, 2), (2, None)]

    This way, *end* values can be useful as sentinels to signal the end of the iterable.
    """
    return windowed(src, 2, fill=end)


def pairwise_iter(src, end=_UNSET):
    """Convenience function for calling :func:`windowed_iter` on *src*,
    with *size* set to 2.

    >>> list(pairwise_iter(range(5)))
    [(0, 1), (1, 2), (2, 3), (3, 4)]
    >>> list(pairwise_iter([]))
    []

    Unless *end* is set, the number of pairs is always one less 
    than the number of elements in the iterable passed in, 
    or zero, when *src* is empty.

    With *end* set, a number of pairs equal to the length of *src* is returned,
    with the last item of the last pair being equal to *end*. 

    >>> list(pairwise_iter(range(3), end=None))
    [(0, 1), (1, 2), (2, None)]    

    This way, *end* values can be useful as sentinels to signal the end
    of the iterable. For infinite iterators, setting *end* has no effect.
    """
    return windowed_iter(src, 2, fill=end)


def windowed(src, size, fill=_UNSET):
    """Returns tuples with exactly length *size*. If *fill* is unset 
    and the iterable is too short to make a window of length *size*, 
    no tuples are returned. See :func:`windowed_iter` for more.
    """
    return list(windowed_iter(src, size, fill=fill))


def windowed_iter(src, size, fill=_UNSET):
    """Returns tuples with length *size* which represent a sliding
    window over iterable *src*.

    >>> list(windowed_iter(range(7), 3))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]

    If *fill* is unset, and the iterable is too short to make a window 
    of length *size*, then no window tuples are returned.

    >>> list(windowed_iter(range(3), 5))
    []

    With *fill* set, the iterator always yields a number of windows
    equal to the length of the *src* iterable.

    >>> windowed(range(4), 3, fill=None)
    [(0, 1, 2), (1, 2, 3), (2, 3, None), (3, None, None)]

    This way, *fill* values can be useful to signal the end of the iterable.
    For infinite iterators, setting *fill* has no effect.
    """
    tees = itertools.tee(src, size)
    if fill is _UNSET:
        try:
            for i, t in enumerate(tees):
                for _ in range(i):
                    next(t)
        except StopIteration:
            return zip([])
        return zip(*tees)

    for i, t in enumerate(tees):
        for _ in range(i):
            try:
                next(t)
            except StopIteration:
                continue
    return zip_longest(*tees, fillvalue=fill)


def xfrange(stop, start=None, step=1.0):
    """Same as :func:`frange`, but generator-based instead of returning a
    list.

    >>> tuple(xfrange(1, 3, step=0.75))
    (1.0, 1.75, 2.5)

    See :func:`frange` for more details.
    """
    if not step:
        raise ValueError('step must be non-zero')
    if start is None:
        start, stop = 0.0, stop * 1.0
    else:
        # swap when all args are used
        stop, start = start * 1.0, stop * 1.0
    cur = start
    while cur < stop:
        yield cur
        cur += step


def frange(stop, start=None, step=1.0):
    """A :func:`range` clone for float-based ranges.

    >>> frange(5)
    [0.0, 1.0, 2.0, 3.0, 4.0]
    >>> frange(6, step=1.25)
    [0.0, 1.25, 2.5, 3.75, 5.0]
    >>> frange(100.5, 101.5, 0.25)
    [100.5, 100.75, 101.0, 101.25]
    >>> frange(5, 0)
    []
    >>> frange(5, 0, step=-1.25)
    [5.0, 3.75, 2.5, 1.25]
    """
    if not step:
        raise ValueError('step must be non-zero')
    if start is None:
        start, stop = 0.0, stop * 1.0
    else:
        # swap when all args are used
        stop, start = start * 1.0, stop * 1.0
    count = int(math.ceil((stop - start) / step))
    ret = [None] * count
    if not ret:
        return ret
    ret[0] = start
    for i in range(1, count):
        ret[i] = ret[i - 1] + step
    return ret


def backoff(start, stop, count=None, factor=2.0, jitter=False):
    """Returns a list of geometrically-increasing floating-point numbers,
    suitable for usage with `exponential backoff`_. Exactly like
    :func:`backoff_iter`, but without the ``'repeat'`` option for
    *count*. See :func:`backoff_iter` for more details.

    .. _exponential backoff: https://en.wikipedia.org/wiki/Exponential_backoff

    >>> backoff(1, 10)
    [1.0, 2.0, 4.0, 8.0, 10.0]
    """
    if count == 'repeat':
        raise ValueError("'repeat' supported in backoff_iter, not backoff")
    return list(backoff_iter(start, stop, count=count,
                             factor=factor, jitter=jitter))


def backoff_iter(start, stop, count=None, factor=2.0, jitter=False):
    """Generates a sequence of geometrically-increasing floats, suitable
    for usage with `exponential backoff`_. Starts with *start*,
    increasing by *factor* until *stop* is reached, optionally
    stopping iteration once *count* numbers are yielded. *factor*
    defaults to 2. In general retrying with properly-configured
    backoff creates a better-behaved component for a larger service
    ecosystem.

    .. _exponential backoff: https://en.wikipedia.org/wiki/Exponential_backoff

    >>> list(backoff_iter(1.0, 10.0, count=5))
    [1.0, 2.0, 4.0, 8.0, 10.0]
    >>> list(backoff_iter(1.0, 10.0, count=8))
    [1.0, 2.0, 4.0, 8.0, 10.0, 10.0, 10.0, 10.0]
    >>> list(backoff_iter(0.25, 100.0, factor=10))
    [0.25, 2.5, 25.0, 100.0]

    A simplified usage example:

    .. code-block:: python

      for timeout in backoff_iter(0.25, 5.0):
          try:
              res = network_call()
              break
          except Exception as e:
              log(e)
              time.sleep(timeout)

    An enhancement for large-scale systems would be to add variation,
    or *jitter*, to timeout values. This is done to avoid a thundering
    herd on the receiving end of the network call.

    Finally, for *count*, the special value ``'repeat'`` can be passed to
    continue yielding indefinitely.

    Args:

        start (float): Positive number for baseline.
        stop (float): Positive number for maximum.
        count (int): Number of steps before stopping
            iteration. Defaults to the number of steps between *start* and
            *stop*. Pass the string, `'repeat'`, to continue iteration
            indefinitely.
        factor (float): Rate of exponential increase. Defaults to `2.0`,
            e.g., `[1, 2, 4, 8, 16]`.
        jitter (float): A factor between `-1.0` and `1.0`, used to
            uniformly randomize and thus spread out timeouts in a distributed
            system, avoiding rhythm effects. Positive values use the base
            backoff curve as a maximum, negative values use the curve as a
            minimum. Set to 1.0 or `True` for a jitter approximating
            Ethernet's time-tested backoff solution. Defaults to `False`.

    """
    start = float(start)
    stop = float(stop)
    factor = float(factor)
    if start < 0.0:
        raise ValueError('expected start >= 0, not %r' % start)
    if factor < 1.0:
        raise ValueError('expected factor >= 1.0, not %r' % factor)
    if stop == 0.0:
        raise ValueError('expected stop >= 0')
    if stop < start:
        raise ValueError('expected stop >= start, not %r' % stop)
    if count is None:
        denom = start if start else 1
        count = 1 + math.ceil(math.log(stop/denom, factor))
        count = count if start else count + 1
    if count != 'repeat' and count < 0:
        raise ValueError('count must be positive or "repeat", not %r' % count)
    if jitter:
        jitter = float(jitter)
        if not (-1.0 <= jitter <= 1.0):
            raise ValueError('expected jitter -1 <= j <= 1, not: %r' % jitter)

    cur, i = start, 0
    while count == 'repeat' or i < count:
        if not jitter:
            cur_ret = cur
        elif jitter:
            cur_ret = cur - (cur * jitter * random.random())
        yield cur_ret
        i += 1
        if cur == 0:
            cur = 1
        elif cur < stop:
            cur *= factor
        if cur > stop:
            cur = stop
    return


def bucketize(src, key=bool, value_transform=None, key_filter=None):
    """Group values in the *src* iterable by the value returned by *key*.

    >>> bucketize(range(5))
    {False: [0], True: [1, 2, 3, 4]}
    >>> is_odd = lambda x: x % 2 == 1
    >>> bucketize(range(5), is_odd)
    {False: [0, 2, 4], True: [1, 3]}

    *key* is :class:`bool` by default, but can either be a callable or a string or a list
    if it is a string, it is the name of the attribute on which to bucketize objects.

    >>> bucketize([1+1j, 2+2j, 1, 2], key='real')
    {1.0: [(1+1j), 1], 2.0: [(2+2j), 2]}

    if *key* is a list, it contains the buckets where to put each object

    >>> bucketize([1,2,365,4,98],key=[0,1,2,0,2])
    {0: [1, 4], 1: [2], 2: [365, 98]}


    Value lists are not deduplicated:

    >>> bucketize([None, None, None, 'hello'])
    {False: [None, None, None], True: ['hello']}

    Bucketize into more than 3 groups

    >>> bucketize(range(10), lambda x: x % 3)
    {0: [0, 3, 6, 9], 1: [1, 4, 7], 2: [2, 5, 8]}

    ``bucketize`` has a couple of advanced options useful in certain
    cases.  *value_transform* can be used to modify values as they are
    added to buckets, and *key_filter* will allow excluding certain
    buckets from being collected.

    >>> bucketize(range(5), value_transform=lambda x: x*x)
    {False: [0], True: [1, 4, 9, 16]}

    >>> bucketize(range(10), key=lambda x: x % 3, key_filter=lambda k: k % 3 != 1)
    {0: [0, 3, 6, 9], 2: [2, 5, 8]}

    Note in some of these examples there were at most two keys, ``True`` and
    ``False``, and each key present has a list with at least one
    item. See :func:`partition` for a version specialized for binary
    use cases.

    """
    if not is_iterable(src):
        raise TypeError('expected an iterable')
    elif isinstance(key, list):
        if len(key) != len(src):
            raise ValueError("key and src have to be the same length")
        src = zip(key, src)

    if isinstance(key, str):
        def key_func(x): return getattr(x, key, x)
    elif callable(key):
        key_func = key
    elif isinstance(key, list):
        def key_func(x): return x[0]
    else:
        raise TypeError('expected key to be callable or a string or a list')

    if value_transform is None:
        def value_transform(x): return x
    if not callable(value_transform):
        raise TypeError('expected callable value transform function')
    if isinstance(key, list):
        f = value_transform
        def value_transform(x): return f(x[1])

    ret = {}
    for val in src:
        key_of_val = key_func(val)
        if key_filter is None or key_filter(key_of_val):
            ret.setdefault(key_of_val, []).append(value_transform(val))
    return ret


def partition(src, key=bool):
    """No relation to :meth:`str.partition`, ``partition`` is like
    :func:`bucketize`, but for added convenience returns a tuple of
    ``(truthy_values, falsy_values)``.

    >>> nonempty, empty = partition(['', '', 'hi', '', 'bye'])
    >>> nonempty
    ['hi', 'bye']

    *key* defaults to :class:`bool`, but can be carefully overridden to
    use either a function that returns either ``True`` or ``False`` or
    a string name of the attribute on which to partition objects.

    >>> import string
    >>> is_digit = lambda x: x in string.digits
    >>> decimal_digits, hexletters = partition(string.hexdigits, is_digit)
    >>> ''.join(decimal_digits), ''.join(hexletters)
    ('0123456789', 'abcdefABCDEF')
    """
    bucketized = bucketize(src, key)
    return bucketized.get(True, []), bucketized.get(False, [])


def unique(src, key=None):
    """``unique()`` returns a list of unique values, as determined by
    *key*, in the order they first appeared in the input iterable,
    *src*.

    >>> ones_n_zeros = '11010110001010010101010'
    >>> ''.join(unique(ones_n_zeros))
    '10'

    See :func:`unique_iter` docs for more details.
    """
    return list(unique_iter(src, key))


def unique_iter(src, key=None):
    """Yield unique elements from the iterable, *src*, based on *key*,
    in the order in which they first appeared in *src*.

    >>> repetitious = [1, 2, 3] * 10
    >>> list(unique_iter(repetitious))
    [1, 2, 3]

    By default, *key* is the object itself, but *key* can either be a
    callable or, for convenience, a string name of the attribute on
    which to uniqueify objects, falling back on identity when the
    attribute is not present.

    >>> pleasantries = ['hi', 'hello', 'ok', 'bye', 'yes']
    >>> list(unique_iter(pleasantries, key=lambda x: len(x)))
    ['hi', 'hello', 'bye']
    """
    if not is_iterable(src):
        raise TypeError('expected an iterable, not %r' % type(src))
    if key is None:
        def key_func(x): return x
    elif callable(key):
        key_func = key
    elif isinstance(key, str):
        def key_func(x): return getattr(x, key, x)
    else:
        raise TypeError('"key" expected a string or callable, not %r' % key)
    seen = set()
    for i in src:
        k = key_func(i)
        if k not in seen:
            seen.add(k)
            yield i
    return


def redundant(src, key=None, groups=False):
    """The complement of :func:`unique()`.

    By default returns non-unique/duplicate values as a list of the
    *first* redundant value in *src*. Pass ``groups=True`` to get
    groups of all values with redundancies, ordered by position of the
    first redundant value. This is useful in conjunction with some
    normalizing *key* function.

    >>> redundant([1, 2, 3, 4])
    []
    >>> redundant([1, 2, 3, 2, 3, 3, 4])
    [2, 3]
    >>> redundant([1, 2, 3, 2, 3, 3, 4], groups=True)
    [[2, 2], [3, 3, 3]]

    An example using a *key* function to do case-insensitive
    redundancy detection.

    >>> redundant(['hi', 'Hi', 'HI', 'hello'], key=str.lower)
    ['Hi']
    >>> redundant(['hi', 'Hi', 'HI', 'hello'], groups=True, key=str.lower)
    [['hi', 'Hi', 'HI']]

    *key* should also be used when the values in *src* are not hashable.

    .. note::

       This output of this function is designed for reporting
       duplicates in contexts when a unique input is desired. Due to
       the grouped return type, there is no streaming equivalent of
       this function for the time being.

    """
    if key is None:
        pass
    elif callable(key):
        key_func = key
    elif isinstance(key, (str, bytes)):
        def key_func(x): return getattr(x, key, x)
    else:
        raise TypeError('"key" expected a string or callable, not %r' % key)
    seen = {}  # key to first seen item
    redundant_order = []
    redundant_groups = {}
    for i in src:
        k = key_func(i) if key else i
        if k not in seen:
            seen[k] = i
        else:
            if k in redundant_groups:
                if groups:
                    redundant_groups[k].append(i)
            else:
                redundant_order.append(k)
                redundant_groups[k] = [seen[k], i]
    if not groups:
        ret = [redundant_groups[k][1] for k in redundant_order]
    else:
        ret = [redundant_groups[k] for k in redundant_order]
    return ret


def one(src, default=None, key=None):
    """Along the same lines as builtins, :func:`all` and :func:`any`, and
    similar to :func:`first`, ``one()`` returns the single object in
    the given iterable *src* that evaluates to ``True``, as determined
    by callable *key*. If unset, *key* defaults to :class:`bool`. If
    no such objects are found, *default* is returned. If *default* is
    not passed, ``None`` is returned.

    If *src* has more than one object that evaluates to ``True``, or
    if there is no object that fulfills such condition, return
    *default*. It's like an `XOR`_ over an iterable.

    >>> one((True, False, False))
    True
    >>> one((True, False, True))
    >>> one((0, 0, 'a'))
    'a'
    >>> one((0, False, None))
    >>> one((True, True), default=False)
    False
    >>> bool(one(('', 1)))
    True
    >>> one((10, 20, 30, 42), key=lambda i: i > 40)
    42

    See `Martín Gaitán's original repo`_ for further use cases.

    .. _Martín Gaitán's original repo: https://github.com/mgaitan/one
    .. _XOR: https://en.wikipedia.org/wiki/Exclusive_or

    """
    ones = list(itertools.islice(filter(key, src), 2))
    return ones[0] if len(ones) == 1 else default


def first(iterable, default=None, key=None):
    """Return first element of *iterable* that evaluates to ``True``, else
    return ``None`` or optional *default*. Similar to :func:`one`.

    >>> first([0, False, None, [], (), 42])
    42
    >>> first([0, False, None, [], ()]) is None
    True
    >>> first([0, False, None, [], ()], default='ohai')
    'ohai'
    >>> import re
    >>> m = first(re.match(regex, 'abc') for regex in ['b.*', 'a(.*)'])
    >>> m.group(1)
    'bc'

    The optional *key* argument specifies a one-argument predicate function
    like that used for *filter()*.  The *key* argument, if supplied, should be
    in keyword form. For example, finding the first even number in an iterable:

    >>> first([1, 1, 3, 4, 5], key=lambda x: x % 2 == 0)
    4

    Contributed by Hynek Schlawack, author of `the original standalone module`_.

    .. _the original standalone module: https://github.com/hynek/first
    """
    return next(filter(key, iterable), default)


def flatten_iter(iterable):
    """``flatten_iter()`` yields all the elements from *iterable* while
    collapsing any nested iterables.

    >>> nested = [[1, 2], [[3], [4, 5]]]
    >>> list(flatten_iter(nested))
    [1, 2, 3, 4, 5]
    """
    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten_iter(item)
        else:
            yield item


def flatten(iterable):
    """``flatten()`` returns a collapsed list of all the elements from
    *iterable* while collapsing any nested iterables.

    >>> nested = [[1, 2], [[3], [4, 5]]]
    >>> flatten(nested)
    [1, 2, 3, 4, 5]
    """
    return list(flatten_iter(iterable))


def same(iterable, ref=_UNSET):
    """``same()`` returns ``True`` when all values in *iterable* are
    equal to one another, or optionally a reference value,
    *ref*. Similar to :func:`all` and :func:`any` in that it evaluates
    an iterable and returns a :class:`bool`. ``same()`` returns
    ``True`` for empty iterables.

    >>> same([])
    True
    >>> same([1])
    True
    >>> same(['a', 'a', 'a'])
    True
    >>> same(range(20))
    False
    >>> same([[], []])
    True
    >>> same([[], []], ref='test')
    False

    """
    iterator = iter(iterable)
    if ref is _UNSET:
        ref = next(iterator, ref)
    return all(val == ref for val in iterator)


def default_visit(path, key, value):
    # print('visit(%r, %r, %r)' % (path, key, value))
    return key, value


# enable the extreme: monkeypatching iterutils with a different default_visit
_orig_default_visit = default_visit


def default_enter(path, key, value):
    # print('enter(%r, %r)' % (key, value))
    if isinstance(value, (str, bytes)):
        return value, False
    elif isinstance(value, Mapping):
        return value.__class__(), ItemsView(value)
    elif isinstance(value, Sequence):
        return value.__class__(), enumerate(value)
    elif isinstance(value, Set):
        return value.__class__(), enumerate(value)
    else:
        # files, strings, other iterables, and scalars are not
        # traversed
        return value, False


def default_exit(path, key, old_parent, new_parent, new_items):
    # print('exit(%r, %r, %r, %r, %r)'
    #       % (path, key, old_parent, new_parent, new_items))
    ret = new_parent
    if isinstance(new_parent, Mapping):
        new_parent.update(new_items)
    elif isinstance(new_parent, Sequence):
        vals = [v for i, v in new_items]
        try:
            new_parent.extend(vals)
        except AttributeError:
            ret = new_parent.__class__(vals)  # tuples
    elif isinstance(new_parent, Set):
        vals = [v for i, v in new_items]
        try:
            new_parent.update(vals)
        except AttributeError:
            ret = new_parent.__class__(vals)  # frozensets
    else:
        raise RuntimeError('unexpected iterable type: %r' % type(new_parent))
    return ret


def remap(root, visit=default_visit, enter=default_enter, exit=default_exit,
          **kwargs):
    """The remap ("recursive map") function is used to traverse and
    transform nested structures. Lists, tuples, sets, and dictionaries
    are just a few of the data structures nested into heterogeneous
    tree-like structures that are so common in programming.
    Unfortunately, Python's built-in ways to manipulate collections
    are almost all flat. List comprehensions may be fast and succinct,
    but they do not recurse, making it tedious to apply quick changes
    or complex transforms to real-world data.

    remap goes where list comprehensions cannot.

    Here's an example of removing all Nones from some data:

    >>> from pprint import pprint
    >>> reviews = {'Star Trek': {'TNG': 10, 'DS9': 8.5, 'ENT': None},
    ...            'Babylon 5': 6, 'Dr. Who': None}
    >>> pprint(remap(reviews, lambda p, k, v: v is not None))
    {'Babylon 5': 6, 'Star Trek': {'DS9': 8.5, 'TNG': 10}}

    Notice how both Nones have been removed despite the nesting in the
    dictionary. Not bad for a one-liner, and that's just the beginning.
    See `this remap cookbook`_ for more delicious recipes.

    .. _this remap cookbook: http://sedimental.org/remap.html

    remap takes four main arguments: the object to traverse and three
    optional callables which determine how the remapped object will be
    created.

    Args:

        root: The target object to traverse. By default, remap
            supports iterables like :class:`list`, :class:`tuple`,
            :class:`dict`, and :class:`set`, but any object traversable by
            *enter* will work.
        visit (callable): This function is called on every item in
            *root*. It must accept three positional arguments, *path*,
            *key*, and *value*. *path* is simply a tuple of parents'
            keys. *visit* should return the new key-value pair. It may
            also return ``True`` as shorthand to keep the old item
            unmodified, or ``False`` to drop the item from the new
            structure. *visit* is called after *enter*, on the new parent.

            The *visit* function is called for every item in root,
            including duplicate items. For traversable values, it is
            called on the new parent object, after all its children
            have been visited. The default visit behavior simply
            returns the key-value pair unmodified.
        enter (callable): This function controls which items in *root*
            are traversed. It accepts the same arguments as *visit*: the
            path, the key, and the value of the current item. It returns a
            pair of the blank new parent, and an iterator over the items
            which should be visited. If ``False`` is returned instead of
            an iterator, the value will not be traversed.

            The *enter* function is only called once per unique value. The
            default enter behavior support mappings, sequences, and
            sets. Strings and all other iterables will not be traversed.
        exit (callable): This function determines how to handle items
            once they have been visited. It gets the same three
            arguments as the other functions -- *path*, *key*, *value*
            -- plus two more: the blank new parent object returned
            from *enter*, and a list of the new items, as remapped by
            *visit*.

            Like *enter*, the *exit* function is only called once per
            unique value. The default exit behavior is to simply add
            all new items to the new parent, e.g., using
            :meth:`list.extend` and :meth:`dict.update` to add to the
            new parent. Immutable objects, such as a :class:`tuple` or
            :class:`namedtuple`, must be recreated from scratch, but
            use the same type as the new parent passed back from the
            *enter* function.
        reraise_visit (bool): A pragmatic convenience for the *visit*
            callable. When set to ``False``, remap ignores any errors
            raised by the *visit* callback. Items causing exceptions
            are kept. See examples for more details.
        trace (bool): Pass ``trace=True`` to print out the entire
            traversal. Or pass a tuple of ``'visit'``, ``'enter'``,
            or ``'exit'`` to print only the selected events.

    remap is designed to cover the majority of cases with just the
    *visit* callable. While passing in multiple callables is very
    empowering, remap is designed so very few cases should require
    passing more than one function.

    When passing *enter* and *exit*, it's common and easiest to build
    on the default behavior. Simply add ``from boltons.iterutils import
    default_enter`` (or ``default_exit``), and have your enter/exit
    function call the default behavior before or after your custom
    logic. See `this example`_.

    Duplicate and self-referential objects (aka reference loops) are
    automatically handled internally, `as shown here`_.

    .. _this example: http://sedimental.org/remap.html#sort_all_lists
    .. _as shown here: http://sedimental.org/remap.html#corner_cases

    """
    # TODO: improve argument formatting in sphinx doc
    # TODO: enter() return (False, items) to continue traverse but cancel copy?
    if not callable(visit):
        raise TypeError('visit expected callable, not: %r' % visit)
    if not callable(enter):
        raise TypeError('enter expected callable, not: %r' % enter)
    if not callable(exit):
        raise TypeError('exit expected callable, not: %r' % exit)
    reraise_visit = kwargs.pop('reraise_visit', True)
    trace = kwargs.pop('trace', ())
    if trace is True:
        trace = ('visit', 'enter', 'exit')
    elif isinstance(trace, str):
        trace = (trace,)
    if not isinstance(trace, (tuple, list, set)):
        raise TypeError('trace expected tuple of event names, not: %r' % trace)
    trace_enter, trace_exit, trace_visit = 'enter' in trace, 'exit' in trace, 'visit' in trace

    if kwargs:
        raise TypeError('unexpected keyword arguments: %r' % kwargs.keys())

    path, registry, stack = (), {}, [(None, root)]
    new_items_stack = []
    while stack:
        key, value = stack.pop()
        id_value = id(value)
        if key is _REMAP_EXIT:
            key, new_parent, old_parent = value
            id_value = id(old_parent)
            path, new_items = new_items_stack.pop()
            if trace_exit:
                print(' .. remap exit:', path, '-', key, '-',
                      old_parent, '-', new_parent, '-', new_items)
            value = exit(path, key, old_parent, new_parent, new_items)
            if trace_exit:
                print(' .. remap exit result:', value)
            registry[id_value] = value
            if not new_items_stack:
                continue
        elif id_value in registry:
            value = registry[id_value]
        else:
            if trace_enter:
                print(' .. remap enter:', path, '-', key, '-', value)
            res = enter(path, key, value)
            if trace_enter:
                print(' .. remap enter result:', res)
            try:
                new_parent, new_items = res
            except TypeError:
                # TODO: handle False?
                raise TypeError('enter should return a tuple of (new_parent,'
                                ' items_iterator), not: %r' % res)
            if new_items is not False:
                # traverse unless False is explicitly passed
                registry[id_value] = new_parent
                new_items_stack.append((path, []))
                if value is not root:
                    path += (key,)
                stack.append((_REMAP_EXIT, (key, new_parent, value)))
                if new_items:
                    stack.extend(reversed(list(new_items)))
                if trace_enter:
                    print(' .. remap stack size now:', len(stack))
                continue
        if visit is _orig_default_visit:
            # avoid function call overhead by inlining identity operation
            visited_item = (key, value)
        else:
            try:
                if trace_visit:
                    print(' .. remap visit:', path, '-', key, '-', value)
                visited_item = visit(path, key, value)
            except Exception:
                if reraise_visit:
                    raise
                visited_item = True
            if visited_item is False:
                if trace_visit:
                    print(' .. remap visit result: <drop>')
                continue  # drop
            elif visited_item is True:
                visited_item = (key, value)
            if trace_visit:
                print(' .. remap visit result:', visited_item)
            # TODO: typecheck?
            #    raise TypeError('expected (key, value) from visit(),'
            #                    ' not: %r' % visited_item)
        try:
            new_items_stack[-1][1].append(visited_item)
        except IndexError:
            raise TypeError('expected remappable root, not: %r' % root)
    return value


class PathAccessError(KeyError, IndexError, TypeError):
    """An amalgamation of KeyError, IndexError, and TypeError,
    representing what can occur when looking up a path in a nested
    object.
    """

    def __init__(self, exc, seg, path):
        self.exc = exc
        self.seg = seg
        self.path = path

    def __repr__(self):
        cn = self.__class__.__name__
        return f'{cn}({self.exc!r}, {self.seg!r}, {self.path!r})'

    def __str__(self):
        return ('could not access %r from path %r, got error: %r'
                % (self.seg, self.path, self.exc))


def get_path(root, path, default=_UNSET):
    """Retrieve a value from a nested object via a tuple representing the
    lookup path.

    >>> root = {'a': {'b': {'c': [[1], [2], [3]]}}}
    >>> get_path(root, ('a', 'b', 'c', 2, 0))
    3

    The path tuple format is intentionally consistent with that of
    :func:`remap`, but a single dotted string can also be passed.

    One of get_path's chief aims is improved error messaging. EAFP is
    great, but the error messages are not.

    For instance, ``root['a']['b']['c'][2][1]`` gives back
    ``IndexError: list index out of range``

    What went out of range where? get_path currently raises
    ``PathAccessError: could not access 2 from path ('a', 'b', 'c', 2,
    1), got error: IndexError('list index out of range',)``, a
    subclass of IndexError and KeyError.

    You can also pass a default that covers the entire operation,
    should the lookup fail at any level.

    Args:
       root: The target nesting of dictionaries, lists, or other
          objects supporting ``__getitem__``.
       path (tuple): A sequence of strings and integers to be successively
          looked up within *root*. A dot-separated (``a.b``) string may 
          also be passed.
       default: The value to be returned should any
          ``PathAccessError`` exceptions be raised.
    """
    if isinstance(path, str):
        path = path.split('.')
    cur = root
    try:
        for seg in path:
            try:
                cur = cur[seg]
            except (KeyError, IndexError) as exc:
                raise PathAccessError(exc, seg, path)
            except TypeError as exc:
                # either string index in a list, or a parent that
                # doesn't support indexing
                try:
                    seg = int(seg)
                    cur = cur[seg]
                except (ValueError, KeyError, IndexError, TypeError):
                    if not is_iterable(cur):
                        exc = TypeError('%r object is not indexable'
                                        % type(cur).__name__)
                    raise PathAccessError(exc, seg, path)
    except PathAccessError:
        if default is _UNSET:
            raise
        return default
    return cur


def research(root, query=lambda p, k, v: True, reraise=False, enter=default_enter):
    """The :func:`research` function uses :func:`remap` to recurse over
    any data nested in *root*, and find values which match a given
    criterion, specified by the *query* callable.

    Results are returned as a list of ``(path, value)`` pairs. The
    paths are tuples in the same format accepted by
    :func:`get_path`. This can be useful for comparing values nested
    in two or more different structures.

    Here's a simple example that finds all integers:

    >>> root = {'a': {'b': 1, 'c': (2, 'd', 3)}, 'e': None}
    >>> res = research(root, query=lambda p, k, v: isinstance(v, int))
    >>> print(sorted(res))
    [(('a', 'b'), 1), (('a', 'c', 0), 2), (('a', 'c', 2), 3)]

    Note how *query* follows the same, familiar ``path, key, value``
    signature as the ``visit`` and ``enter`` functions on
    :func:`remap`, and returns a :class:`bool`.

    Args:
       root: The target object to search. Supports the same types of
          objects as :func:`remap`, including :class:`list`,
          :class:`tuple`, :class:`dict`, and :class:`set`.
       query (callable): The function called on every object to
          determine whether to include it in the search results. The
          callable must accept three arguments, *path*, *key*, and
          *value*, commonly abbreviated *p*, *k*, and *v*, same as
          *enter* and *visit* from :func:`remap`.
       reraise (bool): Whether to reraise exceptions raised by *query*
          or to simply drop the result that caused the error.


    With :func:`research` it's easy to inspect the details of a data
    structure, like finding values that are at a certain depth (using
    ``len(p)``) and much more. If more advanced functionality is
    needed, check out the code and make your own :func:`remap`
    wrapper, and consider `submitting a patch`_!

    .. _submitting a patch: https://github.com/mahmoud/boltons/pulls
    """
    ret = []

    if not callable(query):
        raise TypeError('query expected callable, not: %r' % query)

    def _enter(path, key, value):
        try:
            if query(path, key, value):
                ret.append((path + (key,), value))
        except Exception:
            if reraise:
                raise
        return enter(path, key, value)

    remap(root, enter=_enter)
    return ret


# TODO: recollect()
# TODO: refilter()
# TODO: reiter()


# GUID iterators: 10x faster and somewhat more compact than uuid.

class GUIDerator:
    """The GUIDerator is an iterator that yields a globally-unique
    identifier (GUID) on every iteration. The GUIDs produced are
    hexadecimal strings.

    Testing shows it to be around 12x faster than the uuid module. By
    default it is also more compact, partly due to its default 96-bit
    (24-hexdigit) length. 96 bits of randomness means that there is a
    1 in 2 ^ 32 chance of collision after 2 ^ 64 iterations. If more
    or less uniqueness is desired, the *size* argument can be adjusted
    accordingly.

    Args:
        size (int): character length of the GUID, defaults to 24. Lengths
                    between 20 and 36 are considered valid.

    The GUIDerator has built-in fork protection that causes it to
    detect a fork on next iteration and reseed accordingly.

    """

    def __init__(self, size=24):
        self.size = size
        if size < 20 or size > 36:
            raise ValueError('expected 20 < size <= 36')
        import hashlib
        self._sha1 = hashlib.sha1
        self.count = itertools.count()
        self.reseed()

    def reseed(self):
        import socket
        self.pid = os.getpid()
        self.salt = '-'.join([str(self.pid),
                              socket.gethostname() or '<nohostname>',
                              str(time.time()),
                              os.urandom(6).hex()])
        return

    def __iter__(self):
        return self

    def __next__(self):
        if os.getpid() != self.pid:
            self.reseed()
        target_bytes = (self.salt + str(next(self.count))).encode('utf8')
        hash_text = self._sha1(target_bytes).hexdigest()[:self.size]
        return hash_text

    next = __next__


class SequentialGUIDerator(GUIDerator):
    """Much like the standard GUIDerator, the SequentialGUIDerator is an
    iterator that yields a globally-unique identifier (GUID) on every
    iteration. The GUIDs produced are hexadecimal strings.

    The SequentialGUIDerator differs in that it picks a starting GUID
    value and increments every iteration. This yields GUIDs which are
    of course unique, but also ordered and lexicographically sortable.

    The SequentialGUIDerator is around 50% faster than the normal
    GUIDerator, making it almost 20x as fast as the built-in uuid
    module. By default it is also more compact, partly due to its
    96-bit (24-hexdigit) default length. 96 bits of randomness means that
    there is a 1 in 2 ^ 32 chance of collision after 2 ^ 64
    iterations. If more or less uniqueness is desired, the *size*
    argument can be adjusted accordingly.

    Args:
        size (int): character length of the GUID, defaults to 24.

    Note that with SequentialGUIDerator there is a chance of GUIDs
    growing larger than the size configured. The SequentialGUIDerator
    has built-in fork protection that causes it to detect a fork on
    next iteration and reseed accordingly.

    """

    def reseed(self):
        super().reseed()
        start_str = self._sha1(self.salt.encode('utf8')).hexdigest()
        self.start = int(start_str[:self.size], 16)
        self.start |= (1 << ((self.size * 4) - 2))

    def __next__(self):
        if os.getpid() != self.pid:
            self.reseed()
        return '%x' % (next(self.count) + self.start)

    next = __next__


guid_iter = GUIDerator()
seq_guid_iter = SequentialGUIDerator()


def soft_sorted(iterable, first=None, last=None, key=None, reverse=False):
    """For when you care about the order of some elements, but not about
    others.

    Use this to float to the top and/or sink to the bottom a specific
    ordering, while sorting the rest of the elements according to
    normal :func:`sorted` rules.

    >>> soft_sorted(['two', 'b', 'one', 'a'], first=['one', 'two'])
    ['one', 'two', 'a', 'b']
    >>> soft_sorted(range(7), first=[6, 15], last=[2, 4], reverse=True)
    [6, 5, 3, 1, 0, 2, 4]
    >>> import string
    >>> ''.join(soft_sorted(string.hexdigits, first='za1', last='b', key=str.lower))
    'aA1023456789cCdDeEfFbB'

    Args:
       iterable (list): A list or other iterable to sort.
       first (list): A sequence to enforce for elements which should
          appear at the beginning of the returned list.
       last (list): A sequence to enforce for elements which should
          appear at the end of the returned list.
       key (callable): Callable used to generate a comparable key for
          each item to be sorted, same as the key in
          :func:`sorted`. Note that entries in *first* and *last*
          should be the keys for the items. Defaults to
          passthrough/the identity function.
       reverse (bool): Whether or not elements not explicitly ordered
          by *first* and *last* should be in reverse order or not.

    Returns a new list in sorted order.
    """
    first = first or []
    last = last or []
    key = key or (lambda x: x)
    seq = list(iterable)
    other = [x for x in seq if not (
        (first and key(x) in first) or (last and key(x) in last))]
    other.sort(key=key, reverse=reverse)

    if first:
        first = sorted([x for x in seq if key(x) in first],
                       key=lambda x: first.index(key(x)))
    if last:
        last = sorted([x for x in seq if key(x) in last],
                      key=lambda x: last.index(key(x)))
    return first + other + last


def untyped_sorted(iterable, key=None, reverse=False):
    """A version of :func:`sorted` which will happily sort an iterable of
    heterogeneous types and return a new list, similar to legacy Python's
    behavior.

    >>> untyped_sorted(['abc', 2.0, 1, 2, 'def'])
    [1, 2.0, 2, 'abc', 'def']

    Note how mutually orderable types are sorted as expected, as in
    the case of the integers and floats above.

    .. note::

       Results may vary across Python versions and builds, but the
       function will produce a sorted list, except in the case of
       explicitly unorderable objects.

    """
    class _Wrapper:
        slots = ('obj',)

        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            obj = key(self.obj) if key is not None else self.obj
            other = key(other.obj) if key is not None else other.obj
            try:
                ret = obj < other
            except TypeError:
                ret = ((type(obj).__name__, id(type(obj)), obj)
                       < (type(other).__name__, id(type(other)), other))
            return ret

    if key is not None and not callable(key):
        raise TypeError('expected function or callable object for key, not: %r'
                        % key)

    return sorted(iterable, key=_Wrapper, reverse=reverse)


"""
May actually be faster to do an isinstance check for a str path

$ python -m timeit -s "x = [1]" "x[0]"
10000000 loops, best of 3: 0.0207 usec per loop
$ python -m timeit -s "x = [1]" "try: x[0] \nexcept: pass"
10000000 loops, best of 3: 0.029 usec per loop
$ python -m timeit -s "x = [1]" "try: x[1] \nexcept: pass"
1000000 loops, best of 3: 0.315 usec per loop
# setting up try/except is fast, only around 0.01us
# actually triggering the exception takes almost 10x as long

$ python -m timeit -s "x = [1]" "isinstance(x, basestring)"
10000000 loops, best of 3: 0.141 usec per loop
$ python -m timeit -s "x = [1]" "isinstance(x, str)"
10000000 loops, best of 3: 0.131 usec per loop
$ python -m timeit -s "x = [1]" "try: x.split('.')\n except: pass"
1000000 loops, best of 3: 0.443 usec per loop
$ python -m timeit -s "x = [1]" "try: x.split('.') \nexcept AttributeError: pass"
1000000 loops, best of 3: 0.544 usec per loop
"""
