# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
Utility functions related to analyzing/bundling dependencies.
"""

import ctypes.util
import io
import os
import re
import struct
import zipfile
from types import CodeType

import marshal

from PyInstaller import compat
from PyInstaller import log as logging
from PyInstaller.depend import bytecode
from PyInstaller.depend.dylib import include_library
from PyInstaller.exceptions import ExecCommandFailed
from PyInstaller.lib.modulegraph import modulegraph

logger = logging.getLogger(__name__)


# TODO find out if modules from base_library.zip could be somehow bundled into the .exe file.
def create_py3_base_library(libzip_filename, graph):
    """
    Package basic Python modules into .zip file. The .zip file with basic modules is necessary to have on PYTHONPATH
    for initializing libpython3 in order to run the frozen executable with Python 3.
    """
    # Import strip_paths_in_code locally to avoid cyclic import between building.utils and depend.utils (this module);
    # building.utils imports depend.bindepend, which in turn imports depend.utils.
    from PyInstaller.building.utils import strip_paths_in_code

    # Construct regular expression for matching modules that should be bundled into base_library.zip. Excluded are plain
    # 'modules' or 'submodules.ANY_NAME'. The match has to be exact - start and end of string not substring.
    regex_modules = '|'.join([rf'(^{x}$)' for x in compat.PY3_BASE_MODULES])
    regex_submod = '|'.join([rf'(^{x}\..*$)' for x in compat.PY3_BASE_MODULES])
    regex_str = regex_modules + '|' + regex_submod
    module_filter = re.compile(regex_str)

    try:
        # Remove .zip from previous run.
        if os.path.exists(libzip_filename):
            os.remove(libzip_filename)
        logger.debug('Adding python files to base_library.zip')
        # Class zipfile.PyZipFile is not suitable for PyInstaller needs.
        with zipfile.ZipFile(libzip_filename, mode='w') as zf:
            zf.debug = 3
            # Sort the graph nodes by identifier to ensure repeatable builds
            graph_nodes = list(graph.iter_graph())
            graph_nodes.sort(key=lambda item: item.identifier)
            for mod in graph_nodes:
                if type(mod) in (modulegraph.SourceModule, modulegraph.Package, modulegraph.CompiledModule):
                    # Bundling just required modules.
                    if module_filter.match(mod.identifier):
                        # Name inside the archive. The ZIP format specification requires forward slashes as directory
                        # separator.
                        if type(mod) is modulegraph.Package:
                            new_name = mod.identifier.replace('.', '/') + '/__init__.pyc'
                        else:
                            new_name = mod.identifier.replace('.', '/') + '.pyc'

                        # Write code to a file. This code is similar to py_compile.compile().
                        with io.BytesIO() as fc:
                            fc.write(compat.BYTECODE_MAGIC)
                            fc.write(struct.pack('<I', 0b01))  # PEP-552: hash-based pyc, check_source=False
                            fc.write(b'\00' * 8)  # Match behavior of `building.utils.compile_pymodule`
                            code = strip_paths_in_code(mod.code)  # Strip paths
                            marshal.dump(code, fc)
                            # Use a ZipInfo to set timestamp for deterministic build.
                            info = zipfile.ZipInfo(new_name)
                            zf.writestr(info, fc.getvalue())

    except Exception:
        logger.error('base_library.zip could not be created!')
        raise


def scan_code_for_ctypes(co):
    binaries = __recursively_scan_code_objects_for_ctypes(co)

    # If any of the libraries has been requested with anything else than the basename, drop that entry and warn the
    # user - PyInstaller would need to patch the compiled pyc file to make it work correctly!
    binaries = set(binaries)
    for binary in list(binaries):
        # 'binary' might be in some cases None. Some Python modules (e.g., PyObjC.objc._bridgesupport) might contain
        # code like this:
        #     dll = ctypes.CDLL(None)
        if not binary:
            # None values have to be removed too.
            binaries.remove(binary)
        elif binary != os.path.basename(binary):
            # TODO make these warnings show up somewhere.
            try:
                filename = co.co_filename
            except Exception:
                filename = 'UNKNOWN'
            logger.warning(
                "Ignoring %s imported from %s - only basenames are supported with ctypes imports!", binary, filename
            )
            binaries.remove(binary)

    binaries = _resolveCtypesImports(binaries)
    return binaries


def __recursively_scan_code_objects_for_ctypes(code: CodeType):
    """
    Detects ctypes dependencies, using reasonable heuristics that should cover most common ctypes usages; returns a
    list containing names of binaries detected as dependencies.
    """
    from PyInstaller.depend.bytecode import any_alias, search_recursively

    binaries = []
    ctypes_dll_names = {
        *any_alias("ctypes.CDLL"),
        *any_alias("ctypes.cdll.LoadLibrary"),
        *any_alias("ctypes.WinDLL"),
        *any_alias("ctypes.windll.LoadLibrary"),
        *any_alias("ctypes.OleDLL"),
        *any_alias("ctypes.oledll.LoadLibrary"),
        *any_alias("ctypes.PyDLL"),
        *any_alias("ctypes.pydll.LoadLibrary"),
    }
    find_library_names = {
        *any_alias("ctypes.util.find_library"),
    }

    for calls in bytecode.recursive_function_calls(code).values():
        for (name, args) in calls:
            if not len(args) == 1 or not isinstance(args[0], str):
                continue
            if name in ctypes_dll_names:
                # ctypes.*DLL() or ctypes.*dll.LoadLibrary()
                binaries.append(*args)
            elif name in find_library_names:
                # ctypes.util.find_library() needs to be handled separately, because we need to resolve the library base
                # name given as the argument (without prefix and suffix, e.g. 'gs') into corresponding full name (e.g.,
                # 'libgs.so.9').
                libname = args[0]
                if libname:
                    try:  # this try was inserted due to the ctypes bug https://github.com/python/cpython/issues/93094
                        libname = ctypes.util.find_library(libname)
                    except FileNotFoundError:
                        libname = None
                        logger.warning(
                            'ctypes.util.find_library raised a FileNotFoundError. '
                            'Supressing and assuming no lib with the name "%s" was found.', args[0]
                        )
                    if libname:
                        # On Windows, `find_library` may return a full pathname. See issue #1934.
                        libname = os.path.basename(libname)
                        binaries.append(libname)

    # The above handles any flavour of function/class call. We still need to capture the (albeit rarely used) case of
    # loading libraries with ctypes.cdll's getattr.
    for i in search_recursively(_scan_code_for_ctypes_getattr, code).values():
        binaries.extend(i)

    return binaries


_ctypes_getattr_regex = bytecode.bytecode_regex(
    rb"""
    # Matches 'foo.bar' or 'foo.bar.whizz'.

    # Load the 'foo'.
    (
      (?:(?:""" + bytecode._OPCODES_EXTENDED_ARG + rb""").)*
      (?:""" + bytecode._OPCODES_FUNCTION_GLOBAL + rb""").
    )

    # Load the 'bar.whizz' (one opcode per name component, each possibly preceded by name reference extension).
    (
      (?:
        (?:(?:""" + bytecode._OPCODES_EXTENDED_ARG + rb""").)*
        (?:""" + bytecode._OPCODES_FUNCTION_LOAD + rb""").
      )+
    )
"""
)


def _scan_code_for_ctypes_getattr(code: CodeType):
    """
    Detect uses of ``ctypes.cdll.library_name``, which implies that ``library_name.dll`` should be collected.
    """

    key_names = ("cdll", "oledll", "pydll", "windll")

    for match in bytecode.finditer(_ctypes_getattr_regex, code.co_code):
        name, attrs = match.groups()
        name = bytecode.load(name, code)
        attrs = bytecode.loads(attrs, code)

        if attrs and attrs[-1] == "LoadLibrary":
            continue

        # Capture `from ctypes import ole; ole.dll_name`.
        if len(attrs) == 1:
            if name in key_names:
                yield attrs[0] + ".dll"
        # Capture `import ctypes; ctypes.ole.dll_name`.
        if len(attrs) == 2:
            if name == "ctypes" and attrs[0] in key_names:
                yield attrs[1] + ".dll"


# TODO: reuse this code with modulegraph implementation.
def _resolveCtypesImports(cbinaries):
    """
    Completes ctypes BINARY entries for modules with their full path.

    Input is a list of c-binary-names (as found by `scan_code_instruction_for_ctypes`). Output is a list of tuples
    ready to be appended to the ``binaries`` of a modules.

    This function temporarily extents PATH, LD_LIBRARY_PATH or DYLD_LIBRARY_PATH (depending on the platform) by
    CONF['pathex'] so shared libs will be search there, too.

    Example:
    >>> _resolveCtypesImports(['libgs.so'])
    [(libgs.so', ''/usr/lib/libgs.so', 'BINARY')]
    """
    from ctypes.util import find_library

    from PyInstaller.config import CONF

    if compat.is_unix:
        envvar = "LD_LIBRARY_PATH"
    elif compat.is_darwin:
        envvar = "DYLD_LIBRARY_PATH"
    else:
        envvar = "PATH"

    def _setPaths():
        path = os.pathsep.join(CONF['pathex'])
        old = compat.getenv(envvar)
        if old is not None:
            path = os.pathsep.join((path, old))
        compat.setenv(envvar, path)
        return old

    def _restorePaths(old):
        if old is None:
            compat.unsetenv(envvar)
        else:
            compat.setenv(envvar, old)

    ret = []

    # Try to locate the shared library on the disk. This is done by calling ctypes.util.find_library with
    # ImportTracker's local paths temporarily prepended to the library search paths (and restored after the call).
    old = _setPaths()
    for cbin in cbinaries:
        try:
            # There is an issue with find_library() where it can run into errors trying to locate the library. See
            # #5734.
            cpath = find_library(os.path.splitext(cbin)[0])
        except FileNotFoundError:
            # In these cases, find_library() should return None.
            cpath = None
        if compat.is_unix:
            # CAVEAT: find_library() is not the correct function. ctype's documentation says that it is meant to resolve
            # only the filename (as a *compiler* does) not the full path. Anyway, it works well enough on Windows and
            # Mac OS. On Linux, we need to implement more code to find out the full path.
            if cpath is None:
                cpath = cbin
            # "man ld.so" says that we should first search LD_LIBRARY_PATH and then the ldcache.
            for d in compat.getenv(envvar, '').split(os.pathsep):
                if os.path.isfile(os.path.join(d, cpath)):
                    cpath = os.path.join(d, cpath)
                    break
            else:
                if LDCONFIG_CACHE is None:
                    load_ldconfig_cache()
                if cpath in LDCONFIG_CACHE:
                    cpath = LDCONFIG_CACHE[cpath]
                    assert os.path.isfile(cpath)
                else:
                    cpath = None
        if cpath is None:
            # Skip warning message if cbin (basename of library) is ignored. This prevents messages like:
            # 'W: library kernel32.dll required via ctypes not found'
            if not include_library(cbin):
                continue
            logger.warning("Library %s required via ctypes not found", cbin)
        else:
            if not include_library(cpath):
                continue
            ret.append((cbin, cpath, "BINARY"))
    _restorePaths(old)
    return ret


LDCONFIG_CACHE = None  # cache the output of `/sbin/ldconfig -p`


def load_ldconfig_cache():
    """
    Create a cache of the `ldconfig`-output to call it only once.
    It contains thousands of libraries and running it on every dylib is expensive.
    """
    global LDCONFIG_CACHE

    if LDCONFIG_CACHE is not None:
        return

    if compat.is_musl:
        # Musl deliberately doesn't use ldconfig. The ldconfig executable either doesn't exist or it's a functionless
        # executable which, on calling with any arguments, simply tells you that those arguments are invalid.
        LDCONFIG_CACHE = {}
        return

    from distutils.spawn import find_executable
    ldconfig = find_executable('ldconfig')
    if ldconfig is None:
        # If `ldconfig` is not found in $PATH, search for it in some fixed directories. Simply use a second call instead
        # of fiddling around with checks for empty env-vars and string-concat.
        ldconfig = find_executable('ldconfig', '/usr/sbin:/sbin:/usr/bin:/usr/sbin')

        # If we still could not find the 'ldconfig' command...
        if ldconfig is None:
            LDCONFIG_CACHE = {}
            return

    if compat.is_freebsd or compat.is_openbsd:
        # This has a quite different format than other Unixes:
        # [vagrant@freebsd-10 ~]$ ldconfig -r
        # /var/run/ld-elf.so.hints:
        #     search directories: /lib:/usr/lib:/usr/lib/compat:...
        #     0:-lgeom.5 => /lib/libgeom.so.5
        #   184:-lpython2.7.1 => /usr/local/lib/libpython2.7.so.1
        ldconfig_arg = '-r'
        splitlines_count = 2
        pattern = re.compile(r'^\s+\d+:-l(\S+)(\s.*)? => (\S+)')
    else:
        # Skip first line of the library list because it is just an informative line and might contain localized
        # characters. Example of first line with locale set to cs_CZ.UTF-8:
        #$ /sbin/ldconfig -p
        #V keši „/etc/ld.so.cache“ nalezeno knihoven: 2799
        #      libzvbi.so.0 (libc6,x86-64) => /lib64/libzvbi.so.0
        #      libzvbi-chains.so.0 (libc6,x86-64) => /lib64/libzvbi-chains.so.0
        ldconfig_arg = '-p'
        splitlines_count = 1
        pattern = re.compile(r'^\s+(\S+)(\s.*)? => (\S+)')

    try:
        text = compat.exec_command(ldconfig, ldconfig_arg)
    except ExecCommandFailed:
        logger.warning("Failed to execute ldconfig. Disabling LD cache.")
        LDCONFIG_CACHE = {}
        return

    text = text.strip().splitlines()[splitlines_count:]

    LDCONFIG_CACHE = {}
    for line in text:
        # :fixme: this assumes library names do not contain whitespace
        m = pattern.match(line)

        # Sanitize away any abnormal lines of output.
        if m is None:
            # Warn about it then skip the rest of this iteration.
            if re.search("Cache generated by:", line):
                # See #5540. This particular line is harmless.
                pass
            else:
                logger.warning("Unrecognised line of output %r from ldconfig", line)
            continue

        path = m.groups()[-1]
        if compat.is_freebsd or compat.is_openbsd:
            # Insert `.so` at the end of the lib's basename. soname and filename may have (different) trailing versions.
            # We assume the `.so` in the filename to mark the end of the lib's basename.
            bname = os.path.basename(path).split('.so', 1)[0]
            name = 'lib' + m.group(1)
            assert name.startswith(bname)
            name = bname + '.so' + name[len(bname):]
        else:
            name = m.group(1)
        # ldconfig may know about several versions of the same lib, e.g., different arch, different libc, etc.
        # Use the first entry.
        if name not in LDCONFIG_CACHE:
            LDCONFIG_CACHE[name] = path
