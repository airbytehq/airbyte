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
Find external dependencies of binary libraries.
"""

import ctypes.util
import os
import pathlib
import re
import sys
import sysconfig
import subprocess

from PyInstaller import compat
from PyInstaller import log as logging
from PyInstaller.depend import dylib, utils
from PyInstaller.utils.win32 import winutils

if compat.is_darwin:
    import PyInstaller.utils.osx as osxutils

logger = logging.getLogger(__name__)

_exe_machine_type = None
if compat.is_win:
    _exe_machine_type = winutils.get_pe_file_machine_type(compat.python_executable)

#- High-level binary dependency analysis


def _get_paths_for_parent_directory_preservation():
    """
    Return list of paths that serve as prefixes for parent-directory preservation of collected binaries and/or
    shared libraries. If a binary is collected from a location that starts with a path from this list, the relative
    directory structure is preserved within the frozen application bundle; otherwise, the binary is collected to the
    frozen application's top-level directory.
    """

    # Use only site-packages paths. We have no control over contents of `sys.path`, so using all paths from that may
    # lead to unintended behavior in corner cases. For example, if `sys.path` contained the drive root (see #7028),
    # all paths that do not match some other sub-path rooted in that drive will end up recognized as relative to the
    # drive root. In such case, any DLL collected from `c:\Windows\system32` will be collected into `Windows\system32`
    # sub-directory; ucrt DLLs collected from MSVC or Windows SDK installed in `c:\Program Files\...` will end up
    # collected into `Program Files\...` subdirectory; etc.
    #
    # On the other hand, the DLL parent directory preservation is primarily aimed at packages installed via PyPI
    # wheels, which are typically installed into site-packages. Therefore, limiting the directory preservation for
    # shared libraries collected from site-packages should do the trick, and should be reasonably safe.
    import site

    orig_paths = site.getsitepackages()
    orig_paths.append(site.getusersitepackages())

    # Explicitly excluded paths. `site.getsitepackages` seems to include `sys.prefix`, which we need to exclude, to
    # avoid issue swith DLLs in its sub-directories. We need both resolved and unresolved variant to handle cases
    # where `base_prefix` itself is a symbolic link (e.g., `scoop`-installed python on Windows, see #8023).
    excluded_paths = {
        pathlib.Path(sys.base_prefix),
        pathlib.Path(sys.base_prefix).resolve(),
        pathlib.Path(sys.prefix),
        pathlib.Path(sys.prefix).resolve(),
    }

    # For each path in orig_paths, append a resolved variant. This helps with linux venv where we need to consider
    # both `venv/lib/python3.11/site-packages` and `venv/lib/python3.11/site-packages` and `lib64` is a symlink
    # to `lib`.
    orig_paths += [pathlib.Path(path).resolve() for path in orig_paths]

    paths = set()
    for path in orig_paths:
        if not path:
            continue
        path = pathlib.Path(path)
        # Filter out non-directories (e.g., /path/to/python3x.zip) or non-existent paths
        if not path.is_dir():
            continue
        # Filter out explicitly excluded paths
        if path in excluded_paths:
            continue
        paths.add(path)

    # Sort by length (in term of path components) to ensure match against the longest common prefix (for example, match
    # /path/to/venv/lib/site-packages instead of /path/to/venv when both paths are in site paths).
    paths = sorted(paths, key=lambda x: len(x.parents), reverse=True)

    return paths


def _select_destination_directory(src_filename, parent_dir_preservation_paths):
    # Check parent directory preservation paths
    for parent_dir_preservation_path in parent_dir_preservation_paths:
        if parent_dir_preservation_path in src_filename.parents:
            # Collect into corresponding sub-directory.
            return src_filename.relative_to(parent_dir_preservation_path)

    # Collect into top-level directory.
    return src_filename.name


def binary_dependency_analysis(binaries, search_paths=None):
    """
    Perform binary dependency analysis on the given TOC list of collected binaries, by recursively scanning each binary
    for linked dependencies (shared library imports). Returns new TOC list that contains both original entries and their
    binary dependencies.

    Additional search paths for dependencies' full path resolution may be supplied via optional argument.
    """

    # Get all path prefixes for binaries' parent-directory preservation. For binaries collected from packages in (for
    # example) site-packages directory, we should try to preserve the parent directory structure.
    parent_dir_preservation_paths = _get_paths_for_parent_directory_preservation()

    # Keep track of processed binaries and processed dependencies.
    processed_binaries = set()
    processed_dependencies = set()

    # Keep track of unresolved dependencies, in order to defer the missing-library warnings until after everything has
    # been processed. This allows us to suppress warnings for dependencies that end up being collected anyway; for
    # details, see the end of this function.
    missing_dependencies = []

    # Populate output TOC with input binaries - this also serves as TODO list, as we iterate over it while appending
    # new entries at the end.
    output_toc = binaries[:]
    for dest_name, src_name, typecode in output_toc:
        # Do not process symbolic links (already present in input TOC list, or added during analysis below).
        if typecode == 'SYMLINK':
            continue

        # Keep track of processed binaries, to avoid unnecessarily repeating analysis of the same file. Use pathlib.Path
        # to avoid having to worry about case normalization.
        src_path = pathlib.Path(src_name)
        if src_path in processed_binaries:
            continue
        processed_binaries.add(src_path)

        logger.debug("Analyzing binary %r", src_name)

        # Analyze imports (linked dependencies)
        for dep_name, dep_src_path in get_imports(src_name, search_paths):
            logger.debug("Processing dependency, name: %r, resolved path: %r", dep_name, dep_src_path)

            # Skip unresolved dependencies. Defer the missing-library warnings until after binary dependency analysis
            # is complete.
            if not dep_src_path:
                missing_dependencies.append((dep_name, src_name))
                continue

            # Compare resolved dependency against global inclusion/exclusion rules.
            if not dylib.include_library(dep_src_path):
                logger.debug("Skipping dependency %r due to global exclusion rules.", dep_src_path)
                continue

            dep_src_path = pathlib.Path(dep_src_path)  # Turn into pathlib.Path for subsequent processing

            # Avoid processing this dependency if we have already processed it.
            if dep_src_path in processed_dependencies:
                logger.debug("Skipping dependency %r due to prior processing.", str(dep_src_path))
                continue
            processed_dependencies.add(dep_src_path)

            # Try to preserve parent directory structure, if applicable.
            # NOTE: do not resolve the source path, because on macOS and linux, it may be a versioned .so (e.g.,
            # libsomething.so.1, pointing at libsomething.so.1.2.3), and we need to collect it under original name!
            dep_dest_path = _select_destination_directory(dep_src_path, parent_dir_preservation_paths)
            dep_dest_path = pathlib.PurePath(dep_dest_path)  # Might be a str() if it is just a basename...

            # If we are collecting library into top-level directory on macOS, check whether it comes from a
            # .framework bundle. If it does, re-create the .framework bundle in the top-level directory
            # instead.
            if compat.is_darwin and dep_dest_path.parent == pathlib.PurePath('.'):
                if osxutils.is_framework_bundle_lib(dep_src_path):
                    # dst_src_path is parent_path/Name.framework/Versions/Current/Name
                    framework_parent_path = dep_src_path.parent.parent.parent.parent
                    dep_dest_path = pathlib.PurePath(dep_src_path.relative_to(framework_parent_path))

            logger.debug("Collecting dependency %r as %r.", str(dep_src_path), str(dep_dest_path))
            output_toc.append((str(dep_dest_path), str(dep_src_path), 'BINARY'))

            # On non-Windows, if we are not collecting the binary into application's top-level directory ('.'),
            # add a symbolic link from top-level directory to the actual location. This is to accommodate
            # LD_LIBRARY_PATH being set to the top-level application directory on linux (although library search
            # should be mostly done via rpaths, so this might be redundant) and to accommodate library path
            # rewriting on macOS, which assumes that the library was collected into top-level directory.
            if not compat.is_win and dep_dest_path.parent != pathlib.PurePath('.'):
                logger.debug("Adding symbolic link from %r to top-level application directory.", str(dep_dest_path))
                output_toc.append((str(dep_dest_path.name), str(dep_dest_path), 'SYMLINK'))

    # Display warnings about missing dependencies
    seen_binaries = set([
        os.path.normcase(os.path.basename(src_name)) for dest_name, src_name, typecode in output_toc
        if typecode != 'SYMLINK'
    ])
    for dependency_name, referring_binary in missing_dependencies:
        # Ignore libraries that we would not collect in the first place.
        if not dylib.include_library(dependency_name):
            continue
        # Apply global warning suppression rules.
        if not dylib.warn_missing_lib(dependency_name):
            continue
        # If the binary with a matching basename happens to be among the discovered binaries, suppress the message as
        # well. This might happen either because the library was collected by some other mechanism (for example, via
        # hook, or supplied by the user), or because it was discovered during the analysis of another binary (which,
        # for example, had properly set run-paths on Linux/macOS or was located next to that other analyzed binary on
        # Windows).
        if os.path.normcase(os.path.basename(dependency_name)) in seen_binaries:
            continue
        logger.warning("Library not found: could not resolve %r, dependency of %r.", dependency_name, referring_binary)

    return output_toc


#- Low-level import analysis


def get_imports(filename, search_paths=None):
    """
    Analyze the given binary file (shared library or executable), and obtain the list of shared libraries it imports
    (i.e., link-time dependencies).

    Returns set of tuples (name, fullpath). The name component is the referenced name, and on macOS, may not be just
    a base name. If the library's full path cannot be resolved, fullpath element is None.

    Additional list of search paths may be specified via `search_paths`, to be used as a fall-back when the
    platform-specific resolution mechanism fails to resolve a library fullpath.
    """
    if compat.is_win:
        if filename.lower().endswith(".manifest"):
            return []
        return _get_imports_pefile(filename, search_paths)
    elif compat.is_darwin:
        return _get_imports_macholib(filename, search_paths)
    else:
        return _get_imports_ldd(filename, search_paths)


def _get_imports_pefile(filename, search_paths):
    """
    Windows-specific helper for `get_imports`, which uses the `pefile` library to walk through PE header.
    """
    import pefile

    output = set()

    # By default, pefile library parses all PE information. We are only interested in the list of dependent dlls.
    # Performance is improved by reading only needed information. https://code.google.com/p/pefile/wiki/UsageExamples
    pe = pefile.PE(filename, fast_load=True)
    pe.parse_data_directories(
        directories=[
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT'],
        ],
        forwarded_exports_only=True,
        import_dllnames_only=True,
    )

    # If a library has no binary dependencies, pe.DIRECTORY_ENTRY_IMPORT does not exist.
    for entry in getattr(pe, 'DIRECTORY_ENTRY_IMPORT', []):
        dll_str = entry.dll.decode('utf-8')
        output.add(dll_str)

    # We must also read the exports table to find forwarded symbols:
    # http://blogs.msdn.com/b/oldnewthing/archive/2006/07/19/671238.aspx
    exported_symbols = getattr(pe, 'DIRECTORY_ENTRY_EXPORT', None)
    if exported_symbols:
        for symbol in exported_symbols.symbols:
            if symbol.forwarder is not None:
                # symbol.forwarder is a bytes object. Convert it to a string.
                forwarder = symbol.forwarder.decode('utf-8')
                # symbol.forwarder is for example 'KERNEL32.EnterCriticalSection'
                dll = forwarder.split('.')[0]
                output.add(dll + ".dll")

    pe.close()

    # Attempt to resolve full paths to referenced DLLs. Always add the input binary's parent directory to the search
    # paths.
    search_paths = [os.path.dirname(filename)] + (search_paths or [])
    output = {(lib, resolve_library_path(lib, search_paths)) for lib in output}

    return output


def _get_imports_ldd(filename, search_paths):
    """
    Helper for `get_imports`, which uses `ldd` to analyze shared libraries. Used on Linux and other POSIX-like platforms
    (with exception of macOS).
    """

    output = set()

    # Output of ldd varies between platforms...
    if compat.is_aix:
        # Match libs of the form
        #   'archivelib.a(objectmember.so/.o)'
        # or
        #   'sharedlib.so'
        # Will not match the fake lib '/unix'
        LDD_PATTERN = re.compile(r"^\s*(((?P<libarchive>(.*\.a))(?P<objectmember>\(.*\)))|((?P<libshared>(.*\.so))))$")
    elif compat.is_hpux:
        # Match libs of the form
        #   'sharedlib.so => full-path-to-lib
        # e.g.
        #   'libpython2.7.so =>      /usr/local/lib/hpux32/libpython2.7.so'
        LDD_PATTERN = re.compile(r"^\s+(.*)\s+=>\s+(.*)$")
    elif compat.is_solar:
        # Match libs of the form
        #   'sharedlib.so => full-path-to-lib
        # e.g.
        #   'libpython2.7.so.1.0 => /usr/local/lib/libpython2.7.so.1.0'
        # Will not match the platform specific libs starting with '/platform'
        LDD_PATTERN = re.compile(r"^\s+(.*)\s+=>\s+(.*)$")
    else:
        LDD_PATTERN = re.compile(r"\s*(.*?)\s+=>\s+(.*?)\s+\(.*\)")

    p = subprocess.run(
        ['ldd', filename],
        stdin=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding='utf-8',
    )

    for line in p.stderr.splitlines():
        if not line:
            continue
        # Python extensions (including stdlib ones) are not linked against python.so but rely on Python's symbols having
        # already been loaded into symbol space at runtime. musl's ldd issues a series of harmless warnings to stderr
        # telling us that those symbols are unfindable. These should be suppressed.
        elif line.startswith("Error relocating ") and line.endswith(" symbol not found"):
            continue
        # Propagate any other warnings it might have.
        print(line, file=sys.stderr)

    for line in p.stdout.splitlines():
        name = None  # Referenced name
        lib = None  # Resolved library path

        m = LDD_PATTERN.search(line)
        if m:
            if compat.is_aix:
                libarchive = m.group('libarchive')
                if libarchive:
                    # We matched an archive lib with a request for a particular embedded shared object.
                    #   'archivelib.a(objectmember.so/.o)'
                    lib = libarchive
                    name = os.path.basename(lib) + m.group('objectmember')
                else:
                    # We matched a stand-alone shared library.
                    #   'sharedlib.so'
                    lib = m.group('libshared')
                    name = os.path.basename(lib)
            elif compat.is_hpux:
                name, lib = m.group(1), m.group(2)
            else:
                name, lib = m.group(1), m.group(2)
            if name[:10] in ('linux-gate', 'linux-vdso'):
                # linux-gate is a fake library which does not exist and should be ignored. See also:
                # http://www.trilithium.com/johan/2005/08/linux-gate/
                continue

            if compat.is_cygwin:
                # exclude Windows system library
                if lib.lower().startswith('/cygdrive/c/windows/system'):
                    continue

            # Reset library path if it does not exist
            if not os.path.exists(lib):
                lib = None
        elif line.endswith("not found"):
            # On glibc-based linux distributions, missing libraries are marked with name.so => not found
            tokens = line.split('=>')
            if len(tokens) != 2:
                continue
            name = tokens[0].strip()
            lib = None
        else:
            # TODO: should we warn about unprocessed lines?
            continue

        # Fall back to searching the supplied search paths, if any.
        if not lib:
            lib = _resolve_library_path_in_search_paths(
                os.path.basename(name),  # Search for basename of the referenced name.
                search_paths,
            )

        # Normalize the resolved path, to remove any extraneous "../" elements.
        if lib:
            lib = os.path.normpath(lib)

        # Return referenced name as-is instead of computing a basename, to provide additional context when library
        # cannot be resolved.
        output.add((name, lib))

    return output


def _get_imports_macholib(filename, search_paths):
    """
    macOS-specific helper for `get_imports`, which uses `macholib` to analyze library load commands in Mach-O headers.
    """
    from macholib.dyld import dyld_find
    from macholib.mach_o import LC_RPATH
    from macholib.MachO import MachO

    output = set()
    referenced_libs = set()  # Libraries referenced in Mach-O headers.

    # Parent directory of the input binary and parent directory of python executable, used to substitute @loader_path
    # and @executable_path. The MacOS dylib loader (dyld) fully resolves the symbolic links when using @loader_path
    # and @executable_path references, so we need to do the same using `os.path.realpath`.
    bin_path = os.path.dirname(os.path.realpath(filename))
    python_bin_path = os.path.dirname(os.path.realpath(sys.executable))

    # Walk through Mach-O headers, and collect all referenced libraries.
    m = MachO(filename)
    for header in m.headers:
        for idx, name, lib in header.walkRelocatables():
            referenced_libs.add(lib)

    # Find LC_RPATH commands to collect rpaths. macholib does not handle @rpath, so we need to handle run paths
    # ourselves.
    run_paths = set()
    for header in m.headers:
        for command in header.commands:
            # A command is a tuple like:
            #   (<macholib.mach_o.load_command object at 0x>,
            #    <macholib.mach_o.rpath_command object at 0x>,
            #    '../lib\x00\x00')
            cmd_type = command[0].cmd
            if cmd_type == LC_RPATH:
                rpath = command[2].decode('utf-8')
                # Remove trailing '\x00' characters. E.g., '../lib\x00\x00'
                rpath = rpath.rstrip('\x00')
                # If run path starts with @, ensure it starts with either @loader_path or @executable_path. We cannot
                # process anything else.
                if rpath.startswith("@") and not rpath.startswith(("@executable_path", "@loader_path")):
                    logger.warning("Unsupported rpath format %r found in binary %r - ignoring...", rpath, filename)
                    continue
                run_paths.add(rpath)

    # For distributions like Anaconda, all of the dylibs are stored in the lib directory of the Python distribution, not
    # alongside of the .so's in each module's subdirectory. Usually, libraries using @rpath to reference their
    # dependencies also set up their run-paths via LC_RPATH commands. However, they are not strictly required to do so,
    # because run-paths are inherited from the process within which the libraries are loaded. Therefore, if the python
    # executable uses an LC_RPATH command to set up run-path that resolves the shared lib directory (for example,
    # `@loader_path/../lib` in case of the Anaconda python), all libraries loaded within the python process are able
    # to resolve the shared libraries within the environment's shared lib directory without using LC_RPATH commands
    # themselves.
    #
    # Our analysis does not account for inherited run-paths, and we attempt to work around this limitation by
    # registering the following fall-back run-path.
    run_paths.add(os.path.join(compat.base_prefix, 'lib'))

    def _resolve_using_loader_path(lib, bin_path, python_bin_path):
        # macholib does not support @loader_path, so replace it with @executable_path. Strictly speaking, @loader_path
        # should be anchored to parent directory of analyzed binary (`bin_path`), while @executable_path should be
        # anchored to the parent directory of the process' executable. Typically, this would be python executable
        # (`python_bin_path`), unless we are analyzing a collected 3rd party executable. In that case, `bin_path`
        # is correct option. So we first try resolving using `bin_path`, and then fall back to `python_bin_path`.
        # This does not account for transitive run paths of higher-order dependencies, but there is only so much we
        # can do here...
        if lib.startswith('@loader_path'):
            lib = lib.replace('@loader_path', '@executable_path')

        try:
            # Try resolving with binary's path first...
            return dyld_find(lib, executable_path=bin_path)
        except ValueError:
            # ... and fall-back to resolving with python executable's path
            try:
                return dyld_find(lib, executable_path=python_bin_path)
            except ValueError:
                return None

    def _resolve_using_path(lib):
        try:
            return dyld_find(lib)
        except ValueError:
            return None

    # Try to resolve full path of the referenced libraries.
    for referenced_lib in referenced_libs:
        resolved_lib = None

        # If path starts with @rpath, we have to handle it ourselves.
        if referenced_lib.startswith('@rpath'):
            lib = os.path.join(*referenced_lib.split(os.sep)[1:])  # Remove the @rpath/ prefix

            # Try all run paths.
            for run_path in run_paths:
                # Join the path.
                lib_path = os.path.join(run_path, lib)

                if lib_path.startswith(("@executable_path", "@loader_path")):
                    # Run path starts with @executable_path or @loader_path.
                    lib_path = _resolve_using_loader_path(lib_path, bin_path, python_bin_path)
                else:
                    # If run path was relative, anchor it to binary's location.
                    if not os.path.isabs(lib_path):
                        os.path.join(bin_path, lib_path)
                    lib_path = _resolve_using_path(lib_path)

                if lib_path and os.path.exists(lib_path):
                    resolved_lib = lib_path
                    break
        else:
            if referenced_lib.startswith(("@executable_path", "@loader_path")):
                resolved_lib = _resolve_using_loader_path(referenced_lib, bin_path, python_bin_path)
            else:
                resolved_lib = _resolve_using_path(referenced_lib)

        # Fall back to searching the supplied search paths, if any.
        if not resolved_lib:
            resolved_lib = _resolve_library_path_in_search_paths(
                os.path.basename(referenced_lib),  # Search for basename of the referenced name.
                search_paths,
            )

        # Normalize the resolved path, to remove any extraneous "../" elements.
        if resolved_lib:
            resolved_lib = os.path.normpath(resolved_lib)

        # Return referenced library name as-is instead of computing a basename. Full referenced name carries additional
        # information that might be useful for the caller to determine how to deal with unresolved library (e.g., ignore
        # unresolved libraries that are supposed to be located in system-wide directories).
        output.add((referenced_lib, resolved_lib))

    return output


#- Library full path resolution


def resolve_library_path(name, search_paths=None):
    """
    Given a library name, attempt to resolve full path to that library. The search for library is done via
    platform-specific mechanism and fall back to optionally-provided list of search paths. Returns None if library
    cannot be resolved. If give library name is already an absolute path, the given path is returned without any
    processing.
    """
    # No-op if path is already absolute.
    if os.path.isabs(name):
        return name

    if compat.is_unix:
        # Use platform-specific helper.
        fullpath = _resolve_library_path_unix(name)
        if fullpath:
            return fullpath
        # Fall back to searching the supplied search paths, if any
        return _resolve_library_path_in_search_paths(name, search_paths)
    elif compat.is_win:
        # Try the caller-supplied search paths, if any.
        fullpath = _resolve_library_path_in_search_paths(name, search_paths)
        if fullpath:
            return fullpath

        # Fall back to default Windows search paths, using the PATH environment variable (which should also include
        # the system paths, such as c:\windows and c:\windows\system32)
        win_search_paths = [path for path in compat.getenv('PATH', '').split(os.pathsep) if path]
        return _resolve_library_path_in_search_paths(name, win_search_paths)
    else:
        return ctypes.util.find_library(name)

    return None


# Compatibility aliases for hooks from contributed hooks repository. All of these now point to the high-level
# `resolve_library_path`.
findLibrary = resolve_library_path
findSystemLibrary = resolve_library_path


def _resolve_library_path_in_search_paths(name, search_paths=None):
    """
    Low-level helper for resolving given library name to full path in given list of search paths.
    """
    for search_path in search_paths or []:
        fullpath = os.path.join(search_path, name)
        if not os.path.isfile(fullpath):
            continue

        # On Windows, ensure that architecture matches that of running python interpreter.
        if compat.is_win:
            try:
                dll_machine_type = winutils.get_pe_file_machine_type(fullpath)
            except Exception:
                # A search path might contain a DLL that we cannot analyze; for example, a stub file. Skip over.
                continue
            if dll_machine_type != _exe_machine_type:
                continue

        return os.path.normpath(fullpath)

    return None


def _resolve_library_path_unix(name):
    """
    UNIX-specific helper for resolving library path.

    Emulates the algorithm used by dlopen. `name` must include the prefix, e.g., ``libpython2.4.so``.
    """
    assert compat.is_unix, "Current implementation for Unix only (Linux, Solaris, AIX, FreeBSD)"

    # Look in the LD_LIBRARY_PATH according to platform.
    if compat.is_aix:
        lp = compat.getenv('LIBPATH', '')
    elif compat.is_darwin:
        lp = compat.getenv('DYLD_LIBRARY_PATH', '')
    else:
        lp = compat.getenv('LD_LIBRARY_PATH', '')
    lib = _which_library(name, filter(None, lp.split(os.pathsep)))

    # Look in /etc/ld.so.cache
    # Solaris does not have /sbin/ldconfig. Just check if this file exists.
    if lib is None:
        utils.load_ldconfig_cache()
        lib = utils.LDCONFIG_CACHE.get(name)
        if lib:
            assert os.path.isfile(lib)

    # Look in the known safe paths.
    if lib is None:
        # Architecture independent locations.
        paths = ['/lib', '/usr/lib']
        # Architecture dependent locations.
        if compat.architecture == '32bit':
            paths.extend(['/lib32', '/usr/lib32'])
        else:
            paths.extend(['/lib64', '/usr/lib64'])
        # Machine dependent locations.
        if compat.machine == 'intel':
            if compat.architecture == '32bit':
                paths.extend(['/usr/lib/i386-linux-gnu'])
            else:
                paths.extend(['/usr/lib/x86_64-linux-gnu'])

        # On Debian/Ubuntu /usr/bin/python is linked statically with libpython. Newer Debian/Ubuntu with multiarch
        # support puts the libpythonX.Y.so in paths like /usr/lib/i386-linux-gnu/. Try to query the arch-specific
        # sub-directory, if available.
        arch_subdir = sysconfig.get_config_var('multiarchsubdir')
        if arch_subdir:
            arch_subdir = os.path.basename(arch_subdir)
            paths.append(os.path.join('/usr/lib', arch_subdir))
        else:
            logger.debug('Multiarch directory not detected.')

        # Termux (a Ubuntu like subsystem for Android) has an additional libraries directory.
        if os.path.isdir('/data/data/com.termux/files/usr/lib'):
            paths.append('/data/data/com.termux/files/usr/lib')

        if compat.is_aix:
            paths.append('/opt/freeware/lib')
        elif compat.is_hpux:
            if compat.architecture == '32bit':
                paths.append('/usr/local/lib/hpux32')
            else:
                paths.append('/usr/local/lib/hpux64')
        elif compat.is_freebsd or compat.is_openbsd:
            paths.append('/usr/local/lib')
        lib = _which_library(name, paths)

    # Give up :(
    if lib is None:
        return None

    # Resolve the file name into the soname
    if compat.is_freebsd or compat.is_aix or compat.is_openbsd:
        # On FreeBSD objdump does not show SONAME, and on AIX objdump does not exist, so we just return the lib we
        # have found.
        return lib
    else:
        dir = os.path.dirname(lib)
        return os.path.join(dir, _get_so_name(lib))


def _which_library(name, dirs):
    """
    Search for a shared library in a list of directories.

    Args:
        name:
            The library name including the `lib` prefix but excluding any `.so` suffix.
        dirs:
            An iterable of folders to search in.
    Returns:
        The path to the library if found or None otherwise.

    """
    matcher = _library_matcher(name)
    for path in filter(os.path.exists, dirs):
        for _path in os.listdir(path):
            if matcher(_path):
                return os.path.join(path, _path)


def _library_matcher(name):
    """
    Create a callable that matches libraries if **name** is a valid library prefix for input library full names.
    """
    return re.compile(name + r"[0-9]*\.").match


def _get_so_name(filename):
    """
    Return the soname of a library.

    Soname is useful when there are multiple symplinks to one library.
    """
    # TODO verify that objdump works on other unixes and not Linux only.
    cmd = ["objdump", "-p", filename]
    pattern = r'\s+SONAME\s+([^\s]+)'
    if compat.is_solar:
        cmd = ["elfdump", "-d", filename]
        pattern = r'\s+SONAME\s+[^\s]+\s+([^\s]+)'
    m = re.search(pattern, compat.exec_command(*cmd))
    return m.group(1)


#- Python shared library search


def get_python_library_path():
    """
    Find dynamic Python library that will be bundled with frozen executable.

    NOTE: This is a fallback option when the Python executable is likely statically linked with the Python library and
          we need to search more for it. For example, this is the case on Debian/Ubuntu.

    Return  full path to Python dynamic library or None when not found.

    We need to know name of the Python dynamic library for the bootloader. Bootloader has to know what library to
    load and not try to guess.

    Some linux distributions (e.g. debian-based) statically link the Python executable to the libpython,
    so bindepend does not include it in its output. In this situation let's try to find it.

    Custom Mac OS builds could possibly also have non-framework style libraries, so this method also checks for that
    variant as well.
    """
    def _find_lib_in_libdirs(*libdirs):
        for libdir in libdirs:
            for name in compat.PYDYLIB_NAMES:
                full_path = os.path.join(libdir, name)
                if not os.path.exists(full_path):
                    continue
                # Resolve potential symbolic links to achieve consistent results with linker-based search; e.g., on
                # POSIX systems, linker resolves unversioned library names (python3.X.so) to versioned ones
                # (libpython3.X.so.1.0) due to former being symbolic linkes to the latter. See #6831.
                full_path = os.path.realpath(full_path)
                if not os.path.exists(full_path):
                    continue
                return full_path
        return None

    # If this is Microsoft App Store Python, check the compat.base_path first. While compat.python_executable resolves
    # to actual python.exe file, the latter contains a relative library reference that we fail to properly resolve.
    if compat.is_ms_app_store:
        python_libname = _find_lib_in_libdirs(compat.base_prefix)
        if python_libname:
            return python_libname

    # Try to get Python library name from the Python executable. It assumes that Python library is not statically
    # linked.
    imported_libraries = get_imports(compat.python_executable)  # (name, fullpath) tuples
    for _, lib_path in imported_libraries:
        if lib_path is None:
            continue  # Skip unresolved imports
        for name in compat.PYDYLIB_NAMES:
            if os.path.normcase(os.path.basename(lib_path)) == name:
                # Python library found. Return absolute path to it.
                return lib_path

    # Python library NOT found. Resume searching using alternative methods.

    # Work around for python venv having VERSION.dll rather than pythonXY.dll
    if compat.is_win and any([os.path.normcase(lib_name) == 'version.dll' for lib_name, _ in imported_libraries]):
        pydll = 'python%d%d.dll' % sys.version_info[:2]
        return resolve_library_path(pydll, [os.path.dirname(compat.python_executable)])

    # Applies only to non Windows platforms and conda.

    if compat.is_conda:
        # Conda needs to be the first here since it overrules the operating system specific paths.
        python_libname = _find_lib_in_libdirs(os.path.join(compat.base_prefix, 'lib'))
        if python_libname:
            return python_libname

    elif compat.is_unix:
        for name in compat.PYDYLIB_NAMES:
            python_libname = findLibrary(name)
            if python_libname:
                return python_libname

    if compat.is_darwin or compat.is_linux:
        # On MacPython, Analysis.assemble is able to find the libpython with no additional help, asking for
        # sys.executable dependencies. However, this fails on system python, because the shared library is not listed as
        # a dependency of the binary (most probably it is opened at runtime using some dlopen trickery). This happens on
        # Mac OS when Python is compiled as Framework.
        # Linux using pyenv is similarly linked so that sys.executable dependencies does not yield libpython.so.

        # Python compiled as Framework contains same values in sys.prefix and exec_prefix. That is why we can use just
        # sys.prefix. In virtualenv, PyInstaller is not able to find Python library. We need special care for this case.
        python_libname = _find_lib_in_libdirs(
            compat.base_prefix,
            os.path.join(compat.base_prefix, 'lib'),
        )
        if python_libname:
            return python_libname

    # Python library NOT found. Return None and let the caller deal with this.
    return None


#- Binary vs data (re)classification


def classify_binary_vs_data(filename):
    """
    Classify the given file as either BINARY or a DATA, using appropriate platform-specific method. Returns 'BINARY'
    or 'DATA' string depending on the determined file type, or None if classification cannot be performed (non-existing
    file, missing tool, and other errors during classification).
    """

    # We cannot classify non-existent files.
    if not os.path.isfile(filename):
        return None

    # Use platform-specific implementation.
    return _classify_binary_vs_data(filename)


if compat.is_linux:

    def _classify_binary_vs_data(filename):
        # First check for ELF signature, in order to avoid calling `objdump` on every data file, which can be costly.
        try:
            with open(filename, 'rb') as fp:
                sig = fp.read(4)
        except Exception:
            return None

        if sig != b"\x7FELF":
            return "DATA"

        # Verify the binary by checking if `objdump` recognizes the file. The preceding ELF signature check should
        # ensure that this is an ELF file, while this check should ensure that it is a valid ELF file. In the future,
        # we could try checking that the architecture matches the running platform.
        cmd_args = ['objdump', '-a', filename]
        try:
            p = subprocess.run(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                encoding='utf8',
            )
        except Exception:
            return None  # Failed to run `objdump` or `objdump` unavailable.

        return 'BINARY' if p.returncode == 0 else 'DATA'

elif compat.is_win:

    def _classify_binary_vs_data(filename):
        # See if the file can be opened using `pefile`.
        import pefile

        try:
            pe = pefile.PE(filename, fast_load=True)  # noqa: F841
            return 'BINARY'
        except Exception:
            # TODO: catch only `pefile.PEFormatError`?
            pass

        return 'DATA'

elif compat.is_darwin:

    def _classify_binary_vs_data(filename):
        # See if the file can be opened using `macholib`.
        import macholib.MachO

        try:
            macho = macholib.MachO.MachO(filename)  # noqa: F841
            return 'BINARY'
        except Exception:
            # TODO: catch only `ValueError`?
            pass

        return 'DATA'

else:

    def _classify_binary_vs_data(filename):
        # Classification not implemented for the platform.
        return None
