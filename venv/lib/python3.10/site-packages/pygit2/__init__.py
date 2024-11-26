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

# Standard Library
import functools

# Low level API
from ._pygit2 import *

# High level API
from .blame import Blame, BlameHunk
from .blob import BlobIO
from .callbacks import git_clone_options, git_fetch_options, get_credentials
from .callbacks import Payload, RemoteCallbacks, CheckoutCallbacks, StashApplyCallbacks
from .config import Config
from .credentials import *
from .errors import check_error, Passthrough
from .enums import SubmoduleIgnore, SubmoduleStatus
from .ffi import ffi, C
from .filter import Filter
from .index import Index, IndexEntry
from .remote import Remote
from .repository import Repository
from .packbuilder import PackBuilder
from .settings import Settings
from .submodule import Submodule
from .utils import to_bytes, to_str
from ._build import __version__


# Features
features = C.git_libgit2_features()
GIT_FEATURE_THREADS = C.GIT_FEATURE_THREADS
GIT_FEATURE_HTTPS = C.GIT_FEATURE_HTTPS
GIT_FEATURE_SSH = C.GIT_FEATURE_SSH

# GIT_REPOSITORY_INIT_*
GIT_REPOSITORY_INIT_OPTIONS_VERSION = C.GIT_REPOSITORY_INIT_OPTIONS_VERSION
GIT_REPOSITORY_INIT_BARE = C.GIT_REPOSITORY_INIT_BARE
GIT_REPOSITORY_INIT_NO_REINIT = C.GIT_REPOSITORY_INIT_NO_REINIT
GIT_REPOSITORY_INIT_NO_DOTGIT_DIR = C.GIT_REPOSITORY_INIT_NO_DOTGIT_DIR
GIT_REPOSITORY_INIT_MKDIR = C.GIT_REPOSITORY_INIT_MKDIR
GIT_REPOSITORY_INIT_MKPATH = C.GIT_REPOSITORY_INIT_MKPATH
GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE = C.GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE
GIT_REPOSITORY_INIT_RELATIVE_GITLINK = C.GIT_REPOSITORY_INIT_RELATIVE_GITLINK
GIT_REPOSITORY_INIT_SHARED_UMASK = C.GIT_REPOSITORY_INIT_SHARED_UMASK
GIT_REPOSITORY_INIT_SHARED_GROUP = C.GIT_REPOSITORY_INIT_SHARED_GROUP
GIT_REPOSITORY_INIT_SHARED_ALL = C.GIT_REPOSITORY_INIT_SHARED_ALL

# GIT_REPOSITORY_OPEN_*
GIT_REPOSITORY_OPEN_NO_SEARCH = C.GIT_REPOSITORY_OPEN_NO_SEARCH
GIT_REPOSITORY_OPEN_CROSS_FS  = C.GIT_REPOSITORY_OPEN_CROSS_FS
GIT_REPOSITORY_OPEN_BARE      = C.GIT_REPOSITORY_OPEN_BARE
GIT_REPOSITORY_OPEN_NO_DOTGIT = C.GIT_REPOSITORY_OPEN_NO_DOTGIT
GIT_REPOSITORY_OPEN_FROM_ENV  = C.GIT_REPOSITORY_OPEN_FROM_ENV

# GIT_REPOSITORY_STATE_*
GIT_REPOSITORY_STATE_NONE                    : int = C.GIT_REPOSITORY_STATE_NONE
GIT_REPOSITORY_STATE_MERGE                   : int = C.GIT_REPOSITORY_STATE_MERGE
GIT_REPOSITORY_STATE_REVERT                  : int = C.GIT_REPOSITORY_STATE_REVERT
GIT_REPOSITORY_STATE_REVERT_SEQUENCE         : int = C.GIT_REPOSITORY_STATE_REVERT_SEQUENCE
GIT_REPOSITORY_STATE_CHERRYPICK              : int = C.GIT_REPOSITORY_STATE_CHERRYPICK
GIT_REPOSITORY_STATE_CHERRYPICK_SEQUENCE     : int = C.GIT_REPOSITORY_STATE_CHERRYPICK_SEQUENCE
GIT_REPOSITORY_STATE_BISECT                  : int = C.GIT_REPOSITORY_STATE_BISECT
GIT_REPOSITORY_STATE_REBASE                  : int = C.GIT_REPOSITORY_STATE_REBASE
GIT_REPOSITORY_STATE_REBASE_INTERACTIVE      : int = C.GIT_REPOSITORY_STATE_REBASE_INTERACTIVE
GIT_REPOSITORY_STATE_REBASE_MERGE            : int = C.GIT_REPOSITORY_STATE_REBASE_MERGE
GIT_REPOSITORY_STATE_APPLY_MAILBOX           : int = C.GIT_REPOSITORY_STATE_APPLY_MAILBOX
GIT_REPOSITORY_STATE_APPLY_MAILBOX_OR_REBASE : int = C.GIT_REPOSITORY_STATE_APPLY_MAILBOX_OR_REBASE

# GIT_ATTR_CHECK_*
GIT_ATTR_CHECK_FILE_THEN_INDEX = C.GIT_ATTR_CHECK_FILE_THEN_INDEX
GIT_ATTR_CHECK_INDEX_THEN_FILE = C.GIT_ATTR_CHECK_INDEX_THEN_FILE
GIT_ATTR_CHECK_INDEX_ONLY      = C.GIT_ATTR_CHECK_INDEX_ONLY
GIT_ATTR_CHECK_NO_SYSTEM       = C.GIT_ATTR_CHECK_NO_SYSTEM
GIT_ATTR_CHECK_INCLUDE_HEAD    = C.GIT_ATTR_CHECK_INCLUDE_HEAD
GIT_ATTR_CHECK_INCLUDE_COMMIT  = C.GIT_ATTR_CHECK_INCLUDE_COMMIT

# GIT_FETCH_PRUNE
GIT_FETCH_PRUNE_UNSPECIFIED    = C.GIT_FETCH_PRUNE_UNSPECIFIED
GIT_FETCH_PRUNE                = C.GIT_FETCH_PRUNE
GIT_FETCH_NO_PRUNE             = C.GIT_FETCH_NO_PRUNE

# GIT_CHECKOUT_NOTIFY_*
GIT_CHECKOUT_NOTIFY_NONE       : int = C.GIT_CHECKOUT_NOTIFY_NONE
GIT_CHECKOUT_NOTIFY_CONFLICT   : int = C.GIT_CHECKOUT_NOTIFY_CONFLICT
GIT_CHECKOUT_NOTIFY_DIRTY      : int = C.GIT_CHECKOUT_NOTIFY_DIRTY
GIT_CHECKOUT_NOTIFY_UPDATED    : int = C.GIT_CHECKOUT_NOTIFY_UPDATED
GIT_CHECKOUT_NOTIFY_UNTRACKED  : int = C.GIT_CHECKOUT_NOTIFY_UNTRACKED
GIT_CHECKOUT_NOTIFY_IGNORED    : int = C.GIT_CHECKOUT_NOTIFY_IGNORED
GIT_CHECKOUT_NOTIFY_ALL        : int = C.GIT_CHECKOUT_NOTIFY_ALL

# GIT_STASH_APPLY_PROGRESS_*
GIT_STASH_APPLY_PROGRESS_NONE               : int = C.GIT_STASH_APPLY_PROGRESS_NONE
GIT_STASH_APPLY_PROGRESS_LOADING_STASH      : int = C.GIT_STASH_APPLY_PROGRESS_LOADING_STASH
GIT_STASH_APPLY_PROGRESS_ANALYZE_INDEX      : int = C.GIT_STASH_APPLY_PROGRESS_ANALYZE_INDEX
GIT_STASH_APPLY_PROGRESS_ANALYZE_MODIFIED   : int = C.GIT_STASH_APPLY_PROGRESS_ANALYZE_MODIFIED
GIT_STASH_APPLY_PROGRESS_ANALYZE_UNTRACKED  : int = C.GIT_STASH_APPLY_PROGRESS_ANALYZE_UNTRACKED
GIT_STASH_APPLY_PROGRESS_CHECKOUT_UNTRACKED : int = C.GIT_STASH_APPLY_PROGRESS_CHECKOUT_UNTRACKED
GIT_STASH_APPLY_PROGRESS_CHECKOUT_MODIFIED  : int = C.GIT_STASH_APPLY_PROGRESS_CHECKOUT_MODIFIED
GIT_STASH_APPLY_PROGRESS_DONE               : int = C.GIT_STASH_APPLY_PROGRESS_DONE

# libgit version tuple
LIBGIT2_VER = (LIBGIT2_VER_MAJOR, LIBGIT2_VER_MINOR, LIBGIT2_VER_REVISION)

def init_repository(path, bare=False,
                    flags=GIT_REPOSITORY_INIT_MKPATH,
                    mode=0,
                    workdir_path=None,
                    description=None,
                    template_path=None,
                    initial_head=None,
                    origin_url=None):
    """
    Creates a new Git repository in the given *path*.

    If *bare* is True the repository will be bare, i.e. it will not have a
    working copy.

    The *flags* may be a combination of:

    - GIT_REPOSITORY_INIT_BARE (overriden by the *bare* parameter)
    - GIT_REPOSITORY_INIT_NO_REINIT
    - GIT_REPOSITORY_INIT_NO_DOTGIT_DIR
    - GIT_REPOSITORY_INIT_MKDIR
    - GIT_REPOSITORY_INIT_MKPATH (set by default)
    - GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE

    The *mode* parameter may be any of GIT_REPOSITORY_SHARED_UMASK (default),
    GIT_REPOSITORY_SHARED_GROUP or GIT_REPOSITORY_INIT_SHARED_ALL, or a custom
    value.

    The *workdir_path*, *description*, *template_path*, *initial_head* and
    *origin_url* are all strings.

    See libgit2's documentation on git_repository_init_ext for further details.
    """
    # Pre-process input parameters
    if path is None:
        raise TypeError('Expected string type for path, found None.')

    if bare:
        flags |= GIT_REPOSITORY_INIT_BARE

    # Options
    options = ffi.new('git_repository_init_options *')
    C.git_repository_init_options_init(options,
                                       GIT_REPOSITORY_INIT_OPTIONS_VERSION)
    options.flags = flags
    options.mode = mode

    if workdir_path:
        workdir_path_ref = ffi.new('char []', to_bytes(workdir_path))
        options.workdir_path = workdir_path_ref

    if description:
        description_ref = ffi.new('char []', to_bytes(description))
        options.description = description_ref

    if template_path:
        template_path_ref = ffi.new('char []', to_bytes(template_path))
        options.template_path = template_path_ref

    if initial_head:
        initial_head_ref = ffi.new('char []', to_bytes(initial_head))
        options.initial_head = initial_head_ref

    if origin_url:
        origin_url_ref = ffi.new('char []', to_bytes(origin_url))
        options.origin_url = origin_url_ref

    # Call
    crepository = ffi.new('git_repository **')
    err = C.git_repository_init_ext(crepository, to_bytes(path), options)
    check_error(err)

    # Ok
    return Repository(to_str(path))


def clone_repository(
        url, path, bare=False, repository=None, remote=None,
        checkout_branch=None, callbacks=None, depth=0):
    """
    Clones a new Git repository from *url* in the given *path*.

    Returns: a Repository class pointing to the newly cloned repository.

    Parameters:

    url : str
        URL of the repository to clone.
    path : str
        Local path to clone into.
    bare : bool
        Whether the local repository should be bare.
    remote : callable
        Callback for the remote to use.

        The remote callback has `(Repository, name, url) -> Remote` as a
        signature. The Remote it returns will be used instead of the default
        one.
    repository : callable
        Callback for the repository to use.

        The repository callback has `(path, bare) -> Repository` as a
        signature. The Repository it returns will be used instead of creating a
        new one.
    checkout_branch : str
        Branch to checkout after the clone. The default is to use the remote's
        default branch.
    callbacks : RemoteCallbacks
        Object which implements the callbacks as methods.

        The callbacks should be an object which inherits from
        `pyclass:RemoteCallbacks`.
    depth : int
        Number of commits to clone.

        If greater than 0, creates a shallow clone with a history truncated to
        the specified number of commits.
        The default is 0 (full commit history).
    """

    if callbacks is None:
        callbacks = RemoteCallbacks()

    # Add repository and remote to the payload
    payload = callbacks
    payload.repository = repository
    payload.remote = remote

    with git_clone_options(payload):
        opts = payload.clone_options
        opts.bare = bare
        opts.fetch_opts.depth = depth

        if checkout_branch:
            checkout_branch_ref = ffi.new('char []', to_bytes(checkout_branch))
            opts.checkout_branch = checkout_branch_ref

        with git_fetch_options(payload, opts=opts.fetch_opts):
            crepo = ffi.new('git_repository **')
            err = C.git_clone(crepo, to_bytes(url), to_bytes(path), opts)
            payload.check_error(err)

    # Ok
    return Repository._from_c(crepo[0], owned=True)


tree_entry_key = functools.cmp_to_key(tree_entry_cmp)

settings = Settings()
