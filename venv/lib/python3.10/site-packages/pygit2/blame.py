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
from .ffi import ffi, C
from .utils import GenericIterator
from ._pygit2 import Signature, Oid


def wrap_signature(csig):
    if not csig:
        return None

    return Signature(ffi.string(csig.name).decode('utf-8'),
                     ffi.string(csig.email).decode('utf-8'),
                     csig.when.time, csig.when.offset, 'utf-8')

class BlameHunk:

    @classmethod
    def _from_c(cls, blame, ptr):
        hunk = cls.__new__(cls)
        hunk._blame = blame
        hunk._hunk = ptr
        return hunk

    @property
    def lines_in_hunk(self):
        """Number of lines"""
        return self._hunk.lines_in_hunk

    @property
    def boundary(self):
        """Tracked to a boundary commit"""
        # Casting directly to bool via cffi does not seem to work
        return int(ffi.cast('int', self._hunk.boundary)) != 0

    @property
    def final_start_line_number(self):
        """Final start line number"""
        return self._hunk.final_start_line_number

    @property
    def final_committer(self):
        """Final committer"""
        return wrap_signature(self._hunk.final_signature)

    @property
    def final_commit_id(self):
        return Oid(raw=bytes(ffi.buffer(ffi.addressof(self._hunk, 'final_commit_id'))[:]))

    @property
    def orig_start_line_number(self):
        """Origin start line number"""
        return self._hunk.orig_start_line_number

    @property
    def orig_committer(self):
        """Original committer"""
        return wrap_signature(self._hunk.orig_signature)

    @property
    def orig_commit_id(self):
        return Oid(raw=bytes(ffi.buffer(ffi.addressof(self._hunk, 'orig_commit_id'))[:]))

    @property
    def orig_path(self):
        """Original path"""
        path = self._hunk.orig_path
        if not path:
            return None

        return ffi.string(path).decode('utf-8')


class Blame:

    @classmethod
    def _from_c(cls, repo, ptr):
        blame = cls.__new__(cls)
        blame._repo = repo
        blame._blame = ptr
        return blame

    def __del__(self):
        C.git_blame_free(self._blame)

    def __len__(self):
        return C.git_blame_get_hunk_count(self._blame)

    def __getitem__(self, index):
        chunk = C.git_blame_get_hunk_byindex(self._blame, index)
        if not chunk:
            raise IndexError

        return BlameHunk._from_c(self, chunk)

    def for_line(self, line_no):
        """
        Returns the <BlameHunk> object for a given line given its number in the
        current Blame.

        Parameters:

        line_no
            Line number, starts at 1.
        """
        if line_no < 0:
            raise IndexError

        chunk = C.git_blame_get_hunk_byline(self._blame, line_no)
        if not chunk:
            raise IndexError

        return BlameHunk._from_c(self, chunk)

    def __iter__(self):
        return GenericIterator(self)
