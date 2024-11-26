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

"""
Settings mapping.
"""

from ssl import get_default_verify_paths

from . import _pygit2
from ._pygit2 import option
from .errors import GitError


class SearchPathList:

    def __getitem__(self, key):
        return option(_pygit2.GIT_OPT_GET_SEARCH_PATH, key)

    def __setitem__(self, key, value):
        option(_pygit2.GIT_OPT_SET_SEARCH_PATH, key, value)


class Settings:
    """Library-wide settings interface."""

    __slots__ = '_default_tls_verify_paths', '_ssl_cert_dir', '_ssl_cert_file'

    _search_path = SearchPathList()

    def __init__(self):
        """Initialize global pygit2 and libgit2 settings."""
        self._initialize_tls_certificate_locations()

    def _initialize_tls_certificate_locations(self):
        """Set up initial TLS file and directory lookup locations."""
        self._default_tls_verify_paths = get_default_verify_paths()
        try:
            self.set_ssl_cert_locations(
                self._default_tls_verify_paths.cafile,
                self._default_tls_verify_paths.capath,
            )
        except GitError as git_err:
            valid_msg = "TLS backend doesn't support certificate locations"
            if str(git_err) != valid_msg:
                raise
            self._default_tls_verify_paths = None
            self._ssl_cert_file = None
            self._ssl_cert_dir = None

    @property
    def search_path(self):
        """Configuration file search path.

        This behaves like an array whose indices correspond to the
        GIT_CONFIG_LEVEL_* values.  The local search path cannot be
        changed.
        """
        return self._search_path

    @property
    def mwindow_size(self):
        """Get or set the maximum mmap window size"""
        return option(_pygit2.GIT_OPT_GET_MWINDOW_SIZE)

    @mwindow_size.setter
    def mwindow_size(self, value):
        option(_pygit2.GIT_OPT_SET_MWINDOW_SIZE, value)

    @property
    def mwindow_mapped_limit(self):
        """
        Get or set the maximum memory that will be mapped in total by the
        library
        """
        return option(_pygit2.GIT_OPT_GET_MWINDOW_MAPPED_LIMIT)

    @mwindow_mapped_limit.setter
    def mwindow_mapped_limit(self, value):
        return option(_pygit2.GIT_OPT_SET_MWINDOW_MAPPED_LIMIT, value)

    @property
    def cached_memory(self):
        """
        Get the current bytes in cache and the maximum that would be
        allowed in the cache.
        """
        return option(_pygit2.GIT_OPT_GET_CACHED_MEMORY)

    def enable_caching(self, value=True):
        """
        Enable or disable caching completely.

        Because caches are repository-specific, disabling the cache
        cannot immediately clear all cached objects, but each cache will
        be cleared on the next attempt to update anything in it.
        """
        return option(_pygit2.GIT_OPT_ENABLE_CACHING, value)

    def disable_pack_keep_file_checks(self, value=True):
        """
        This will cause .keep file existence checks to be skipped when
        accessing packfiles, which can help performance with remote
        filesystems.
        """
        return option(_pygit2.GIT_OPT_DISABLE_PACK_KEEP_FILE_CHECKS, value)

    def cache_max_size(self, value):
        """
        Set the maximum total data size that will be cached in memory
        across all repositories before libgit2 starts evicting objects
        from the cache.  This is a soft limit, in that the library might
        briefly exceed it, but will start aggressively evicting objects
        from cache when that happens.  The default cache size is 256MB.
        """
        return option(_pygit2.GIT_OPT_SET_CACHE_MAX_SIZE, value)

    def cache_object_limit(self, object_type, value):
        """
        Set the maximum data size for the given type of object to be
        considered eligible for caching in memory.  Setting to value to
        zero means that that type of object will not be cached.
        Defaults to 0 for GIT_OBJECT_BLOB (i.e. won't cache blobs) and 4k
        for GIT_OBJECT_COMMIT, GIT_OBJECT_TREE, and GIT_OBJECT_TAG.
        """
        return option(_pygit2.GIT_OPT_SET_CACHE_OBJECT_LIMIT, object_type, value)

    @property
    def ssl_cert_file(self):
        """TLS certificate file path."""
        return self._ssl_cert_file

    @ssl_cert_file.setter
    def ssl_cert_file(self, value):
        """Set the TLS cert file path."""
        self.set_ssl_cert_locations(value, self._ssl_cert_dir)

    @ssl_cert_file.deleter
    def ssl_cert_file(self):
        """Reset the TLS cert file path."""
        self.ssl_cert_file = self._default_tls_verify_paths.cafile

    @property
    def ssl_cert_dir(self):
        """TLS certificates lookup directory path."""
        return self._ssl_cert_dir

    @ssl_cert_dir.setter
    def ssl_cert_dir(self, value):
        """Set the TLS certificate lookup folder."""
        self.set_ssl_cert_locations(self._ssl_cert_file, value)

    @ssl_cert_dir.deleter
    def ssl_cert_dir(self):
        """Reset the TLS certificate lookup folder."""
        self.ssl_cert_dir = self._default_tls_verify_paths.capath

    def set_ssl_cert_locations(self, cert_file, cert_dir):
        """
        Set the SSL certificate-authority locations.

        - `cert_file` is the location of a file containing several
          certificates concatenated together.
        - `cert_dir` is the location of a directory holding several
          certificates, one per file.

        Either parameter may be `NULL`, but not both.
        """
        option(_pygit2.GIT_OPT_SET_SSL_CERT_LOCATIONS, cert_file, cert_dir)
        self._ssl_cert_file = cert_file
        self._ssl_cert_dir = cert_dir
