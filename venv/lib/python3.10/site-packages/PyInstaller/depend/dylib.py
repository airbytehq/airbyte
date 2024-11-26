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
Manipulating with dynamic libraries.
"""

import os.path

from PyInstaller.utils.win32 import winutils

__all__ = ['exclude_list', 'include_list', 'include_library']

import os
import re

import PyInstaller.log as logging
from PyInstaller import compat

logger = logging.getLogger(__name__)

# Ignoring some system libraries speeds up packaging process
_excludes = {
    # Ignore annoying warnings with Windows system DLLs.
    #
    # 'W: library kernel32.dll required via ctypes not found'
    # 'W: library coredll.dll required via ctypes not found'
    #
    # These these dlls has to be ignored for all operating systems because they might be resolved when scanning code for
    # ctypes dependencies.
    r'advapi32\.dll',
    r'ws2_32\.dll',
    r'gdi32\.dll',
    r'oleaut32\.dll',
    r'shell32\.dll',
    r'ole32\.dll',
    r'coredll\.dll',
    r'crypt32\.dll',
    r'kernel32',
    r'kernel32\.dll',
    r'msvcrt\.dll',
    r'rpcrt4\.dll',
    r'user32\.dll',
    # Some modules tries to import the Python library. e.g. pyreadline.console.console
    r'python\%s\%s',
}

# Regex includes - overrides excludes. Include list is used only to override specific libraries from exclude list.
_includes = set()

_win_includes = {
    # We need to allow collection of Visual Studio C++ (VC) runtime DLLs from system directories in order to avoid
    # missing DLL errors when the frozen application is run on a system that does not have the corresponding VC
    # runtime installed. The VC runtime DLLs may be dependencies of python shared library itself or of extension
    # modules provided by 3rd party packages.

    # Visual Studio 2010 (VC10) runtime
    # http://msdn.microsoft.com/en-us/library/8kche8ah(v=vs.100).aspx
    r'atl100\.dll',
    r'msvcr100\.dll',
    r'msvcp100\.dll',
    r'mfc100\.dll',
    r'mfc100u\.dll',
    r'mfcmifc80\.dll',
    r'mfcm100\.dll',
    r'mfcm100u\.dll',

    # Visual Studio 2012 (VC11) runtime
    # https://docs.microsoft.com/en-us/visualstudio/releases/2013/2012-redistribution-vs
    #
    # VC110.ATL
    r'atl110\.dll',
    # VC110.CRT
    r'msvcp110\.dll',
    r'msvcr110\.dll',
    r'vccorlib110\.dll',
    # VC110.CXXAMP
    r'vcamp110\.dll',
    # VC110.MFC
    r'mfc110\.dll',
    r'mfc110u\.dll',
    r'mfcm110\.dll',
    r'mfcm110u\.dll',
    # VC110.MFCLOC
    r'mfc110chs\.dll',
    r'mfc110cht\.dll',
    r'mfc110enu\.dll',
    r'mfc110esn\.dll',
    r'mfc110deu\.dll',
    r'mfc110fra\.dll',
    r'mfc110ita\.dll',
    r'mfc110jpn\.dll',
    r'mfc110kor\.dll',
    r'mfc110rus\.dll',
    # VC110.OpenMP
    r'vcomp110\.dll',
    # DIA SDK
    r'msdia110\.dll',

    # Visual Studio 2013 (VC12) runtime
    # https://docs.microsoft.com/en-us/visualstudio/releases/2013/2013-redistribution-vs
    #
    # VC120.CRT
    r'msvcp120\.dll',
    r'msvcr120\.dll',
    r'vccorlib120\.dll',
    # VC120.CXXAMP
    r'vcamp120\.dll',
    # VC120.MFC
    r'mfc120\.dll',
    r'mfc120u\.dll',
    r'mfcm120\.dll',
    r'mfcm120u\.dll',
    # VC120.MFCLOC
    r'mfc120chs\.dll',
    r'mfc120cht\.dll',
    r'mfc120deu\.dll',
    r'mfc120enu\.dll',
    r'mfc120esn\.dll',
    r'mfc120fra\.dll',
    r'mfc120ita\.dll',
    r'mfc120jpn\.dll',
    r'mfc120kor\.dll',
    r'mfc120rus\.dll',
    # VC120.OPENMP
    r'vcomp120\.dll',
    # DIA SDK
    r'msdia120\.dll',
    # Cpp REST Windows SDK
    r'casablanca120.winrt\.dll',
    # Mobile Services Cpp Client
    r'zumosdk120.winrt\.dll',
    # Cpp REST SDK
    r'casablanca120\.dll',

    # Universal C Runtime Library (since Visual Studio 2015)
    #
    # NOTE: these should be put under a switch, as they need not to be bundled if deployment target is Windows 10
    # and later, as "UCRT is now a system component in Windows 10 and later, managed by Windows Update".
    # (https://docs.microsoft.com/en-us/cpp/windows/determining-which-dlls-to-redistribute?view=msvc-170)
    # And as discovered in #6326, Windows prefers system-installed version over the bundled one, anyway
    # (see https://docs.microsoft.com/en-us/cpp/windows/universal-crt-deployment?view=msvc-170#local-deployment).
    r'api-ms-win-core.*',
    r'api-ms-win-crt.*',
    r'ucrtbase\.dll',

    # Visual Studio 2015/2017/2019/2022 (VC14) runtime
    # https://docs.microsoft.com/en-us/visualstudio/releases/2022/redistribution
    #
    # VC141.CRT/VC142.CRT/VC143.CRT
    r'concrt140\.dll',
    r'msvcp140\.dll',
    r'msvcp140_1\.dll',
    r'msvcp140_2\.dll',
    r'msvcp140_atomic_wait\.dll',
    r'msvcp140_codecvt_ids\.dll',
    r'vccorlib140\.dll',
    r'vcruntime140\.dll',
    r'vcruntime140_1\.dll',
    # VC141.CXXAMP/VC142.CXXAMP/VC143.CXXAMP
    r'vcamp140\.dll',
    # VC141.OpenMP/VC142.OpenMP/VC143.OpenMP
    r'vcomp140\.dll',
    # DIA SDK
    r'msdia140\.dll',

    # Allow pythonNN.dll, pythoncomNN.dll, pywintypesNN.dll
    r'py(?:thon(?:com(?:loader)?)?|wintypes)\d+\.dll',
}

_win_excludes = {
    # On Windows, only .dll files can be loaded.
    r'.*\.so',
    r'.*\.dylib',

    # MS assembly excludes
    r'Microsoft\.Windows\.Common-Controls',
}

_unix_excludes = {
    r'libc\.so(\..*)?',
    r'libdl\.so(\..*)?',
    r'libm\.so(\..*)?',
    r'libpthread\.so(\..*)?',
    r'librt\.so(\..*)?',
    r'libthread_db\.so(\..*)?',
    # glibc regex excludes.
    r'ld-linux\.so(\..*)?',
    r'libBrokenLocale\.so(\..*)?',
    r'libanl\.so(\..*)?',
    r'libcidn\.so(\..*)?',
    r'libcrypt\.so(\..*)?',
    r'libnsl\.so(\..*)?',
    r'libnss_compat.*\.so(\..*)?',
    r'libnss_dns.*\.so(\..*)?',
    r'libnss_files.*\.so(\..*)?',
    r'libnss_hesiod.*\.so(\..*)?',
    r'libnss_nis.*\.so(\..*)?',
    r'libnss_nisplus.*\.so(\..*)?',
    r'libresolv\.so(\..*)?',
    r'libutil\.so(\..*)?',
    # graphical interface libraries come with graphical stack (see libglvnd)
    r'libE?(Open)?GLX?(ESv1_CM|ESv2)?(dispatch)?\.so(\..*)?',
    r'libdrm\.so(\..*)?',
    # a subset of libraries included as part of the Nvidia Linux Graphics Driver as of 520.56.06:
    # https://download.nvidia.com/XFree86/Linux-x86_64/520.56.06/README/installedcomponents.html
    r'nvidia_drv\.so',
    r'libglxserver_nvidia\.so(\..*)?',
    r'libnvidia-egl-(gbm|wayland)\.so(\..*)?',
    r'libnvidia-(cfg|compiler|e?glcore|glsi|glvkspirv|rtcore|allocator|tls|ml)\.so(\..*)?',
    r'lib(EGL|GLX)_nvidia\.so(\..*)?',
    # libxcb-dri changes ABI frequently (e.g.: between Ubuntu LTS releases) and is usually installed as dependency of
    # the graphics stack anyway. No need to bundle it.
    r'libxcb\.so(\..*)?',
    r'libxcb-dri.*\.so(\..*)?',
}

_aix_excludes = {
    r'libbz2\.a',
    r'libc\.a',
    r'libC\.a',
    r'libcrypt\.a',
    r'libdl\.a',
    r'libintl\.a',
    r'libpthreads\.a',
    r'librt\\.a',
    r'librtl\.a',
    r'libz\.a',
}

if compat.is_win:
    _includes |= _win_includes
    _excludes |= _win_excludes
elif compat.is_aix:
    # The exclude list for AIX differs from other *nix platforms.
    _excludes |= _aix_excludes
elif compat.is_unix:
    # Common excludes for *nix platforms -- except AIX.
    _excludes |= _unix_excludes


class ExcludeList:
    def __init__(self):
        self.regex = re.compile('|'.join(_excludes), re.I)

    def search(self, libname):
        # Running re.search() on '' regex never returns None.
        if _excludes:
            return self.regex.match(os.path.basename(libname))
        else:
            return False


class IncludeList:
    def __init__(self):
        self.regex = re.compile('|'.join(_includes), re.I)

    def search(self, libname):
        # Running re.search() on '' regex never returns None.
        if _includes:
            return self.regex.match(os.path.basename(libname))
        else:
            return False


exclude_list = ExcludeList()
include_list = IncludeList()

if compat.is_darwin:
    # On Mac use macholib to decide if a binary is a system one.
    from macholib import util

    class MacExcludeList:
        def __init__(self, global_exclude_list):
            # Wraps the global 'exclude_list' before it is overridden by this class.
            self._exclude_list = global_exclude_list

        def search(self, libname):
            # First try global exclude list. If it matches, return its result; otherwise continue with other check.
            result = self._exclude_list.search(libname)
            if result:
                return result
            else:
                return util.in_system_path(libname)

    exclude_list = MacExcludeList(exclude_list)

elif compat.is_win:

    class WinExcludeList:
        def __init__(self, global_exclude_list):
            self._exclude_list = global_exclude_list
            # use normpath because msys2 uses / instead of \
            self._windows_dir = os.path.normpath(winutils.get_windows_dir().lower())

        def search(self, libname):
            libname = libname.lower()
            result = self._exclude_list.search(libname)
            if result:
                return result
            else:
                # Exclude everything from the Windows directory by default.
                # .. sometimes realpath changes the case of libname, lower it
                # .. use normpath because msys2 uses / instead of \
                fn = os.path.normpath(os.path.realpath(libname).lower())
                return fn.startswith(self._windows_dir)

    exclude_list = WinExcludeList(exclude_list)

_seen_wine_dlls = set()  # Used for warning tracking in include_library()


def include_library(libname):
    """
    Check if the dynamic library should be included with application or not.
    """
    if exclude_list:
        if exclude_list.search(libname) and not include_list.search(libname):
            # Library is excluded and is not overridden by include list. It should be excluded.
            return False

    # If we are running under Wine and the library is a Wine built-in DLL, ensure that it is always excluded. Typically,
    # excluding a DLL leads to an incomplete bundle and run-time errors when the said DLL is not installed on the target
    # system. However, having Wine built-in DLLs collected is even more detrimental, as they usually provide Wine's
    # implementation of low-level functionality, and therefore cannot be used on actual Windows (i.e., system libraries
    # from the C:\Windows\system32 directory that might end up collected due to ``_win_includes`` list; a prominent
    # example are VC runtime DLLs, for which Wine provides their own implementation, unless user explicitly installs
    # Microsoft's VC redistributable package in their Wine environment). Therefore, excluding the Wine built-in DLLs
    # actually improves the chances of the bundle running on Windows, or at least makes the issue easier to debug by
    # turning it into the "standard" missing DLL problem. Exclusion should not affect the bundle's ability to run under
    #  Wine itself, as the excluded DLLs are available there.
    if compat.is_win_wine and compat.is_wine_dll(libname):
        if libname not in _seen_wine_dlls:
            logger.warning("Excluding Wine built-in DLL: %s", libname)  # displayed only if DLL would have been included
            _seen_wine_dlls.add(libname)  # display only once for each DLL
        return False

    return True


# Patterns for suppressing warnings about missing dynamically linked libraries
_warning_suppressions = []

# On some systems (e.g., openwrt), libc.so might point to ldd. Suppress warnings about it.
if compat.is_linux:
    _warning_suppressions.append(r'ldd')

# Suppress false warnings on win 10 and UCRT (see issue #1566).
if compat.is_win_10:
    _warning_suppressions.append(r'api-ms-win-.*\.dll')


class MissingLibWarningSuppressionList:
    def __init__(self):
        self.regex = re.compile('|'.join(_warning_suppressions), re.I)

    def search(self, libname):
        # Running re.search() on '' regex never returns None.
        if _warning_suppressions:
            return self.regex.match(os.path.basename(libname))
        else:
            return False


missing_lib_warning_suppression_list = MissingLibWarningSuppressionList()


def warn_missing_lib(libname):
    """
    Check if a missing-library warning should be displayed for the given library name (or full path).
    """
    return not missing_lib_warning_suppression_list.search(libname)
