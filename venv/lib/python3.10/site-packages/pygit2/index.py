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

import weakref

# Import from pygit2
from ._pygit2 import Oid, Tree, Diff
from .errors import check_error
from .ffi import ffi, C
from .utils import to_bytes, to_str
from .utils import GenericIterator, StrArray


class Index:
    # XXX Implement the basic features in C (_pygit2.Index) and make
    # pygit2.Index to inherit from _pygit2.Index? This would allow for
    # a proper implementation in some places: e.g. checking the index type
    # from C code (see Tree_diff_to_index)

    def __init__(self, path=None):
        """Create a new Index

        If path is supplied, the read and write methods will use that path
        to read from and write to.
        """
        cindex = ffi.new('git_index **')
        err = C.git_index_open(cindex, to_bytes(path))
        check_error(err)

        self._repo = None
        self._index = cindex[0]
        self._cindex = cindex

    @classmethod
    def from_c(cls, repo, ptr):
        index = cls.__new__(cls)
        index._repo = repo
        index._index = ptr[0]
        index._cindex = ptr

        return index

    @property
    def _pointer(self):
        return bytes(ffi.buffer(self._cindex)[:])

    def __del__(self):
        C.git_index_free(self._index)

    def __len__(self):
        return C.git_index_entrycount(self._index)

    def __contains__(self, path):
        err = C.git_index_find(ffi.NULL, self._index, to_bytes(path))
        if err == C.GIT_ENOTFOUND:
            return False

        check_error(err)
        return True

    def __getitem__(self, key):
        centry = ffi.NULL
        if isinstance(key, str) or hasattr(key, '__fspath__'):
            centry = C.git_index_get_bypath(self._index, to_bytes(key), 0)
        elif isinstance(key, int):
            if key >= 0:
                centry = C.git_index_get_byindex(self._index, key)
            else:
                raise ValueError(key)
        else:
            raise TypeError(f'Expected str or int, got {type(key)}')

        if centry == ffi.NULL:
            raise KeyError(key)

        return IndexEntry._from_c(centry)

    def __iter__(self):
        return GenericIterator(self)

    def read(self, force=True):
        """
        Update the contents of the Index by reading from a file.

        Parameters:

        force
            If True (the default) always reload. If False, only if the file
            has changed.
        """

        err = C.git_index_read(self._index, force)
        check_error(err, io=True)

    def write(self):
        """Write the contents of the Index to disk."""
        err = C.git_index_write(self._index)
        check_error(err, io=True)

    def clear(self):
        err = C.git_index_clear(self._index)
        check_error(err)

    def read_tree(self, tree):
        """Replace the contents of the Index with those of the given tree,
        expressed either as a <Tree> object or as an oid (string or <Oid>).

        The tree will be read recursively and all its children will also be
        inserted into the Index.
        """
        repo = self._repo
        if isinstance(tree, str):
            tree = repo[tree]

        if isinstance(tree, Oid):
            if repo is None:
                raise TypeError("id given but no associated repository")

            tree = repo[tree]
        elif not isinstance(tree, Tree):
            raise TypeError("argument must be Oid or Tree")

        tree_cptr = ffi.new('git_tree **')
        ffi.buffer(tree_cptr)[:] = tree._pointer[:]
        err = C.git_index_read_tree(self._index, tree_cptr[0])
        check_error(err)

    def write_tree(self, repo=None):
        """Create a tree out of the Index. Return the <Oid> object of the
        written tree.

        The contents of the index will be written out to the object
        database. If there is no associated repository, 'repo' must be
        passed. If there is an associated repository and 'repo' is
        passed, then that repository will be used instead.

        It returns the id of the resulting tree.
        """
        coid = ffi.new('git_oid *')

        repo = repo or self._repo

        if repo:
            err = C.git_index_write_tree_to(coid, self._index, repo._repo)
        else:
            err = C.git_index_write_tree(coid, self._index)

        check_error(err)
        return Oid(raw=bytes(ffi.buffer(coid)[:]))

    def remove(self, path, level=0):
        """Remove an entry from the Index.
        """
        err = C.git_index_remove(self._index, to_bytes(path), level)
        check_error(err, io=True)

    def remove_all(self, pathspecs):
        """Remove all index entries matching pathspecs.
        """
        with StrArray(pathspecs) as arr:
            err = C.git_index_remove_all(self._index, arr, ffi.NULL, ffi.NULL)
            check_error(err, io=True)

    def add_all(self, pathspecs=None):
        """Add or update index entries matching files in the working directory.

        If pathspecs are specified, only files matching those pathspecs will
        be added.
        """
        pathspecs = pathspecs or []
        with StrArray(pathspecs) as arr:
            err = C.git_index_add_all(self._index, arr, 0, ffi.NULL, ffi.NULL)
            check_error(err, io=True)

    def add(self, path_or_entry):
        """Add or update an entry in the Index.

        If a path is given, that file will be added. The path must be relative
        to the root of the worktree and the Index must be associated with a
        repository.

        If an IndexEntry is given, that entry will be added or update in the
        Index without checking for the existence of the path or id.
        """
        if isinstance(path_or_entry, IndexEntry):
            entry = path_or_entry
            centry, str_ref = entry._to_c()
            err = C.git_index_add(self._index, centry)
        elif isinstance(path_or_entry, str) or hasattr(path_or_entry, '__fspath__'):
            path = path_or_entry
            err = C.git_index_add_bypath(self._index, to_bytes(path))
        else:
            raise TypeError('argument must be string or IndexEntry')

        check_error(err, io=True)

    def diff_to_workdir(self, flags=0, context_lines=3, interhunk_lines=0):
        """
        Diff the index against the working directory. Return a <Diff> object
        with the differences between the index and the working copy.

        Parameters:

        flags
            A GIT_DIFF_* constant.

        context_lines
            The number of unchanged lines that define the boundary of a hunk
            (and to display before and after).

        interhunk_lines
            The maximum number of unchanged lines between hunk boundaries
            before the hunks will be merged into a one.
        """
        repo = self._repo
        if repo is None:
            raise ValueError('diff needs an associated repository')

        copts = ffi.new('git_diff_options *')
        err = C.git_diff_options_init(copts, 1)
        check_error(err)

        copts.flags = flags
        copts.context_lines = context_lines
        copts.interhunk_lines = interhunk_lines

        cdiff = ffi.new('git_diff **')
        err = C.git_diff_index_to_workdir(cdiff, repo._repo, self._index,
                                          copts)
        check_error(err)

        return Diff.from_c(bytes(ffi.buffer(cdiff)[:]), repo)

    def diff_to_tree(self, tree, flags=0, context_lines=3, interhunk_lines=0):
        """
        Diff the index against a tree.  Return a <Diff> object with the
        differences between the index and the given tree.

        Parameters:

        tree
            The tree to diff.

        flags
            A GIT_DIFF_* constant.

        context_lines
            The number of unchanged lines that define the boundary of a hunk
            (and to display before and after).

        interhunk_lines
            The maximum number of unchanged lines between hunk boundaries
            before the hunks will be merged into a one.
        """
        repo = self._repo
        if repo is None:
            raise ValueError('diff needs an associated repository')

        if not isinstance(tree, Tree):
            raise TypeError('tree must be a Tree')

        copts = ffi.new('git_diff_options *')
        err = C.git_diff_options_init(copts, 1)
        check_error(err)

        copts.flags = flags
        copts.context_lines = context_lines
        copts.interhunk_lines = interhunk_lines

        ctree = ffi.new('git_tree **')
        ffi.buffer(ctree)[:] = tree._pointer[:]

        cdiff = ffi.new('git_diff **')
        err = C.git_diff_tree_to_index(cdiff, repo._repo, ctree[0],
                                       self._index, copts)
        check_error(err)

        return Diff.from_c(bytes(ffi.buffer(cdiff)[:]), repo)


    #
    # Conflicts
    #
    _conflicts = None

    @property
    def conflicts(self):
        """A collection of conflict information

        If there are no conflicts None is returned. Otherwise return an object
        that represents the conflicts in the index.

        This object presents a mapping interface with the paths as keys. You
        can use the ``del`` operator to remove a conflict from the Index.

        Each conflict is made up of three elements. Access or iteration
        of the conflicts returns a three-tuple of
        :py:class:`~pygit2.IndexEntry`. The first is the common
        ancestor, the second is the "ours" side of the conflict, and the
        third is the "theirs" side.

        These elements may be None depending on which sides exist for
        the particular conflict.
        """
        if not C.git_index_has_conflicts(self._index):
            self._conflicts = None
            return None

        if self._conflicts is None or self._conflicts() is None:
            conflicts = ConflictCollection(self)
            self._conflicts = weakref.ref(conflicts)
            return conflicts

        return self._conflicts()


class IndexEntry:
    __slots__ = ['id', 'path', 'mode']

    def __init__(self, path, object_id, mode):
        self.path = path
        """The path of this entry"""
        self.id = object_id
        """The id of the referenced object"""
        self.mode = mode
        """The mode of this entry, a GIT_FILEMODE_* value"""

    @property
    def oid(self):
        # For backwards compatibility
        return self.id

    @property
    def hex(self):
        """The id of the referenced object as a hex string"""
        return self.id.hex

    def __str__(self):
        return f'<path={self.path} id={self.hex} mode={self.mode}>'

    def __repr__(self):
        t = type(self)
        return f"<{t.__module__}.{t.__qualname__} path={self.path} id={self.hex} mode={self.mode}>"

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, IndexEntry):
            return NotImplemented
        return self.path == other.path and self.id == other.id and self.mode == other.mode

    def _to_c(self):
        """Convert this entry into the C structure

        The first returned arg is the pointer, the second is the reference to
        the string we allocated, which we need to exist past this function
        """
        centry = ffi.new('git_index_entry *')
        # basically memcpy()
        ffi.buffer(ffi.addressof(centry, 'id'))[:] = self.id.raw[:]
        centry.mode = self.mode
        path = ffi.new('char[]', to_bytes(self.path))
        centry.path = path

        return centry, path

    @classmethod
    def _from_c(cls, centry):
        if centry == ffi.NULL:
            return None

        entry = cls.__new__(cls)
        entry.path = to_str(ffi.string(centry.path))
        entry.mode = centry.mode
        entry.id = Oid(raw=bytes(ffi.buffer(ffi.addressof(centry, 'id'))[:]))

        return entry


class ConflictCollection:

    def __init__(self, index):
        self._index = index

    def __getitem__(self, path):
        cancestor = ffi.new('git_index_entry **')
        cours = ffi.new('git_index_entry **')
        ctheirs = ffi.new('git_index_entry **')

        err = C.git_index_conflict_get(cancestor, cours, ctheirs,
                                       self._index._index, to_bytes(path))
        check_error(err)

        ancestor = IndexEntry._from_c(cancestor[0])
        ours = IndexEntry._from_c(cours[0])
        theirs = IndexEntry._from_c(ctheirs[0])

        return ancestor, ours, theirs

    def __delitem__(self, path):
        err = C.git_index_conflict_remove(self._index._index, to_bytes(path))
        check_error(err)

    def __iter__(self):
        return ConflictIterator(self._index)

    def __contains__(self, path):
        cancestor = ffi.new('git_index_entry **')
        cours = ffi.new('git_index_entry **')
        ctheirs = ffi.new('git_index_entry **')

        err = C.git_index_conflict_get(cancestor, cours, ctheirs,
                                       self._index._index, to_bytes(path))
        if err == C.GIT_ENOTFOUND:
            return False

        check_error(err)
        return True


class ConflictIterator:

    def __init__(self, index):
        citer = ffi.new('git_index_conflict_iterator **')
        err = C.git_index_conflict_iterator_new(citer, index._index)
        check_error(err)
        self._index = index
        self._iter = citer[0]

    def __del__(self):
        C.git_index_conflict_iterator_free(self._iter)

    def next(self):
        return self.__next__()

    def __next__(self):
        cancestor = ffi.new('git_index_entry **')
        cours = ffi.new('git_index_entry **')
        ctheirs = ffi.new('git_index_entry **')

        err = C.git_index_conflict_next(cancestor, cours, ctheirs, self._iter)
        if err == C.GIT_ITEROVER:
            raise StopIteration

        check_error(err)

        ancestor = IndexEntry._from_c(cancestor[0])
        ours = IndexEntry._from_c(cours[0])
        theirs = IndexEntry._from_c(ctheirs[0])

        return ancestor, ours, theirs

    def __iter__(self):
        return self
