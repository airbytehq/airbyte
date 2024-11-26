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
Automatically build spec files containing a description of the project.
"""

import argparse
import os
import re

from PyInstaller import DEFAULT_SPECPATH, HOMEPATH
from PyInstaller import log as logging
from PyInstaller.building.templates import bundleexetmplt, bundletmplt, onedirtmplt, onefiletmplt, splashtmpl
from PyInstaller.compat import expand_path, is_darwin, is_win

logger = logging.getLogger(__name__)

# This list gives valid choices for the ``--debug`` command-line option, except for the ``all`` choice.
DEBUG_ARGUMENT_CHOICES = ['imports', 'bootloader', 'noarchive']
# This is the ``all`` choice.
DEBUG_ALL_CHOICE = ['all']


def escape_win_filepath(path):
    # escape all \ with another \ after using normpath to clean up the path
    return os.path.normpath(path).replace('\\', '\\\\')


def make_path_spec_relative(filename, spec_dir):
    """
    Make the filename relative to the directory containing .spec file if filename is relative and not absolute.
    Otherwise keep filename untouched.
    """
    if os.path.isabs(filename):
        return filename
    else:
        filename = os.path.abspath(filename)
        # Make it relative.
        filename = os.path.relpath(filename, start=spec_dir)
        return filename


# Support for trying to avoid hard-coded paths in the .spec files. Eg, all files rooted in the Installer directory tree
# will be written using "HOMEPATH", thus allowing this spec file to be used with any Installer installation. Same thing
# could be done for other paths too.
path_conversions = ((HOMEPATH, "HOMEPATH"),)


class SourceDestAction(argparse.Action):
    """
    A command line option which takes multiple source:dest pairs.
    """
    def __init__(self, *args, default=None, metavar=None, **kwargs):
        super().__init__(*args, default=[], metavar='SOURCE:DEST', **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        try:
            # Find the only separator that isn't a Windows drive.
            separator, = (m for m in re.finditer(rf"(^\w:[/\\])|[:{os.pathsep}]", value) if not m[1])
        except ValueError:
            # Split into SRC and DEST failed, wrong syntax
            raise argparse.ArgumentError(self, f'Wrong syntax, should be {self.option_strings[0]}=SOURCE:DEST')
        src = value[:separator.start()]
        dest = value[separator.end():]
        if not src or not dest:
            # Syntax was correct, but one or both of SRC and DEST was not given
            raise argparse.ArgumentError(self, "You have to specify both SOURCE and DEST")

        # argparse is not particularly smart with copy by reference typed defaults. If the current list is the default,
        # replace it before modifying it to avoid changing the default.
        if getattr(namespace, self.dest) is self.default:
            setattr(namespace, self.dest, [])
        getattr(namespace, self.dest).append((src, dest))


def make_variable_path(filename, conversions=path_conversions):
    if not os.path.isabs(filename):
        # os.path.commonpath can not compare relative and absolute paths, and if filename is not absolute, none of the
        # paths in conversions will match anyway.
        return None, filename
    for (from_path, to_name) in conversions:
        assert os.path.abspath(from_path) == from_path, ("path '%s' should already be absolute" % from_path)
        try:
            common_path = os.path.commonpath([filename, from_path])
        except ValueError:
            # Per https://docs.python.org/3/library/os.path.html#os.path.commonpath, this raises ValueError in several
            # cases which prevent computing a common path.
            common_path = None
        if common_path == from_path:
            rest = filename[len(from_path):]
            if rest.startswith(('\\', '/')):
                rest = rest[1:]
            return to_name, rest
    return None, filename


def removed_key_option(x):
    from PyInstaller.exceptions import RemovedCipherFeatureError
    raise RemovedCipherFeatureError("Please remove your --key=xxx argument.")


class _RemovedFlagAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        kwargs["help"] = argparse.SUPPRESS
        kwargs["nargs"] = 0
        super().__init__(*args, **kwargs)


class _RemovedNoEmbedManifestAction(_RemovedFlagAction):
    def __call__(self, *args, **kwargs):
        from PyInstaller.exceptions import RemovedExternalManifestError
        raise RemovedExternalManifestError("Please remove your --no-embed-manifest argument.")


class _RemovedWinPrivateAssembliesAction(_RemovedFlagAction):
    def __call__(self, *args, **kwargs):
        from PyInstaller.exceptions import RemovedWinSideBySideSupportError
        raise RemovedWinSideBySideSupportError("Please remove your --win-private-assemblies argument.")


class _RemovedWinNoPreferRedirectsAction(_RemovedFlagAction):
    def __call__(self, *args, **kwargs):
        from PyInstaller.exceptions import RemovedWinSideBySideSupportError
        raise RemovedWinSideBySideSupportError("Please remove your --win-no-prefer-redirects argument.")


# An object used in place of a "path string", which knows how to repr() itself using variable names instead of
# hard-coded paths.
class Path:
    def __init__(self, *parts):
        self.path = os.path.join(*parts)
        self.variable_prefix = self.filename_suffix = None

    def __repr__(self):
        if self.filename_suffix is None:
            self.variable_prefix, self.filename_suffix = make_variable_path(self.path)
        if self.variable_prefix is None:
            return repr(self.path)
        return "os.path.join(" + self.variable_prefix + "," + repr(self.filename_suffix) + ")"


# An object used to construct extra preamble for the spec file, in order to accommodate extra collect_*() calls from the
# command-line
class Preamble:
    def __init__(
        self, datas, binaries, hiddenimports, collect_data, collect_binaries, collect_submodules, collect_all,
        copy_metadata, recursive_copy_metadata
    ):
        # Initialize with literal values - will be switched to preamble variable name later, if necessary
        self.binaries = binaries or []
        self.hiddenimports = hiddenimports or []
        self.datas = datas or []
        # Preamble content
        self.content = []

        # Import statements
        if collect_data:
            self._add_hookutil_import('collect_data_files')
        if collect_binaries:
            self._add_hookutil_import('collect_dynamic_libs')
        if collect_submodules:
            self._add_hookutil_import('collect_submodules')
        if collect_all:
            self._add_hookutil_import('collect_all')
        if copy_metadata or recursive_copy_metadata:
            self._add_hookutil_import('copy_metadata')
        if self.content:
            self.content += ['']  # empty line to separate the section
        # Variables
        if collect_data or copy_metadata or collect_all or recursive_copy_metadata:
            self._add_var('datas', self.datas)
            self.datas = 'datas'  # switch to variable
        if collect_binaries or collect_all:
            self._add_var('binaries', self.binaries)
            self.binaries = 'binaries'  # switch to variable
        if collect_submodules or collect_all:
            self._add_var('hiddenimports', self.hiddenimports)
            self.hiddenimports = 'hiddenimports'  # switch to variable
        # Content - collect_data_files
        for entry in collect_data:
            self._add_collect_data(entry)
        # Content - copy_metadata
        for entry in copy_metadata:
            self._add_copy_metadata(entry)
        # Content - copy_metadata(..., recursive=True)
        for entry in recursive_copy_metadata:
            self._add_recursive_copy_metadata(entry)
        # Content - collect_binaries
        for entry in collect_binaries:
            self._add_collect_binaries(entry)
        # Content - collect_submodules
        for entry in collect_submodules:
            self._add_collect_submodules(entry)
        # Content - collect_all
        for entry in collect_all:
            self._add_collect_all(entry)
        # Merge
        if self.content and self.content[-1] != '':
            self.content += ['']  # empty line
        self.content = '\n'.join(self.content)

    def _add_hookutil_import(self, name):
        self.content += ['from PyInstaller.utils.hooks import {0}'.format(name)]

    def _add_var(self, name, initial_value):
        self.content += ['{0} = {1}'.format(name, initial_value)]

    def _add_collect_data(self, name):
        self.content += ['datas += collect_data_files(\'{0}\')'.format(name)]

    def _add_copy_metadata(self, name):
        self.content += ['datas += copy_metadata(\'{0}\')'.format(name)]

    def _add_recursive_copy_metadata(self, name):
        self.content += ['datas += copy_metadata(\'{0}\', recursive=True)'.format(name)]

    def _add_collect_binaries(self, name):
        self.content += ['binaries += collect_dynamic_libs(\'{0}\')'.format(name)]

    def _add_collect_submodules(self, name):
        self.content += ['hiddenimports += collect_submodules(\'{0}\')'.format(name)]

    def _add_collect_all(self, name):
        self.content += [
            'tmp_ret = collect_all(\'{0}\')'.format(name),
            'datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]'
        ]


def __add_options(parser):
    """
    Add the `Makespec` options to a option-parser instance or a option group.
    """
    g = parser.add_argument_group('What to generate')
    g.add_argument(
        "-D",
        "--onedir",
        dest="onefile",
        action="store_false",
        default=None,
        help="Create a one-folder bundle containing an executable (default)",
    )
    g.add_argument(
        "-F",
        "--onefile",
        dest="onefile",
        action="store_true",
        default=None,
        help="Create a one-file bundled executable.",
    )
    g.add_argument(
        "--specpath",
        metavar="DIR",
        help="Folder to store the generated spec file (default: current directory)",
    )
    g.add_argument(
        "-n",
        "--name",
        help="Name to assign to the bundled app and spec file (default: first script's basename)",
    )
    g.add_argument(
        "--contents-directory",
        help="For onedir builds only, specify the name of the directory in which all supporting files (i.e. everything "
        "except the executable itself) will be placed in. Use \".\" to re-enable old onedir layout without contents "
        "directory.",
    )

    g = parser.add_argument_group('What to bundle, where to search')
    g.add_argument(
        '--add-data',
        action=SourceDestAction,
        dest='datas',
        help="Additional data files or directories containing data files to be added to the application. The argument "
        'value should be in form of "source:dest_dir", where source is the path to file (or directory) to be '
        "collected, dest_dir is the destination directory relative to the top-level application directory, and both "
        "paths are separated by a colon (:). To put a file in the top-level application directory, use . as a "
        "dest_dir. This option can be used multiple times."
    )
    g.add_argument(
        '--add-binary',
        action=SourceDestAction,
        dest="binaries",
        help='Additional binary files to be added to the executable. See the ``--add-data`` option for the format. '
        'This option can be used multiple times.',
    )
    g.add_argument(
        "-p",
        "--paths",
        dest="pathex",
        metavar="DIR",
        action="append",
        default=[],
        help="A path to search for imports (like using PYTHONPATH). Multiple paths are allowed, separated by ``%s``, "
        "or use this option multiple times. Equivalent to supplying the ``pathex`` argument in the spec file." %
        repr(os.pathsep),
    )
    g.add_argument(
        '--hidden-import',
        '--hiddenimport',
        action='append',
        default=[],
        metavar="MODULENAME",
        dest='hiddenimports',
        help='Name an import not visible in the code of the script(s). This option can be used multiple times.',
    )
    g.add_argument(
        '--collect-submodules',
        action="append",
        default=[],
        metavar="MODULENAME",
        dest='collect_submodules',
        help='Collect all submodules from the specified package or module. This option can be used multiple times.',
    )
    g.add_argument(
        '--collect-data',
        '--collect-datas',
        action="append",
        default=[],
        metavar="MODULENAME",
        dest='collect_data',
        help='Collect all data from the specified package or module. This option can be used multiple times.',
    )
    g.add_argument(
        '--collect-binaries',
        action="append",
        default=[],
        metavar="MODULENAME",
        dest='collect_binaries',
        help='Collect all binaries from the specified package or module. This option can be used multiple times.',
    )
    g.add_argument(
        '--collect-all',
        action="append",
        default=[],
        metavar="MODULENAME",
        dest='collect_all',
        help='Collect all submodules, data files, and binaries from the specified package or module. This option can '
        'be used multiple times.',
    )
    g.add_argument(
        '--copy-metadata',
        action="append",
        default=[],
        metavar="PACKAGENAME",
        dest='copy_metadata',
        help='Copy metadata for the specified package. This option can be used multiple times.',
    )
    g.add_argument(
        '--recursive-copy-metadata',
        action="append",
        default=[],
        metavar="PACKAGENAME",
        dest='recursive_copy_metadata',
        help='Copy metadata for the specified package and all its dependencies. This option can be used multiple '
        'times.',
    )
    g.add_argument(
        "--additional-hooks-dir",
        action="append",
        dest="hookspath",
        default=[],
        help="An additional path to search for hooks. This option can be used multiple times.",
    )
    g.add_argument(
        '--runtime-hook',
        action='append',
        dest='runtime_hooks',
        default=[],
        help='Path to a custom runtime hook file. A runtime hook is code that is bundled with the executable and is '
        'executed before any other code or module to set up special features of the runtime environment. This option '
        'can be used multiple times.',
    )
    g.add_argument(
        '--exclude-module',
        dest='excludes',
        action='append',
        default=[],
        help='Optional module or package (the Python name, not the path name) that will be ignored (as though it was '
        'not found). This option can be used multiple times.',
    )
    g.add_argument(
        '--key',
        dest='key',
        help=argparse.SUPPRESS,
        type=removed_key_option,
    )
    g.add_argument(
        '--splash',
        dest='splash',
        metavar="IMAGE_FILE",
        help="(EXPERIMENTAL) Add an splash screen with the image IMAGE_FILE to the application. The splash screen can "
        "display progress updates while unpacking.",
    )

    g = parser.add_argument_group('How to generate')
    g.add_argument(
        "-d",
        "--debug",
        # If this option is not specified, then its default value is an empty list (no debug options selected).
        default=[],
        # Note that ``nargs`` is omitted. This produces a single item not stored in a list, as opposed to a list
        # containing one item, as per `nargs <https://docs.python.org/3/library/argparse.html#nargs>`_.
        nargs=None,
        # The options specified must come from this list.
        choices=DEBUG_ALL_CHOICE + DEBUG_ARGUMENT_CHOICES,
        # Append choice, rather than storing them (which would overwrite any previous selections).
        action='append',
        # Allow newlines in the help text; see the ``_SmartFormatter`` in ``__main__.py``.
        help=(
            "R|Provide assistance with debugging a frozen\n"
            "application. This argument may be provided multiple\n"
            "times to select several of the following options.\n"
            "\n"
            "- all: All three of the following options.\n"
            "\n"
            "- imports: specify the -v option to the underlying\n"
            "  Python interpreter, causing it to print a message\n"
            "  each time a module is initialized, showing the\n"
            "  place (filename or built-in module) from which it\n"
            "  is loaded. See\n"
            "  https://docs.python.org/3/using/cmdline.html#id4.\n"
            "\n"
            "- bootloader: tell the bootloader to issue progress\n"
            "  messages while initializing and starting the\n"
            "  bundled app. Used to diagnose problems with\n"
            "  missing imports.\n"
            "\n"
            "- noarchive: instead of storing all frozen Python\n"
            "  source files as an archive inside the resulting\n"
            "  executable, store them as files in the resulting\n"
            "  output directory.\n"
            "\n"
        ),
    )
    g.add_argument(
        '--python-option',
        dest='python_options',
        metavar='PYTHON_OPTION',
        action='append',
        default=[],
        help='Specify a command-line option to pass to the Python interpreter at runtime. Currently supports '
        '"v" (equivalent to "--debug imports"), "u", "W <warning control>", "X <xoption>", and "hash_seed=<value>". '
        'For details, see the section "Specifying Python Interpreter Options" in PyInstaller manual.',
    )
    g.add_argument(
        "-s",
        "--strip",
        action="store_true",
        help="Apply a symbol-table strip to the executable and shared libs (not recommended for Windows)",
    )
    g.add_argument(
        "--noupx",
        action="store_true",
        default=False,
        help="Do not use UPX even if it is available (works differently between Windows and *nix)",
    )
    g.add_argument(
        "--upx-exclude",
        dest="upx_exclude",
        metavar="FILE",
        action="append",
        help="Prevent a binary from being compressed when using upx. This is typically used if upx corrupts certain "
        "binaries during compression. FILE is the filename of the binary without path. This option can be used "
        "multiple times.",
    )

    g = parser.add_argument_group('Windows and Mac OS X specific options')
    g.add_argument(
        "-c",
        "--console",
        "--nowindowed",
        dest="console",
        action="store_true",
        default=None,
        help="Open a console window for standard i/o (default). On Windows this option has no effect if the first "
        "script is a '.pyw' file.",
    )
    g.add_argument(
        "-w",
        "--windowed",
        "--noconsole",
        dest="console",
        action="store_false",
        default=None,
        help="Windows and Mac OS X: do not provide a console window for standard i/o. On Mac OS this also triggers "
        "building a Mac OS .app bundle. On Windows this option is automatically set if the first script is a '.pyw' "
        "file. This option is ignored on *NIX systems.",
    )
    g.add_argument(
        "--hide-console",
        type=str,
        choices={'hide-early', 'hide-late', 'minimize-early', 'minimize-late'},
        default=None,
        help="Windows only: in console-enabled executable, have bootloader automatically hide or minimize the console "
        "window if the program owns the console window (i.e., was not launched from an existing console window).",
    )
    g.add_argument(
        "-i",
        "--icon",
        action='append',
        dest="icon_file",
        metavar='<FILE.ico or FILE.exe,ID or FILE.icns or Image or "NONE">',
        help="FILE.ico: apply the icon to a Windows executable. FILE.exe,ID: extract the icon with ID from an exe. "
        "FILE.icns: apply the icon to the .app bundle on Mac OS. If an image file is entered that isn't in the "
        "platform format (ico on Windows, icns on Mac), PyInstaller tries to use Pillow to translate the icon into "
        "the correct format (if Pillow is installed). Use \"NONE\" to not apply any icon, thereby making the OS show "
        "some default (default: apply PyInstaller's icon). This option can be used multiple times.",
    )
    g.add_argument(
        "--disable-windowed-traceback",
        dest="disable_windowed_traceback",
        action="store_true",
        default=False,
        help="Disable traceback dump of unhandled exception in windowed (noconsole) mode (Windows and macOS only), "
        "and instead display a message that this feature is disabled.",
    )

    g = parser.add_argument_group('Windows specific options')
    g.add_argument(
        "--version-file",
        dest="version_file",
        metavar="FILE",
        help="Add a version resource from FILE to the exe.",
    )
    g.add_argument(
        "-m",
        "--manifest",
        metavar="<FILE or XML>",
        help="Add manifest FILE or XML to the exe.",
    )
    g.add_argument(
        "--no-embed-manifest",
        action=_RemovedNoEmbedManifestAction,
    )
    g.add_argument(
        "-r",
        "--resource",
        dest="resources",
        metavar="RESOURCE",
        action="append",
        default=[],
        help="Add or update a resource to a Windows executable. The RESOURCE is one to four items, "
        "FILE[,TYPE[,NAME[,LANGUAGE]]]. FILE can be a data file or an exe/dll. For data files, at least TYPE and NAME "
        "must be specified. LANGUAGE defaults to 0 or may be specified as wildcard * to update all resources of the "
        "given TYPE and NAME. For exe/dll files, all resources from FILE will be added/updated to the final executable "
        "if TYPE, NAME and LANGUAGE are omitted or specified as wildcard *. This option can be used multiple times.",
    )
    g.add_argument(
        '--uac-admin',
        dest='uac_admin',
        action="store_true",
        default=False,
        help="Using this option creates a Manifest that will request elevation upon application start.",
    )
    g.add_argument(
        '--uac-uiaccess',
        dest='uac_uiaccess',
        action="store_true",
        default=False,
        help="Using this option allows an elevated application to work with Remote Desktop.",
    )

    g = parser.add_argument_group('Windows Side-by-side Assembly searching options (advanced)')
    g.add_argument(
        "--win-private-assemblies",
        action=_RemovedWinPrivateAssembliesAction,
    )
    g.add_argument(
        "--win-no-prefer-redirects",
        action=_RemovedWinNoPreferRedirectsAction,
    )

    g = parser.add_argument_group('Mac OS specific options')
    g.add_argument(
        "--argv-emulation",
        dest="argv_emulation",
        action="store_true",
        default=False,
        help="Enable argv emulation for macOS app bundles. If enabled, the initial open document/URL event is "
        "processed by the bootloader and the passed file paths or URLs are appended to sys.argv.",
    )

    g.add_argument(
        '--osx-bundle-identifier',
        dest='bundle_identifier',
        help="Mac OS .app bundle identifier is used as the default unique program name for code signing purposes. "
        "The usual form is a hierarchical name in reverse DNS notation. For example: com.mycompany.department.appname "
        "(default: first script's basename)",
    )

    g.add_argument(
        '--target-architecture',
        '--target-arch',
        dest='target_arch',
        metavar='ARCH',
        default=None,
        help="Target architecture (macOS only; valid values: x86_64, arm64, universal2). Enables switching between "
        "universal2 and single-arch version of frozen application (provided python installation supports the target "
        "architecture). If not target architecture is not specified, the current running architecture is targeted.",
    )

    g.add_argument(
        '--codesign-identity',
        dest='codesign_identity',
        metavar='IDENTITY',
        default=None,
        help="Code signing identity (macOS only). Use the provided identity to sign collected binaries and generated "
        "executable. If signing identity is not provided, ad-hoc signing is performed instead.",
    )

    g.add_argument(
        '--osx-entitlements-file',
        dest='entitlements_file',
        metavar='FILENAME',
        default=None,
        help="Entitlements file to use when code-signing the collected binaries (macOS only).",
    )

    g = parser.add_argument_group('Rarely used special options')
    g.add_argument(
        "--runtime-tmpdir",
        dest="runtime_tmpdir",
        metavar="PATH",
        help="Where to extract libraries and support files in `onefile`-mode. If this option is given, the bootloader "
        "will ignore any temp-folder location defined by the run-time OS. The ``_MEIxxxxxx``-folder will be created "
        "here. Please use this option only if you know what you are doing.",
    )
    g.add_argument(
        "--bootloader-ignore-signals",
        action="store_true",
        default=False,
        help="Tell the bootloader to ignore signals rather than forwarding them to the child process. Useful in "
        "situations where for example a supervisor process signals both the bootloader and the child (e.g., via a "
        "process group) to avoid signalling the child twice.",
    )


def main(
    scripts,
    name=None,
    onefile=False,
    console=True,
    debug=[],
    python_options=[],
    strip=False,
    noupx=False,
    upx_exclude=None,
    runtime_tmpdir=None,
    contents_directory=None,
    pathex=[],
    version_file=None,
    specpath=None,
    bootloader_ignore_signals=False,
    disable_windowed_traceback=False,
    datas=[],
    binaries=[],
    icon_file=None,
    manifest=None,
    resources=[],
    bundle_identifier=None,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    uac_admin=False,
    uac_uiaccess=False,
    collect_submodules=[],
    collect_binaries=[],
    collect_data=[],
    collect_all=[],
    copy_metadata=[],
    splash=None,
    recursive_copy_metadata=[],
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    argv_emulation=False,
    hide_console=None,
    **_kwargs
):
    # Default values for onefile and console when not explicitly specified on command-line (indicated by None)
    if onefile is None:
        onefile = False

    if console is None:
        console = True

    # If appname is not specified - use the basename of the main script as name.
    if name is None:
        name = os.path.splitext(os.path.basename(scripts[0]))[0]

    # If specpath not specified - use default value - current working directory.
    if specpath is None:
        specpath = DEFAULT_SPECPATH
    else:
        # Expand tilde to user's home directory.
        specpath = expand_path(specpath)
    # If cwd is the root directory of PyInstaller, generate the .spec file in ./appname/ subdirectory.
    if specpath == HOMEPATH:
        specpath = os.path.join(HOMEPATH, name)
    # Create directory tree if missing.
    if not os.path.exists(specpath):
        os.makedirs(specpath)

    # Handle additional EXE options.
    exe_options = ''
    if version_file:
        exe_options += "\n    version='%s'," % escape_win_filepath(version_file)
    if uac_admin:
        exe_options += "\n    uac_admin=True,"
    if uac_uiaccess:
        exe_options += "\n    uac_uiaccess=True,"
    if icon_file:
        # Icon file for Windows.
        # On Windows, the default icon is embedded in the bootloader executable.
        if icon_file[0] == 'NONE':
            exe_options += "\n    icon='NONE',"
        else:
            exe_options += "\n    icon=[%s]," % ','.join("'%s'" % escape_win_filepath(ic) for ic in icon_file)
        # Icon file for Mac OS.
        # We need to encapsulate it into apostrofes.
        icon_file = "'%s'" % icon_file[0]
    else:
        # On Mac OS, the default icon has to be copied into the .app bundle.
        # The the text value 'None' means - use default icon.
        icon_file = 'None'
    if contents_directory:
        exe_options += "\n    contents_directory='%s'," % (contents_directory or "_internal")
    if hide_console:
        exe_options += "\n    hide_console='%s'," % hide_console

    if bundle_identifier:
        # We need to encapsulate it into apostrofes.
        bundle_identifier = "'%s'" % bundle_identifier

    if manifest:
        if "<" in manifest:
            # Assume XML string
            exe_options += "\n    manifest='%s'," % manifest.replace("'", "\\'")
        else:
            # Assume filename
            exe_options += "\n    manifest='%s'," % escape_win_filepath(manifest)
    if resources:
        resources = list(map(escape_win_filepath, resources))
        exe_options += "\n    resources=%s," % repr(resources)

    hiddenimports = hiddenimports or []
    upx_exclude = upx_exclude or []

    # If file extension of the first script is '.pyw', force --windowed option.
    if is_win and os.path.splitext(scripts[0])[-1] == '.pyw':
        console = False

    # If script paths are relative, make them relative to the directory containing .spec file.
    scripts = [make_path_spec_relative(x, specpath) for x in scripts]
    # With absolute paths replace prefix with variable HOMEPATH.
    scripts = list(map(Path, scripts))

    # Translate the default of ``debug=None`` to an empty list.
    if debug is None:
        debug = []
    # Translate the ``all`` option.
    if DEBUG_ALL_CHOICE[0] in debug:
        debug = DEBUG_ARGUMENT_CHOICES

    # Create preamble (for collect_*() calls)
    preamble = Preamble(
        datas, binaries, hiddenimports, collect_data, collect_binaries, collect_submodules, collect_all, copy_metadata,
        recursive_copy_metadata
    )

    if splash:
        splash_init = splashtmpl % {'splash_image': splash}
        splash_binaries = "\n    splash.binaries,"
        splash_target = "\n    splash,"
    else:
        splash_init = splash_binaries = splash_target = ""

    # Create OPTIONs array
    if 'imports' in debug and 'v' not in python_options:
        python_options.append('v')
    python_options_array = [(opt, None, 'OPTION') for opt in python_options]

    d = {
        'scripts': scripts,
        'pathex': pathex or [],
        'binaries': preamble.binaries,
        'datas': preamble.datas,
        'hiddenimports': preamble.hiddenimports,
        'preamble': preamble.content,
        'name': name,
        'noarchive': 'noarchive' in debug,
        'options': python_options_array,
        'debug_bootloader': 'bootloader' in debug,
        'bootloader_ignore_signals': bootloader_ignore_signals,
        'strip': strip,
        'upx': not noupx,
        'upx_exclude': upx_exclude,
        'runtime_tmpdir': runtime_tmpdir,
        'exe_options': exe_options,
        # Directory with additional custom import hooks.
        'hookspath': hookspath,
        # List with custom runtime hook files.
        'runtime_hooks': runtime_hooks or [],
        # List of modules/packages to ignore.
        'excludes': excludes or [],
        # only Windows and Mac OS distinguish windowed and console apps
        'console': console,
        'disable_windowed_traceback': disable_windowed_traceback,
        # Icon filename. Only Mac OS uses this item.
        'icon': icon_file,
        # .app bundle identifier. Only OSX uses this item.
        'bundle_identifier': bundle_identifier,
        # argv emulation (macOS only)
        'argv_emulation': argv_emulation,
        # Target architecture (macOS only)
        'target_arch': target_arch,
        # Code signing identity (macOS only)
        'codesign_identity': codesign_identity,
        # Entitlements file (macOS only)
        'entitlements_file': entitlements_file,
        # splash screen
        'splash_init': splash_init,
        'splash_target': splash_target,
        'splash_binaries': splash_binaries,
    }

    # Write down .spec file to filesystem.
    specfnm = os.path.join(specpath, name + '.spec')
    with open(specfnm, 'w', encoding='utf-8') as specfile:
        if onefile:
            specfile.write(onefiletmplt % d)
            # For Mac OS create .app bundle.
            if is_darwin and not console:
                specfile.write(bundleexetmplt % d)
        else:
            specfile.write(onedirtmplt % d)
            # For Mac OS create .app bundle.
            if is_darwin and not console:
                specfile.write(bundletmplt % d)

    return specfnm
