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

"""This module provides useful math functions on top of Python's
built-in :mod:`math` module.
"""

from math import ceil as _ceil, floor as _floor
import bisect
import binascii


def clamp(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(x, lower), upper)


def ceil(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def floor(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


class Bits:
    '''
    An immutable bit-string or bit-array object.
    Provides list-like access to bits as bools,
    as well as bitwise masking and shifting operators.
    Bits also make it easy to convert between many
    different useful representations:

    * bytes -- good for serializing raw binary data
    * int -- good for incrementing (e.g. to try all possible values)
    * list of bools -- good for iterating over or treating as flags
    * hex/bin string -- good for human readability

    '''
    __slots__ = ('val', 'len')

    def __init__(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def __getitem__(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def __len__(self):
        return self.len

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.val == other.val and self.len == other.len

    def __or__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, other.len))

    def __and__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, other.len))

    def __lshift__(self, other):
        return Bits(self.val << other, self.len + other)

    def __rshift__(self, other):
        return Bits(self.val >> other, self.len - other)

    def __hash__(self):
        return hash(self.val)

    def as_list(self):
        return [c == '1' for c in self.as_bin()]

    def as_bin(self):
        return f'{{0:0{self.len}b}}'.format(self.val)

    def as_hex(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len % 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def as_int(self):
        return self.val

    def as_bytes(self):
        return binascii.unhexlify(self.as_hex())

    @classmethod
    def from_list(cls, list_):
        return cls(list_)

    @classmethod
    def from_bin(cls, bin):
        return cls(bin)

    @classmethod
    def from_hex(cls, hex):
        if isinstance(hex, bytes):
            hex = hex.decode('ascii')
        if not hex.startswith('0x'):
            hex = '0x' + hex
        return cls(hex)

    @classmethod
    def from_int(cls, int_, len_=None):
        return cls(int_, len_)

    @classmethod
    def from_bytes(cls, bytes_):
        return cls.from_hex(binascii.hexlify(bytes_))

    def __repr__(self):
        cn = self.__class__.__name__
        return f"{cn}('{self.as_bin()}')"
