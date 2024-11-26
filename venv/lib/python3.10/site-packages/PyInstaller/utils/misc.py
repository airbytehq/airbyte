#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
This module contains miscellaneous functions that do not fit anywhere else.
"""

import glob
import os
import pprint
import codecs
import re
import tokenize
import io
import pathlib

from PyInstaller import log as logging
from PyInstaller.compat import is_win

logger = logging.getLogger(__name__)


def dlls_in_subdirs(directory):
    """
    Returns a list *.dll, *.so, *.dylib in the given directory and its subdirectories.
    """
    filelist = []
    for root, dirs, files in os.walk(directory):
        filelist.extend(dlls_in_dir(root))
    return filelist


def dlls_in_dir(directory):
    """
    Returns a list of *.dll, *.so, *.dylib in the given directory.
    """
    return files_in_dir(directory, ["*.so", "*.dll", "*.dylib"])


def files_in_dir(directory, file_patterns=None):
    """
    Returns a list of files in the given directory that match the given pattern.
    """

    file_patterns = file_patterns or []

    files = []
    for file_pattern in file_patterns:
        files.extend(glob.glob(os.path.join(directory, file_pattern)))
    return files


def get_path_to_toplevel_modules(filename):
    """
    Return the path to top-level directory that contains Python modules.

    It will look in parent directories for __init__.py files. The first parent directory without __init__.py is the
    top-level directory.

    Returned directory might be used to extend the PYTHONPATH.
    """
    curr_dir = os.path.dirname(os.path.abspath(filename))
    pattern = '__init__.py'

    # Try max. 10 levels up.
    try:
        for i in range(10):
            files = set(os.listdir(curr_dir))
            # 'curr_dir' is still not top-level; go to parent dir.
            if pattern in files:
                curr_dir = os.path.dirname(curr_dir)
            # Top-level dir found; return it.
            else:
                return curr_dir
    except IOError:
        pass
    # No top-level directory found, or error was encountered.
    return None


def mtime(fnm):
    try:
        # TODO: explain why this does not use os.path.getmtime() ?
        #       - It is probably not used because it returns float and not int.
        return os.stat(fnm)[8]
    except Exception:
        return 0


def save_py_data_struct(filename, data):
    """
    Save data into text file as Python data structure.
    :param filename:
    :param data:
    :return:
    """
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, 'w', encoding='utf-8') as f:
        pprint.pprint(data, f)


def load_py_data_struct(filename):
    """
    Load data saved as python code and interpret that code.
    :param filename:
    :return:
    """
    with open(filename, 'r', encoding='utf-8') as f:
        if is_win:
            # import versioninfo so that VSVersionInfo can parse correctly.
            from PyInstaller.utils.win32 import versioninfo  # noqa: F401

        return eval(f.read())


def absnormpath(apath):
    return os.path.abspath(os.path.normpath(apath))


def module_parent_packages(full_modname):
    """
    Return list of parent package names.
        'aaa.bb.c.dddd' ->  ['aaa', 'aaa.bb', 'aaa.bb.c']
    :param full_modname: Full name of a module.
    :return: List of parent module names.
    """
    prefix = ''
    parents = []
    # Ignore the last component in module name and get really just parent, grandparent, great grandparent, etc.
    for pkg in full_modname.split('.')[0:-1]:
        # Ensure that first item does not start with dot '.'
        prefix += '.' + pkg if prefix else pkg
        parents.append(prefix)
    return parents


def is_file_qt_plugin(filename):
    """
    Check if the given file is a Qt plugin file.
    :param filename: Full path to file to check.
    :return: True if given file is a Qt plugin file, False if not.
    """

    # Check the file contents; scan for QTMETADATA string. The scan is based on the brute-force Windows codepath of
    # findPatternUnloaded() from qtbase/src/corelib/plugin/qlibrary.cpp in Qt5.
    with open(filename, 'rb') as fp:
        fp.seek(0, os.SEEK_END)
        end_pos = fp.tell()

        SEARCH_CHUNK_SIZE = 8192
        QTMETADATA_MAGIC = b'QTMETADATA '

        magic_offset = -1
        while end_pos >= len(QTMETADATA_MAGIC):
            start_pos = max(end_pos - SEARCH_CHUNK_SIZE, 0)
            chunk_size = end_pos - start_pos
            # Is the remaining chunk large enough to hold the pattern?
            if chunk_size < len(QTMETADATA_MAGIC):
                break
            # Read and scan the chunk
            fp.seek(start_pos, os.SEEK_SET)
            buf = fp.read(chunk_size)
            pos = buf.rfind(QTMETADATA_MAGIC)
            if pos != -1:
                magic_offset = start_pos + pos
                break
            # Adjust search location for next chunk; ensure proper overlap.
            end_pos = start_pos + len(QTMETADATA_MAGIC) - 1
        if magic_offset == -1:
            return False

        return True


BOM_MARKERS_TO_DECODERS = {
    codecs.BOM_UTF32_LE: codecs.utf_32_le_decode,
    codecs.BOM_UTF32_BE: codecs.utf_32_be_decode,
    codecs.BOM_UTF32: codecs.utf_32_decode,
    codecs.BOM_UTF16_LE: codecs.utf_16_le_decode,
    codecs.BOM_UTF16_BE: codecs.utf_16_be_decode,
    codecs.BOM_UTF16: codecs.utf_16_decode,
    codecs.BOM_UTF8: codecs.utf_8_decode,
}
BOM_RE = re.compile(rb"\A(%s)?(.*)" % b"|".join(map(re.escape, BOM_MARKERS_TO_DECODERS)), re.DOTALL)


def decode(raw: bytes):
    """
    Decode bytes to string, respecting and removing any byte-order marks if present, or respecting but not removing any
    PEP263 encoding comments (# encoding: cp1252).
    """
    bom, raw = BOM_RE.match(raw).groups()
    if bom:
        return BOM_MARKERS_TO_DECODERS[bom](raw)[0]

    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    return raw.decode(encoding)


def is_iterable(arg):
    """
    Check if the passed argument is an iterable."
    """
    try:
        iter(arg)
    except TypeError:
        return False
    return True


def path_to_parent_archive(filename):
    """
    Check if the given file path points to a file inside an existing archive file. Returns first path from the set of
    parent paths that points to an existing file, or `None` if no such path exists (i.e., file is an actual stand-alone
    file).
    """
    for parent in pathlib.Path(filename).parents:
        if parent.is_file():
            return parent
    return None
