# Copyright 2010-2023 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# Import from pygit2
from .errors import check_error
from .ffi import ffi, C
from .utils import to_bytes


class Refspec:
    """The constructor is for internal use only.
    """

    def __init__(self, owner, ptr):
        self._owner = owner
        self._refspec = ptr

    @property
    def src(self):
        """Source or lhs of the refspec"""
        return ffi.string(C.git_refspec_src(self._refspec)).decode('utf-8')

    @property
    def dst(self):
        """Destinaton or rhs of the refspec"""
        return ffi.string(C.git_refspec_dst(self._refspec)).decode('utf-8')

    @property
    def force(self):
        """Whether this refspeca llows non-fast-forward updates"""
        return bool(C.git_refspec_force(self._refspec))

    @property
    def string(self):
        """String which was used to create this refspec"""
        return ffi.string(C.git_refspec_string(self._refspec)).decode('utf-8')

    @property
    def direction(self):
        """Direction of this refspec (fetch or push)"""
        return C.git_refspec_direction(self._refspec)

    def src_matches(self, ref):
        """Return True if the given string matches the source of this refspec,
        False otherwise.
        """
        return bool(C.git_refspec_src_matches(self._refspec, to_bytes(ref)))

    def dst_matches(self, ref):
        """Return True if the given string matches the destination of this
        refspec, False otherwise."""
        return bool(C.git_refspec_dst_matches(self._refspec, to_bytes(ref)))

    def _transform(self, ref, fn):
        buf = ffi.new('git_buf *', (ffi.NULL, 0))
        err = fn(buf, self._refspec, to_bytes(ref))
        check_error(err)

        try:
            return ffi.string(buf.ptr).decode('utf-8')
        finally:
            C.git_buf_dispose(buf)

    def transform(self, ref):
        """Transform a reference name according to this refspec from the lhs to
        the rhs. Return an string.
        """
        return self._transform(ref, C.git_refspec_transform)

    def rtransform(self, ref):
        """Transform a reference name according to this refspec from the lhs to
        the rhs. Return an string.
        """
        return self._transform(ref, C.git_refspec_rtransform)
