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

from ._pygit2 import Oid
from .callbacks import git_fetch_options, RemoteCallbacks
from .errors import check_error
from .ffi import ffi, C


class Submodule:

    @classmethod
    def _from_c(cls, repo, cptr):
        subm = cls.__new__(cls)

        subm._repo = repo
        subm._subm = cptr

        return subm

    def __del__(self):
        C.git_submodule_free(self._subm)

    def open(self):
        """Open the repository for a submodule."""
        crepo = ffi.new('git_repository **')
        err = C.git_submodule_open(crepo, self._subm)
        check_error(err)

        return self._repo._from_c(crepo[0], True)

    def init(self, overwrite: bool = False):
        """
        Just like "git submodule init", this copies information about the submodule
        into ".git/config".

        Parameters:

        overwrite
            By default, existing submodule entries will not be overwritten,
            but setting this to True forces them to be updated.
        """
        err = C.git_submodule_init(self._subm, int(overwrite))
        check_error(err)

    def update(self, init: bool = False, callbacks: RemoteCallbacks = None):
        """
        Update a submodule. This will clone a missing submodule and checkout
        the subrepository to the commit specified in the index of the
        containing repository. If the submodule repository doesn't contain the
        target commit (e.g. because fetchRecurseSubmodules isn't set), then the
        submodule is fetched using the fetch options supplied in options.

        Parameters:

        init
            If the submodule is not initialized, setting this flag to True will
            initialize the submodule before updating. Otherwise, this will raise
            an error if attempting to update an uninitialized repository.

        callbacks
            Optional RemoteCallbacks to clone or fetch the submodule.
        """

        opts = ffi.new('git_submodule_update_options *')
        C.git_submodule_update_options_init(opts, C.GIT_SUBMODULE_UPDATE_OPTIONS_VERSION)

        with git_fetch_options(callbacks, opts=opts.fetch_opts) as payload:
            err = C.git_submodule_update(self._subm, int(init), opts)
            payload.check_error(err)

    def reload(self, force: bool = False):
        """
        Reread submodule info from config, index, and HEAD.

        Call this to reread cached submodule information for this submodule if
        you have reason to believe that it has changed.

        Parameters:

        force
            Force reload even if the data doesn't seem out of date
        """
        err = C.git_submodule_reload(self._subm, int(force))
        check_error(err)

    @property
    def name(self):
        """Name of the submodule."""
        name = C.git_submodule_name(self._subm)
        return ffi.string(name).decode('utf-8')

    @property
    def path(self):
        """Path of the submodule."""
        path = C.git_submodule_path(self._subm)
        return ffi.string(path).decode('utf-8')

    @property
    def url(self):
        """URL of the submodule."""
        url = C.git_submodule_url(self._subm)
        return ffi.string(url).decode('utf-8')

    @property
    def branch(self):
        """Branch that is to be tracked by the submodule."""
        branch = C.git_submodule_branch(self._subm)
        return ffi.string(branch).decode('utf-8')

    @property
    def head_id(self):
        """Head of the submodule."""
        head = C.git_submodule_head_id(self._subm)
        return Oid(raw=bytes(ffi.buffer(head)[:]))
