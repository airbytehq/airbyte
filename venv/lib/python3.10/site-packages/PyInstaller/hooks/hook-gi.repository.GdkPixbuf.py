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

import glob
import os
import shutil
import subprocess

from PyInstaller import compat
from PyInstaller.config import CONF  # workpath
from PyInstaller.utils.hooks import get_hook_config, logger
from PyInstaller.utils.hooks.gi import GiModuleInfo, collect_glib_translations

LOADERS_PATH = os.path.join('gdk-pixbuf-2.0', '2.10.0', 'loaders')
LOADER_MODULE_DEST_PATH = "lib/gdk-pixbuf/loaders"
LOADER_CACHE_DEST_PATH = "lib/gdk-pixbuf"  # NOTE: some search & replace code depends on / being used on all platforms.


def _find_gdk_pixbuf_query_loaders_executable(libdir):
    # Distributions either package gdk-pixbuf-query-loaders in the GI libs directory (not on the path), or on the path
    # with or without a -x64 suffix, depending on the architecture.
    cmds = [
        os.path.join(libdir, 'gdk-pixbuf-2.0', 'gdk-pixbuf-query-loaders'),
        'gdk-pixbuf-query-loaders-64',
        'gdk-pixbuf-query-loaders',
    ]

    for cmd in cmds:
        cmd_fullpath = shutil.which(cmd)
        if cmd_fullpath is not None:
            return cmd_fullpath

    return None


def _collect_loaders(libdir):
    # Assume loader plugins have .so library suffix on all non-Windows platforms
    lib_ext = "*.dll" if compat.is_win else "*.so"

    # Find all loaders
    loader_libs = []
    pattern = os.path.join(libdir, LOADERS_PATH, lib_ext)
    for f in glob.glob(pattern):
        loader_libs.append(f)

    # Sometimes the loaders are stored in a different directory from the library (msys2)
    if not loader_libs:
        pattern = os.path.abspath(os.path.join(libdir, '..', 'lib', LOADERS_PATH, lib_ext))
        for f in glob.glob(pattern):
            loader_libs.append(f)

    return loader_libs


def _generate_loader_cache(gdk_pixbuf_query_loaders, libdir, loader_libs):
    # Run the "gdk-pixbuf-query-loaders" command and capture its standard output providing an updated loader
    # cache; then write this output to the loader cache bundled with this frozen application. On all platforms,
    # we also move the package structure to point to lib/gdk-pixbuf instead of lib/gdk-pixbuf-2.0/2.10.0 in
    # order to make compatible for OSX application signing.
    #
    # On Mac OS we use @executable_path to specify a path relative to the generated bundle. However, on
    # non-Windows, we need to rewrite the loader cache because it is not relocatable by default. See
    # https://bugzilla.gnome.org/show_bug.cgi?id=737523
    #
    # To make it easier to rewrite, we just always write @executable_path, since its significantly easier to
    # find/replace at runtime. :)
    #
    # To permit string munging, decode the encoded bytes output by this command (i.e., enable the
    # "universal_newlines" option).
    #
    # On Fedora, the default loaders cache is /usr/lib64, but the libdir is actually /lib64. To get around this,
    # we pass the path to the loader command, and it will create a cache with the right path.
    #
    # On Windows, the loaders lib directory is relative, starts with 'lib', and uses \\ as path separators
    # (escaped \).
    cachedata = subprocess.run([gdk_pixbuf_query_loaders, *loader_libs],
                               check=True,
                               stdout=subprocess.PIPE,
                               encoding='utf-8').stdout

    output_lines = []
    prefix = '"' + os.path.join(libdir, 'gdk-pixbuf-2.0', '2.10.0')
    plen = len(prefix)

    win_prefix = '"' + '\\\\'.join(['lib', 'gdk-pixbuf-2.0', '2.10.0'])
    win_plen = len(win_prefix)

    msys2_prefix = '"' + os.path.abspath(os.path.join(libdir, '..', 'lib', 'gdk-pixbuf-2.0', '2.10.0'))
    msys2_plen = len(msys2_prefix)

    # For each line in the updated loader cache...
    for line in cachedata.splitlines():
        if line.startswith('#'):
            continue
        if line.startswith(prefix):
            line = '"@executable_path/' + LOADER_CACHE_DEST_PATH + line[plen:]
        elif line.startswith(win_prefix):
            line = '"' + LOADER_CACHE_DEST_PATH.replace('/', '\\\\') + line[win_plen:]
        elif line.startswith(msys2_prefix):
            line = ('"' + LOADER_CACHE_DEST_PATH + line[msys2_plen:]).replace('/', '\\\\')
        output_lines.append(line)

    return '\n'.join(output_lines)


def hook(hook_api):
    module_info = GiModuleInfo('GdkPixbuf', '2.0')
    if not module_info.available:
        return

    binaries, datas, hiddenimports = module_info.collect_typelib_data()

    libdir = module_info.get_libdir()

    # Collect GdkPixbuf loaders and generate loader cache file
    gdk_pixbuf_query_loaders = _find_gdk_pixbuf_query_loaders_executable(libdir)
    logger.debug("gdk-pixbuf-query-loaders executable: %s", gdk_pixbuf_query_loaders)
    if not gdk_pixbuf_query_loaders:
        logger.warning("gdk-pixbuf-query-loaders executable not found in GI library directory or in PATH!")
    else:
        # Find all GdkPixbuf loader modules
        loader_libs = _collect_loaders(libdir)

        # Collect discovered loaders
        for lib in loader_libs:
            binaries.append((lib, LOADER_MODULE_DEST_PATH))

        # Generate loader cache; we need to store it to CONF['workpath'] so we can collect it as a data file.
        cachedata = _generate_loader_cache(gdk_pixbuf_query_loaders, libdir, loader_libs)
        cachefile = os.path.join(CONF['workpath'], 'loaders.cache')
        with open(cachefile, 'w', encoding='utf-8') as fp:
            fp.write(cachedata)
        datas.append((cachefile, LOADER_CACHE_DEST_PATH))

    # Collect translations
    lang_list = get_hook_config(hook_api, "gi", "languages")
    if gdk_pixbuf_query_loaders:
        datas += collect_glib_translations('gdk-pixbuf', lang_list)

    hook_api.add_datas(datas)
    hook_api.add_binaries(binaries)
    hook_api.add_imports(*hiddenimports)
