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
from ._pygit2 import Oid
from .callbacks import git_fetch_options, git_push_options, git_remote_callbacks
from .errors import check_error
from .ffi import ffi, C
from .refspec import Refspec
from .utils import maybe_string, to_bytes, strarray_to_strings, StrArray


class TransferProgress:
    """Progress downloading and indexing data during a fetch.
    """

    def __init__(self, tp):

        self.total_objects = tp.total_objects
        """Total number of objects to download"""

        self.indexed_objects = tp.indexed_objects
        """Objects which have been indexed"""

        self.received_objects = tp.received_objects
        """Objects which have been received up to now"""

        self.local_objects = tp.local_objects
        """Local objects which were used to fix the thin pack"""

        self.total_deltas = tp.total_deltas
        """Total number of deltas in the pack"""

        self.indexed_deltas = tp.indexed_deltas
        """Deltas which have been indexed"""

        self.received_bytes = tp.received_bytes
        """"Number of bytes received up to now"""


class Remote:

    def __init__(self, repo, ptr):
        """The constructor is for internal use only.
        """
        self._repo = repo
        self._remote = ptr
        self._stored_exception = None

    def __del__(self):
        C.git_remote_free(self._remote)

    @property
    def name(self):
        """Name of the remote"""

        return maybe_string(C.git_remote_name(self._remote))

    @property
    def url(self):
        """Url of the remote"""

        return maybe_string(C.git_remote_url(self._remote))

    @property
    def push_url(self):
        """Push url of the remote"""

        return maybe_string(C.git_remote_pushurl(self._remote))

    def connect(self, callbacks=None, direction=C.GIT_DIRECTION_FETCH, proxy=None):
        """Connect to the remote.

        Parameters:

        proxy : None or True or str
            Proxy configuration. Can be one of:

            * `None` (the default) to disable proxy usage
            * `True` to enable automatic proxy detection
            * an url to a proxy (`http://proxy.example.org:3128/`)
        """
        proxy_opts = ffi.new('git_proxy_options *')
        C.git_proxy_options_init(proxy_opts, C.GIT_PROXY_OPTIONS_VERSION)
        self.__set_proxy(proxy_opts, proxy)
        with git_remote_callbacks(callbacks) as payload:
            err = C.git_remote_connect(self._remote, direction,
                                       payload.remote_callbacks, proxy_opts,
                                       ffi.NULL)
            payload.check_error(err)

    def fetch(self, refspecs=None, message=None, callbacks=None, prune=C.GIT_FETCH_PRUNE_UNSPECIFIED, proxy=None, depth=0):
        """Perform a fetch against this remote. Returns a <TransferProgress>
        object.

        Parameters:

        prune : enum
            Either <GIT_FETCH_PRUNE_UNSPECIFIED>, <GIT_FETCH_PRUNE>, or
            <GIT_FETCH_NO_PRUNE>. The first uses the configuration from the
            repo, the second will remove any remote branch in the local
            repository that does not exist in the remote and the last will
            always keep the remote branches

        proxy : None or True or str
            Proxy configuration. Can be one of:

            * `None` (the default) to disable proxy usage
            * `True` to enable automatic proxy detection
            * an url to a proxy (`http://proxy.example.org:3128/`)

        depth : int
            Number of commits from the tip of each remote branch history to fetch.

            If non-zero, the number of commits from the tip of each remote
            branch history to fetch. If zero, all history is fetched.
            The default is 0 (all history is fetched).
        """
        with git_fetch_options(callbacks) as payload:
            opts = payload.fetch_options
            opts.prune = prune
            opts.depth = depth
            self.__set_proxy(opts.proxy_opts, proxy)
            with StrArray(refspecs) as arr:
                err = C.git_remote_fetch(self._remote, arr, opts, to_bytes(message))
                payload.check_error(err)

        return TransferProgress(C.git_remote_stats(self._remote))

    def ls_remotes(self, callbacks=None, proxy=None):
        """
        Return a list of dicts that maps to `git_remote_head` from a
        `ls_remotes` call.

        Parameters:

        callbacks : Passed to connect()

        proxy : Passed to connect()
        """

        self.connect(callbacks=callbacks, proxy=proxy)

        refs = ffi.new('git_remote_head ***')
        refs_len = ffi.new('size_t *')

        err = C.git_remote_ls(refs, refs_len, self._remote)
        check_error(err)

        results = []
        for i in range(int(refs_len[0])):
            ref = refs[0][i]
            local = bool(ref.local)
            if local:
                loid = Oid(raw=bytes(ffi.buffer(ref.loid.id)[:]))
            else:
                loid = None

            remote = {
                "local": local,
                "loid": loid,
                "name": maybe_string(ref.name),
                "symref_target": maybe_string(ref.symref_target),
                "oid": Oid(raw=bytes(ffi.buffer(ref.oid.id)[:])),
            }

            results.append(remote)

        return results

    def prune(self, callbacks=None):
        """Perform a prune against this remote.
        """
        with git_remote_callbacks(callbacks) as payload:
            err = C.git_remote_prune(self._remote, payload.remote_callbacks)
            payload.check_error(err)

    @property
    def refspec_count(self):
        """Total number of refspecs in this remote"""

        return C.git_remote_refspec_count(self._remote)

    def get_refspec(self, n):
        """Return the <Refspec> object at the given position."""
        spec = C.git_remote_get_refspec(self._remote, n)
        return Refspec(self, spec)

    @property
    def fetch_refspecs(self):
        """Refspecs that will be used for fetching"""

        specs = ffi.new('git_strarray *')
        err = C.git_remote_get_fetch_refspecs(specs, self._remote)
        check_error(err)

        return strarray_to_strings(specs)

    @property
    def push_refspecs(self):
        """Refspecs that will be used for pushing"""

        specs = ffi.new('git_strarray *')
        err = C.git_remote_get_push_refspecs(specs, self._remote)
        check_error(err)

        return strarray_to_strings(specs)

    def push(self, specs, callbacks=None, proxy=None):
        """
        Push the given refspec to the remote. Raises ``GitError`` on protocol
        error or unpack failure.

        When the remote has a githook installed, that denies the reference this
        function will return successfully. Thus it is strongly recommended to
        install a callback, that implements
        :py:meth:`RemoteCallbacks.push_update_reference` and check the passed
        parameters for successfull operations.

        Parameters:

        specs : [str]
            Push refspecs to use.

        proxy : None or True or str
            Proxy configuration. Can be one of:

            * `None` (the default) to disable proxy usage
            * `True` to enable automatic proxy detection
            * an url to a proxy (`http://proxy.example.org:3128/`)
        """
        with git_push_options(callbacks) as payload:
            opts = payload.push_options
            self.__set_proxy(opts.proxy_opts, proxy)
            with StrArray(specs) as refspecs:
                err = C.git_remote_push(self._remote, refspecs, opts)
                payload.check_error(err)

    def __set_proxy(self, proxy_opts, proxy):
        if proxy is None:
            proxy_opts.type = C.GIT_PROXY_NONE
        elif proxy is True:
            proxy_opts.type = C.GIT_PROXY_AUTO
        elif type(proxy) is str:
            proxy_opts.type = C.GIT_PROXY_SPECIFIED
            # Keep url in memory, otherwise memory is freed and bad things happen
            self.__url = ffi.new('char[]', to_bytes(proxy))
            proxy_opts.url = self.__url
        else:
            raise TypeError("Proxy must be None, True, or a string")


class RemoteCollection:
    """Collection of configured remotes

    You can use this class to look up and manage the remotes configured
    in a repository.  You can access repositories using index
    access. E.g. to look up the "origin" remote, you can use

    >>> repo.remotes["origin"]
    """

    def __init__(self, repo):
        self._repo = repo;

    def __len__(self):
        names = ffi.new('git_strarray *')

        try:
            err = C.git_remote_list(names, self._repo._repo)
            check_error(err)

            return names.count
        finally:
            C.git_strarray_free(names)

    def __iter__(self):
        cremote = ffi.new('git_remote **')
        for name in self._ffi_names():
            err = C.git_remote_lookup(cremote, self._repo._repo, name)
            check_error(err)

            yield Remote(self._repo, cremote[0])

    def __getitem__(self, name):
        if isinstance(name, int):
            return list(self)[name]

        cremote = ffi.new('git_remote **')
        err = C.git_remote_lookup(cremote, self._repo._repo, to_bytes(name))
        check_error(err)

        return Remote(self._repo, cremote[0])

    def _ffi_names(self):
        names = ffi.new('git_strarray *')

        try:
            err = C.git_remote_list(names, self._repo._repo)
            check_error(err)

            for i in range(names.count):
                yield names.strings[i]
        finally:
            C.git_strarray_free(names)

    def names(self):
        """An iterator over the names of the available remotes."""
        for name in self._ffi_names():
            yield maybe_string(name)

    def create(self, name, url, fetch=None):
        """Create a new remote with the given name and url. Returns a <Remote>
        object.

        If 'fetch' is provided, this fetch refspec will be used instead of the
        default.
        """
        cremote = ffi.new('git_remote **')

        name = to_bytes(name)
        url = to_bytes(url)
        if fetch:
            fetch = to_bytes(fetch)
            err = C.git_remote_create_with_fetchspec(cremote, self._repo._repo, name, url, fetch)
        else:
            err = C.git_remote_create(cremote, self._repo._repo, name, url)

        check_error(err)

        return Remote(self._repo, cremote[0])

    def create_anonymous(self, url):
        """Create a new anonymous (in-memory only) remote with the given URL.
        Returns a <Remote> object.
        """
        cremote = ffi.new('git_remote **')
        url = to_bytes(url)
        err = C.git_remote_create_anonymous(cremote, self._repo._repo, url)
        check_error(err)
        return Remote(self._repo, cremote[0])

    def rename(self, name, new_name):
        """Rename a remote in the configuration. The refspecs in standard
        format will be renamed.

        Returns a list of fetch refspecs (list of strings) which were not in
        the standard format and thus could not be remapped.
        """

        if not new_name:
            raise ValueError("Current remote name must be a non-empty string")

        if not new_name:
            raise ValueError("New remote name must be a non-empty string")

        problems = ffi.new('git_strarray *')
        err = C.git_remote_rename(problems, self._repo._repo, to_bytes(name), to_bytes(new_name))
        check_error(err)

        ret = strarray_to_strings(problems)
        C.git_strarray_free(problems)

        return ret

    def delete(self, name):
        """Remove a remote from the configuration

        All remote-tracking branches and configuration settings for the remote will be removed.
        """
        err = C.git_remote_delete(self._repo._repo, to_bytes(name))
        check_error(err)

    def set_url(self, name, url):
        """ Set the URL for a remote
        """
        err = C.git_remote_set_url(self._repo._repo, to_bytes(name), to_bytes(url))
        check_error(err)

    def set_push_url(self, name, url):
        """Set the push-URL for a remote
        """
        err = C.git_remote_set_pushurl(self._repo._repo, to_bytes(name), to_bytes(url))
        check_error(err)

    def add_fetch(self, name, refspec):
        """Add a fetch refspec (str) to the remote
        """

        err = C.git_remote_add_fetch(self._repo._repo, to_bytes(name), to_bytes(refspec))
        check_error(err)

    def add_push(self, name, refspec):
        """Add a push refspec (str) to the remote
        """

        err = C.git_remote_add_push(self._repo._repo, to_bytes(name), to_bytes(refspec))
        check_error(err)
