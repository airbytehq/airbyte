#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

"""Use a cache layer in front of entry point scanning."""

import errno
import glob
import hashlib
import importlib.metadata as importlib_metadata
import itertools
import json
import logging
import os
import os.path
import struct
import sys


log = logging.getLogger('stevedore._cache')


def _get_cache_dir():
    """Locate a platform-appropriate cache directory to use.

    Does not ensure that the cache directory exists.
    """
    # Linux, Unix, AIX, etc.
    if os.name == 'posix' and sys.platform != 'darwin':
        # use ~/.cache if empty OR not set
        base_path = os.environ.get("XDG_CACHE_HOME", None) \
            or os.path.expanduser('~/.cache')
        return os.path.join(base_path, 'python-entrypoints')

    # Mac OS
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Caches/Python Entry Points')

    # Windows (hopefully)
    else:
        base_path = os.environ.get('LOCALAPPDATA', None) \
            or os.path.expanduser('~\\AppData\\Local')
        return os.path.join(base_path, 'Python Entry Points')


def _get_mtime(name):
    try:
        s = os.stat(name)
        return s.st_mtime
    except OSError as err:
        if err.errno not in {errno.ENOENT, errno.ENOTDIR}:
            raise
    return -1.0


def _ftobytes(f):
    return struct.Struct('f').pack(f)


def _hash_settings_for_path(path):
    """Return a hash and the path settings that created it."""
    paths = []
    h = hashlib.sha256()

    # Tie the cache to the python interpreter, in case it is part of a
    # virtualenv.
    h.update(sys.executable.encode('utf-8'))
    h.update(sys.prefix.encode('utf-8'))

    for entry in path:
        mtime = _get_mtime(entry)
        h.update(entry.encode('utf-8'))
        h.update(_ftobytes(mtime))
        paths.append((entry, mtime))

        for ep_file in itertools.chain(
                glob.iglob(os.path.join(entry,
                                        '*.dist-info',
                                        'entry_points.txt')),
                glob.iglob(os.path.join(entry,
                                        '*.egg-info',
                                        'entry_points.txt'))
        ):
            mtime = _get_mtime(ep_file)
            h.update(ep_file.encode('utf-8'))
            h.update(_ftobytes(mtime))
            paths.append((ep_file, mtime))

    return (h.hexdigest(), paths)


def _build_cacheable_data():
    real_groups = importlib_metadata.entry_points()

    if not isinstance(real_groups, dict):
        # importlib-metadata 4.0 or later (or stdlib importlib.metadata in
        # Python 3.9 or later)
        real_groups = {
            group: real_groups.select(group=group)
            for group in real_groups.groups
        }

    # Convert the namedtuple values to regular tuples
    groups = {}
    for name, group_data in real_groups.items():
        existing = set()
        members = []
        groups[name] = members
        for ep in group_data:
            # Filter out duplicates that can occur when testing a
            # package that provides entry points using tox, where the
            # package is installed in the virtualenv that tox builds
            # and is present in the path as '.'.
            item = ep.name, ep.value, ep.group  # convert to tuple
            if item in existing:
                continue
            existing.add(item)
            members.append(item)
    return {
        'groups': groups,
        'sys.executable': sys.executable,
        'sys.prefix': sys.prefix,
    }


class Cache:

    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = _get_cache_dir()
        self._dir = cache_dir
        self._internal = {}
        self._disable_caching = False

        # Caching can be disabled by either placing .disable file into the
        # target directory or when python executable is under /tmp (this is the
        # case when executed from ansible)
        if any([os.path.isfile(os.path.join(self._dir, '.disable')),
                sys.executable[0:4] == '/tmp']):  # nosec B108
            self._disable_caching = True

    def _get_data_for_path(self, path):
        if path is None:
            path = sys.path

        internal_key = tuple(path)
        if internal_key in self._internal:
            return self._internal[internal_key]

        digest, path_values = _hash_settings_for_path(path)
        filename = os.path.join(self._dir, digest)
        try:
            log.debug('reading %s', filename)
            with open(filename, 'r') as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError):
            data = _build_cacheable_data()
            data['path_values'] = path_values
            if not self._disable_caching:
                try:
                    log.debug('writing to %s', filename)
                    os.makedirs(self._dir, exist_ok=True)
                    with open(filename, 'w') as f:
                        json.dump(data, f)
                except (IOError, OSError):
                    # Could not create cache dir or write file.
                    pass

        self._internal[internal_key] = data
        return data

    def get_group_all(self, group, path=None):
        result = []
        data = self._get_data_for_path(path)
        group_data = data.get('groups', {}).get(group, [])
        for vals in group_data:
            result.append(importlib_metadata.EntryPoint(*vals))
        return result

    def get_group_named(self, group, path=None):
        result = {}
        for ep in self.get_group_all(group, path=path):
            if ep.name not in result:
                result[ep.name] = ep
        return result

    def get_single(self, group, name, path=None):
        for name, ep in self.get_group_named(group, path=path).items():
            if name == name:
                return ep
        raise ValueError('No entrypoint {!r} in group {!r}'.format(
            group, name))


_c = Cache()
get_group_all = _c.get_group_all
get_group_named = _c.get_group_named
get_single = _c.get_single
