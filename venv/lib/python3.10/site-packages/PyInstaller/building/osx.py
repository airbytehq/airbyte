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

import os
import pathlib
import plistlib
import shutil
import subprocess

from PyInstaller.building.api import COLLECT, EXE
from PyInstaller.building.datastruct import Target, logger, normalize_toc
from PyInstaller.building.utils import _check_path_overlap, _rmtree, process_collected_binary
from PyInstaller.compat import is_darwin, strict_collect_mode
from PyInstaller.building.icon import normalize_icon_type
import PyInstaller.utils.misc as miscutils

if is_darwin:
    import PyInstaller.utils.osx as osxutils

# Character sequence used to replace dot (`.`) in names of directories that are created in `Contents/MacOS` or
# `Contents/Frameworks`, where only .framework bundle directories are allowed to have dot in name.
DOT_REPLACEMENT = '__dot__'


class BUNDLE(Target):
    def __init__(self, *args, **kwargs):
        from PyInstaller.config import CONF

        # BUNDLE only has a sense under Mac OS, it's a noop on other platforms
        if not is_darwin:
            return

        # Get a path to a .icns icon for the app bundle.
        self.icon = kwargs.get('icon')
        if not self.icon:
            # --icon not specified; use the default in the pyinstaller folder
            self.icon = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 'bootloader', 'images', 'icon-windowed.icns'
            )
        else:
            # User gave an --icon=path. If it is relative, make it relative to the spec file location.
            if not os.path.isabs(self.icon):
                self.icon = os.path.join(CONF['specpath'], self.icon)

        super().__init__()

        # .app bundle is created in DISTPATH.
        self.name = kwargs.get('name', None)
        base_name = os.path.basename(self.name)
        self.name = os.path.join(CONF['distpath'], base_name)

        self.appname = os.path.splitext(base_name)[0]
        self.version = kwargs.get("version", "0.0.0")
        self.toc = []
        self.strip = False
        self.upx = False
        self.console = True
        self.target_arch = None
        self.codesign_identity = None
        self.entitlements_file = None

        # .app bundle identifier for Code Signing
        self.bundle_identifier = kwargs.get('bundle_identifier')
        if not self.bundle_identifier:
            # Fallback to appname.
            self.bundle_identifier = self.appname

        self.info_plist = kwargs.get('info_plist', None)

        for arg in args:
            # Valid arguments: EXE object, COLLECT object, and TOC-like iterables
            if isinstance(arg, EXE):
                # Add EXE as an entry to the TOC, and merge its dependencies TOC
                self.toc.append((os.path.basename(arg.name), arg.name, 'EXECUTABLE'))
                self.toc.extend(arg.dependencies)
                # Inherit settings
                self.strip = arg.strip
                self.upx = arg.upx
                self.upx_exclude = arg.upx_exclude
                self.console = arg.console
                self.target_arch = arg.target_arch
                self.codesign_identity = arg.codesign_identity
                self.entitlements_file = arg.entitlements_file
            elif isinstance(arg, COLLECT):
                # Merge the TOC
                self.toc.extend(arg.toc)
                # Inherit settings
                self.strip = arg.strip_binaries
                self.upx = arg.upx_binaries
                self.upx_exclude = arg.upx_exclude
                self.console = arg.console
                self.target_arch = arg.target_arch
                self.codesign_identity = arg.codesign_identity
                self.entitlements_file = arg.entitlements_file
            elif miscutils.is_iterable(arg):
                # TOC-like iterable
                self.toc.extend(arg)
            else:
                raise TypeError(f"Invalid argument type for BUNDLE: {type(arg)!r}")

        # Infer the executable name from the first EXECUTABLE entry in the TOC; it might have come from the COLLECT
        # (as opposed to the stand-alone EXE).
        for dest_name, src_name, typecode in self.toc:
            if typecode == "EXECUTABLE":
                self.exename = src_name
                break
        else:
            raise ValueError("No EXECUTABLE entry found in the TOC!")

        # Normalize TOC
        self.toc = normalize_toc(self.toc)

        self.__postinit__()

    _GUTS = (
        # BUNDLE always builds, just want the toc to be written out
        ('toc', None),
    )

    def _check_guts(self, data, last_build):
        # BUNDLE always needs to be executed, in order to clean the output directory.
        return True

    # Helper for determining whether the given file belongs to a .framework bundle or not. If it does, it returns
    # the path to the top-level .framework bundle directory; otherwise, returns None.
    @staticmethod
    def _is_framework_file(dest_path):
        for parent in dest_path.parents:
            if parent.name.endswith('.framework'):
                return parent
        return None

    # Helper that computes relative cross-link path between link's location and target, assuming they are both
    # rooted in the `Contents` directory of a macOS .app bundle.
    @staticmethod
    def _compute_relative_crosslink(crosslink_location, crosslink_target):
        # We could take symlink_location and symlink_target as they are (relative to parent of the `Contents`
        # directory), but that would introduce an unnecessary `../Contents` part. So instead, we take both paths
        # relative to the `Contents` directory.
        return os.path.join(
            *['..' for level in pathlib.PurePath(crosslink_location).relative_to('Contents').parent.parts],
            pathlib.PurePath(crosslink_target).relative_to('Contents'),
        )

    # This method takes the original (input) TOC and processes it into final TOC, based on which the `assemble` method
    # performs its file collection. The TOC processing here represents the core of our efforts to generate an .app
    # bundle that is compatible with Apple's code-signing requirements.
    #
    # For in-depth details on the code-signing, see Apple's `Technical Note TN2206: macOS Code Signing In Depth` at
    # https://developer.apple.com/library/archive/technotes/tn2206/_index.html
    #
    # The requirements, framed from PyInstaller's perspective, can be summarized as follows:
    #
    # 1. The `Contents/MacOS` directory is expected to contain only the program executable and (binary) code (= dylibs
    #    and nested .framework bundles). Alternatively, the dylibs and .framework bundles can be also placed into
    #    `Contents/Frameworks` directory (where same rules apply as for `Contents/MacOS`, so the remainder of this
    #    text refers to the two inter-changeably, unless explicitly noted otherwise). The code in `Contents/MacOS`
    #    is expected to be signed, and the `codesign` utility will recursively sign all found code when using `--deep`
    #    option to sign the .app bundle.
    #
    # 2. All non-code files should be be placed in `Contents/Resources`, so they become sealed (data) resources;
    #    i.e., their signature data is recorded in `Contents/_CodeSignature/CodeResources`. (As a side note,
    #    it seems that signature information for data/resources in `Contents/Resources` is kept nder `file` key in
    #    the `CodeResources` file, while the information for contents in `Contents/MacOS` is kept under `file2` key).
    #
    # 3. The directories in `Contents/MacOS` may not contain dots (`.`) in their names, except for the nested
    #    .framework bundle directories. The directories in `Contents/Resources` have no such restrictions.
    #
    # 4. There may not be any content in the top level of a bundle. In other words, if a bundle has a `Contents`
    #    or a `Versions` directory at its top level, there may be no other files or directories alongside them. The
    #    sole exception is that alongside ˙Versions˙, there may be symlinks to files and directories in
    #    `Versions/Current`. This rule is important for nested .framework bundles that we collect from python packages.
    #
    # Next, let us consider the consequences of violating each of the above requirements:
    #
    # 1. Code signing machinery can directly store signature only in Mach-O binaries and nested .framework bundles; if
    #    a data file is placed in `Contents/MacOS`, the signature is stored in the file's extended attributes. If the
    #    extended attributes are lost, the program's signature will be broken. Many file transfer techniques (e.g., a
    #    zip file) do not preserve extended attributes, nor are they preserved when uploading to the Mac App Store.
    #
    # 2. Putting code (a dylib or a .framework bundle) into `Contents/Resources` causes it to be treated as a resource;
    #    the outer signature (i.e., of the whole .app bundle) does not know that this nested content is actually a code.
    #    Consequently, signing the bundle with ˙codesign --deep` will NOT sign binaries placed in the
    #    `Contents/Resources`, which may result in missing signatures when .app bundle is verified for notarization.
    #    This might be worked around by signing each binary separately, and then signing the whole bundle (without the
    #    `--deep˙ option), but requires the user to keep track of the offending binaries.
    #
    # 3. If a directory in `Contents/MacOS` contains a dot in the name, code-signing the bundle fails with
    #    ˙bundle format unrecognized, invalid, or unsuitable` due to code signing machinery treating directory as a
    #    nested .framework bundle directory.
    #
    # 4. If nested .framework bundle is malformed, the signing of the .app bundle might succeed, but subsequent
    #    verification will fail, for example with `embedded framework contains modified or invalid version` (as observed
    #    with .framework bundles shipped by contemporary PyQt/PySide PyPI wheels).
    #
    # The above requirements are unfortunately often at odds with the structure of python packages:
    #
    # * In general, python packages are mixed-content directories, where binaries and data files may be expected to
    #   be found next to each other.
    #
    #   For example, `opencv-python` provides a custom loader script that requires the package to be collected in the
    #   source-only form by PyInstaller (i.e., the python modules and scripts collected as source .py files). At the
    #   same time, it expects the .py loader script to be able to find the binary extension next to itself.
    #
    #   Another example of mixed-mode directories are Qt QML components' sub-directories, which contain both the
    #   component's plugin (a binary) and associated meta files (data files).
    #
    # * In python world, the directories often contain dots in their names.
    #
    #   Dots are often used for private directories containing binaries that are shipped with a package. For example,
    #   `numpy/.dylibs`, `scipy/.dylibs`, etc.
    #
    #   Qt QML components may also contain a dot in their name; couple of examples from `PySide2` package:
    #   `PySide2/Qt/qml/QtQuick.2`, ˙PySide2/Qt/qml/QtQuick/Controls.2˙, ˙PySide2/Qt/qml/QtQuick/Particles.2˙, etc.
    #
    #   The packages' metadata directories also invariably contain dots in the name due to version (for example,
    #   `numpy-1.24.3.dist-info`).
    #
    # In the light of all above, PyInstaller attempts to strictly place all files to their mandated location
    # (`Contents/MacOS` or `Contents/Frameworks` vs `Contents/Resources`). To preserve the illusion of mixed-content
    # directories, the content is cross-linked from one directory to the other. Specifically:
    #
    # * All entries with DATA typecode are assumed to be data files, and are always placed in corresponding directory
    #   structure rooted in `Contents/Resources`.
    #
    # * All entries with BINARY or EXTENSION typecode are always placed in corresponding directory structure rooted in
    #   `Contents/Frameworks`.
    #
    # * All entries with EXECUTABLE are placed in `Contents/MacOS` directory.
    #
    # * For the purposes of relocation, nested .framework bundles are treated as a single BINARY entity; i.e., the
    #   whole .bundle directory is placed in corresponding directory structure rooted in `Contents/Frameworks` (even
    #   though some of its contents, such as `Info.plist` file, are actually data files).
    #
    # * Top-level data files and binaries are always cross-linked to the other directory. For example, given a data file
    #   `data_file.txt` that was collected into `Contents/Resources`, we create a symbolic link called
    #   `Contents/MacOS/data_file.txt` that points to `../Resources/data_file.txt`.
    #
    # * The executable itself, while placed in `Contents/MacOS`, are cross-linked into both `Contents/Framworks` and
    #   `Contents/Resources`.
    #
    # * The stand-alone PKG entries (used with onefile builds that side-load the PKG archive) are treated as data files
    #   and collected into `Contents/Resources`, but cross-linked only into `Contents/MacOS` directory (because they
    #   must appear to be next to the program executable). This is the only entry type that is cross-linked into the
    #   `Contents/MacOS` directory and also the only data-like entry type that is not cross-linked into the
    #   `Contents/Frameworks` directory.
    #
    # * For files in sub-directories, the cross-linking behavior depends on the type of directory:
    #
    #    * A data-only directory is created in directory structure rooted in `Contents/Resources`, and cross-linked
    #      into directory structure rooted in `Contents/Frameworks` at directory level (i.e., we link the whole
    #      directory instead of individual files).
    #
    #      This largely saves us from having to deal with dots in the names of collected metadata directories, which
    #      are examples of data-only directories.
    #
    #    * A binary-only directory is created in directory structure rooted in `Contents/Frameworks`, and cross-linked
    #      into `Contents/Resources` at directory level.
    #
    #    * A mixed-content directory is created in both directory structures. Files are placed into corresponding
    #      directory structure based on their type, and cross-linked into other directory structure at file level.
    #
    #    * This rule is applied recursively; for example, a data-only sub-directory in a mixed-content directory is
    #      cross-linked at directory level, while adjacent binary and data files are cross-linked at file level.
    #
    # * To work around the issue with dots in the names of directories in `Contents/Frameworks` (applicable to
    #   binary-only or mixed-content directories), such directories are created with modified name (the dot replaced
    #   with a pre-defined pattern). Next to the modified directory, a symbolic link with original name is created,
    #   pointing to the directory with modified name. With mixed-content directories, this modification is performed
    #   only on the `Contents/Frameworks` side; the corresponding directory in `Contents/Resources` can be created
    #   directly, without name modification and symbolic link.
    #
    # * If a symbolic link needs to be created in a mixed-content directory due to a SYMLINK entry from the original
    #   TOC (i.e., a "collected" symlink originating from analysis, as opposed to the cross-linking mechanism described
    #   above), the link is created in both directory structures, each pointing to the resource in its corresponding
    #   directory structure (with one such resource being an actual file, and the other being a cross-link to the file).
    #
    # Final remarks:
    #
    # NOTE: the relocation mechanism is codified by tests in `tests/functional/test_macos_bundle_structure.py`.
    #
    # NOTE: by placing binaries and nested .framework entries into `Contents/Frameworks` instead of `Contents/MacOS`,
    # we have effectively relocated the `sys._MEIPASS` directory from the `Contents/MacOS` (= the parent directory of
    # the program executable) into `Contents/Frameworks`. This requires the PyInstaller's bootloader to detect that it
    # is running in the app-bundle mode (e.g., by checking if program executable's parent directory is `Contents/NacOS`)
    # and adjust the path accordingly.
    #
    # NOTE: the implemented relocation mechanism depends on the input TOC containing properly classified entries
    # w.r.t. BINARY vs DATA. So hooks and .spec files triggering collection of binaries as datas (and vice versa) will
    # result in incorrect placement of those files in the generated .app bundle. However, this is *not* the proper place
    # to address such issues; if necessary, automatic (re)classification should be added to analysis process, to ensure
    # that BUNDLE (as well as other build targets) receive correctly classified TOC.
    #
    # NOTE: similar to the previous note, the relocation mechanism is also not the proper place to enforce compliant
    # structure of the nested .framework bundles. Instead, this is handled by the analysis process, using the
    # `PyInstaller.utils.osx.collect_files_from_framework_bundles` helper function. So the input TOC that BUNDLE
    # receives should already contain entries that reconstruct compliant nested .framework bundles.
    def _process_bundle_toc(self, toc):
        bundle_toc = []

        # Step 1: inspect the directory layout and classify the directories according to their contents.
        directory_types = dict()

        _MIXED_DIR_TYPE = 'MIXED-DIR'
        _DATA_DIR_TYPE = 'DATA-DIR'
        _BINARY_DIR_TYPE = 'BINARY-DIR'
        _FRAMEWORK_DIR_TYPE = 'FRAMEWORK-DIR'

        _TOP_LEVEL_DIR = pathlib.PurePath('.')

        for dest_name, src_name, typecode in toc:
            dest_path = pathlib.PurePath(dest_name)

            framework_dir = self._is_framework_file(dest_path)
            if framework_dir:
                # Mark the framework directory as FRAMEWORK-DIR.
                directory_types[framework_dir] = _FRAMEWORK_DIR_TYPE
                # Treat the framework directory as BINARY file when classifying parent directories.
                typecode = 'BINARY'
                parent_dirs = framework_dir.parents
            else:
                parent_dirs = dest_path.parents
                # Treat BINARY and EXTENSION as BINARY to simplify further processing.
                if typecode == 'EXTENSION':
                    typecode = 'BINARY'

            # (Re)classify parent directories
            for parent_dir in parent_dirs:
                # Skip the top-level `.` dir. This is also the only directory that can contain EXECUTABLE and PKG
                # entries, so we do not have to worry about.
                if parent_dir == _TOP_LEVEL_DIR:
                    continue

                directory_type = _BINARY_DIR_TYPE if typecode == 'BINARY' else _DATA_DIR_TYPE  # default
                directory_type = directory_types.get(parent_dir, directory_type)

                if directory_type == _DATA_DIR_TYPE and typecode == 'BINARY':
                    directory_type = _MIXED_DIR_TYPE
                if directory_type == _BINARY_DIR_TYPE and typecode == 'DATA':
                    directory_type = _MIXED_DIR_TYPE

                directory_types[parent_dir] = directory_type

        logger.debug("Directory classification: %r", directory_types)

        # Step 2: process the obtained directory structure and create symlink entries for directories that need to be
        # cross-linked. Such directories are data-only and binary-only directories (and framework directories) that are
        # located either in the top-level directory (have no parent) or in a mixed-content directory.
        for directory_path, directory_type in directory_types.items():
            # Cross-linking at directory level applies only to data-only and binary-only directories (as well as
            # framework directories).
            if directory_type == _MIXED_DIR_TYPE:
                continue

            # The parent needs to be either top-level directory or a mixed-content directory. Otherwise, the parent
            # (or one of its ancestors) will get cross-linked, and we do not need the link here.
            parent_dir = directory_path.parent
            requires_crosslink = parent_dir == _TOP_LEVEL_DIR or directory_types.get(parent_dir) == _MIXED_DIR_TYPE
            if not requires_crosslink:
                continue

            logger.debug("Cross-linking directory %r of type %r", directory_path, directory_type)

            # Data-only directories are created in `Contents/Resources`, needs to be cross-linked into `Contents/MacOS`.
            # Vice versa for binary-only or framework directories. The directory creation is handled implicitly, when we
            # create parent directory structure for collected files.
            if directory_type == _DATA_DIR_TYPE:
                symlink_src = os.path.join('Contents/Resources', directory_path)
                symlink_dest = os.path.join('Contents/Frameworks', directory_path)
            else:
                symlink_src = os.path.join('Contents/Frameworks', directory_path)
                symlink_dest = os.path.join('Contents/Resources', directory_path)
            symlink_ref = self._compute_relative_crosslink(symlink_dest, symlink_src)

            bundle_toc.append((symlink_dest, symlink_ref, 'SYMLINK'))

        # Step 3: first part of the work-around for directories that are located in `Contents/Frameworks` but contain a
        # dot in their name. As per `codesign` rules, the only directories in `Contents/Frameworks` that are allowed to
        # contain a dot in their name are .framework bundle directories. So we replace the dot with a custom character
        # sequence (stored in global `DOT_REPLACEMENT` variable), and create a symbolic with original name pointing to
        # the modified name. This is the best we can do with code-sign requirements vs. python community showing their
        # packages' dylibs into `.dylib` subdirectories, or Qt storing their Qml components in directories named
        # `QtQuick.2`, `QtQuick/Controls.2`, `QtQuick/Particles.2`, `QtQuick/Templates.2`, etc.
        #
        # In this step, we only prepare symlink entries that link the original directory name (with dot) to the modified
        # one (with dot replaced). The parent paths for collected files are modified in later step(s).
        for directory_path, directory_type in directory_types.items():
            # .framework bundle directories contain a dot in the name, but are allowed that.
            if directory_type == _FRAMEWORK_DIR_TYPE:
                continue

            # Data-only directories are fully located in `Contents/Resources` and cross-linked to `Contents/Frameworks`
            # at directory level, so they are also allowed a dot in their name.
            if directory_type == _DATA_DIR_TYPE:
                continue

            # Apply the work-around, if necessary...
            if '.' not in directory_path.name:
                continue

            logger.debug(
                "Creating symlink to work around the dot in the name of directory %r (%s)...", str(directory_path),
                directory_type
            )

            # Create a SYMLINK entry, but only for this level. In case of nested directories with dots in names, the
            # symlinks for ancestors will be created by corresponding loop iteration.
            bundle_toc.append((
                os.path.join('Contents/Frameworks', directory_path),
                directory_path.name.replace('.', DOT_REPLACEMENT),
                'SYMLINK',
            ))

        # Step 4: process the entries for collected files, and decide whether they should be placed into
        # `Contents/MacOS`, `Contents/Frameworks`, or `Contents/Resources`, and whether they should be cross-linked into
        # other directories.
        for orig_dest_name, src_name, typecode in toc:
            orig_dest_path = pathlib.PurePath(orig_dest_name)

            # Special handling for EXECUTABLE and PKG entries
            if typecode == 'EXECUTABLE':
                # Place into `Contents/MacOS`, ...
                file_dest = os.path.join('Contents/MacOS', orig_dest_name)
                bundle_toc.append((file_dest, src_name, typecode))
                # ... and do nothing else. We explicitly avoid cross-linking the executable to `Contents/Frameworks` and
                # `Contents/Resources`, because it should be not necessary (the executable's location should be
                # discovered via `sys.executable`) and to prevent issues when executable name collides with name of a
                # package from which we collect either binaries or data files (or both); see #7314.
                continue
            elif typecode == 'PKG':
                # Place into `Contents/Resources` ...
                file_dest = os.path.join('Contents/Resources', orig_dest_name)
                bundle_toc.append((file_dest, src_name, typecode))
                # ... and cross-link only into `Contents/MacOS`.
                # This is used only in `onefile` mode, where there is actually no other content to distribute among the
                # `Contents/Resources` and `Contents/Frameworks` directories, so cross-linking into the latter makes
                # little sense.
                symlink_dest = os.path.join('Contents/MacOS', orig_dest_name)
                symlink_ref = self._compute_relative_crosslink(symlink_dest, file_dest)
                bundle_toc.append((symlink_dest, symlink_ref, 'SYMLINK'))
                continue

            # Standard data vs binary processing...

            # Determine file location based on its type.
            if self._is_framework_file(orig_dest_path):
                # File from a framework bundle; put into `Contents/Frameworks`, but never cross-link the file itself.
                # The whole .framework bundle directory will be linked as necessary by the directory cross-linking
                # mechanism.
                file_base_dir = 'Contents/Frameworks'
                crosslink_base_dir = None
            elif typecode == 'DATA':
                # Data file; relocate to `Contents/Resources` and cross-link it back into `Contents/Frameworks`.
                file_base_dir = 'Contents/Resources'
                crosslink_base_dir = 'Contents/Frameworks'
            else:
                # Binary; put into `Contents/Frameworks` and cross-link it into `Contents/Resources`.
                file_base_dir = 'Contents/Frameworks'
                crosslink_base_dir = 'Contents/Resources'

            # Determine if we need to cross-link the file. We need to do this for top-level files (the ones without
            # parent directories), and for files whose parent directories are mixed-content directories.
            requires_crosslink = False
            if crosslink_base_dir is not None:
                parent_dir = orig_dest_path.parent
                requires_crosslink = parent_dir == _TOP_LEVEL_DIR or directory_types.get(parent_dir) == _MIXED_DIR_TYPE

            # Special handling for SYMLINK entries in original TOC; if we need to cross-link a symlink entry, we create
            # it in both locations, and have each point to the (relative) resource in the same directory (so one of the
            # targets will likely be a file, and the other will be a symlink due to cross-linking).
            if typecode == 'SYMLINK' and requires_crosslink:
                bundle_toc.append((os.path.join(file_base_dir, orig_dest_name), src_name, typecode))
                bundle_toc.append((os.path.join(crosslink_base_dir, orig_dest_name), src_name, typecode))
                continue

            # The file itself.
            file_dest = os.path.join(file_base_dir, orig_dest_name)
            bundle_toc.append((file_dest, src_name, typecode))

            # Symlink for cross-linking
            if requires_crosslink:
                symlink_dest = os.path.join(crosslink_base_dir, orig_dest_name)
                symlink_ref = self._compute_relative_crosslink(symlink_dest, file_dest)
                bundle_toc.append((symlink_dest, symlink_ref, 'SYMLINK'))

        # Step 5: sanitize all destination paths in the new TOC, to ensure that paths that are rooted in
        # `Contents/Frameworks` do not contain directories with dots in their names. Doing this as a post-processing
        # step keeps code simple and clean and ensures that this step is applied to files, symlinks that originate from
        # cross-linking files, and symlinks that originate from cross-linking directories. This in turn ensures that
        # all directory hierarchies created during the actual file collection have sanitized names, and that collection
        # outcome does not depend on the order of entries in the TOC.
        sanitized_toc = []
        for dest_name, src_name, typecode in bundle_toc:
            dest_path = pathlib.PurePath(dest_name)

            # Paths rooted in Contents/Resources do not require sanitizing.
            if dest_path.parts[0] == 'Contents' and dest_path.parts[1] == 'Resources':
                sanitized_toc.append((dest_name, src_name, typecode))
                continue

            # Special handling for files from .framework bundle directories; sanitize only parent path of the .framework
            # directory.
            framework_path = self._is_framework_file(dest_path)
            if framework_path:
                parent_path = framework_path.parent
                remaining_path = dest_path.relative_to(parent_path)
            else:
                parent_path = dest_path.parent
                remaining_path = dest_path.name

            sanitized_dest_path = pathlib.PurePath(
                *parent_path.parts[:2],  # Contents/Frameworks
                *[part.replace('.', DOT_REPLACEMENT) for part in parent_path.parts[2:]],
                remaining_path,
            )
            sanitized_dest_name = str(sanitized_dest_path)

            if sanitized_dest_path != dest_path:
                logger.debug("Sanitizing dest path: %r -> %r", dest_name, sanitized_dest_name)

            sanitized_toc.append((sanitized_dest_name, src_name, typecode))

        bundle_toc = sanitized_toc

        # Normalize and sort the TOC for easier inspection
        bundle_toc = sorted(normalize_toc(bundle_toc))

        return bundle_toc

    def assemble(self):
        from PyInstaller.config import CONF

        if _check_path_overlap(self.name) and os.path.isdir(self.name):
            _rmtree(self.name)

        logger.info("Building BUNDLE %s", self.tocbasename)

        # Create a minimal Mac bundle structure.
        os.makedirs(os.path.join(self.name, "Contents", "MacOS"))
        os.makedirs(os.path.join(self.name, "Contents", "Resources"))
        os.makedirs(os.path.join(self.name, "Contents", "Frameworks"))

        # Makes sure the icon exists and attempts to convert to the proper format if applicable
        self.icon = normalize_icon_type(self.icon, ("icns",), "icns", CONF["workpath"])

        # Ensure icon path is absolute
        self.icon = os.path.abspath(self.icon)

        # Copy icns icon to Resources directory.
        shutil.copyfile(self.icon, os.path.join(self.name, 'Contents', 'Resources', os.path.basename(self.icon)))

        # Key/values for a minimal Info.plist file
        info_plist_dict = {
            "CFBundleDisplayName": self.appname,
            "CFBundleName": self.appname,

            # Required by 'codesign' utility.
            # The value for CFBundleIdentifier is used as the default unique name of your program for Code Signing
            # purposes. It even identifies the APP for access to restricted OS X areas like Keychain.
            #
            # The identifier used for signing must be globally unique. The usual form for this identifier is a
            # hierarchical name in reverse DNS notation, starting with the toplevel domain, followed by the company
            # name, followed by the department within the company, and ending with the product name. Usually in the
            # form: com.mycompany.department.appname
            # CLI option --osx-bundle-identifier sets this value.
            "CFBundleIdentifier": self.bundle_identifier,
            "CFBundleExecutable": os.path.basename(self.exename),
            "CFBundleIconFile": os.path.basename(self.icon),
            "CFBundleInfoDictionaryVersion": "6.0",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": self.version,
        }

        # Set some default values. But they still can be overwritten by the user.
        if self.console:
            # Setting EXE console=True implies LSBackgroundOnly=True.
            info_plist_dict['LSBackgroundOnly'] = True
        else:
            # Let's use high resolution by default.
            info_plist_dict['NSHighResolutionCapable'] = True

        # Merge info_plist settings from spec file
        if isinstance(self.info_plist, dict) and self.info_plist:
            info_plist_dict.update(self.info_plist)

        plist_filename = os.path.join(self.name, "Contents", "Info.plist")
        with open(plist_filename, "wb") as plist_fh:
            plistlib.dump(info_plist_dict, plist_fh)

        # Pre-process the TOC into its final BUNDLE-compatible form.
        bundle_toc = self._process_bundle_toc(self.toc)

        # Perform the actual collection.
        CONTENTS_FRAMEWORKS_PATH = pathlib.PurePath('Contents/Frameworks')
        for dest_name, src_name, typecode in bundle_toc:
            # Create parent directory structure, if necessary
            dest_path = os.path.join(self.name, dest_name)  # Absolute destination path
            dest_dir = os.path.dirname(dest_path)
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except FileExistsError:
                raise SystemExit(
                    f"Pyinstaller needs to create a directory at {dest_dir!r}, "
                    "but there already exists a file at that path!"
                )
            # Copy extensions and binaries from cache. This ensures that these files undergo additional binary
            # processing - have paths to linked libraries rewritten (relative to `@rpath`) and have rpath set to the
            # top-level directory (relative to `@loader_path`, i.e., the file's location). The "top-level" directory
            # in this case corresponds to `Contents/MacOS` (where `sys._MEIPASS` also points), so we need to pass
            # the cache retrieval function the *original* destination path (which is without preceding
            # `Contents/MacOS`).
            if typecode in ('EXTENSION', 'BINARY'):
                orig_dest_name = str(pathlib.PurePath(dest_name).relative_to(CONTENTS_FRAMEWORKS_PATH))
                src_name = process_collected_binary(
                    src_name,
                    orig_dest_name,
                    use_strip=self.strip,
                    use_upx=self.upx,
                    upx_exclude=self.upx_exclude,
                    target_arch=self.target_arch,
                    codesign_identity=self.codesign_identity,
                    entitlements_file=self.entitlements_file,
                    strict_arch_validation=(typecode == 'EXTENSION'),
                )
            if typecode == 'SYMLINK':
                os.symlink(src_name, dest_path)  # Create link at dest_path, pointing at (relative) src_name
            else:
                # BUNDLE does not support MERGE-based multipackage
                assert typecode != 'DEPENDENCY', "MERGE DEPENDENCY entries are not supported in BUNDLE!"

                # At this point, `src_name` should be a valid file.
                if not os.path.isfile(src_name):
                    raise ValueError(f"Resource {src_name!r} is not a valid file!")
                # If strict collection mode is enabled, the destination should not exist yet.
                if strict_collect_mode and os.path.exists(dest_path):
                    raise ValueError(
                        f"Attempting to collect a duplicated file into BUNDLE: {dest_name} (type: {typecode})"
                    )
                # Use `shutil.copyfile` to copy file with default permissions. We do not attempt to preserve original
                # permissions nor metadata, as they might be too restrictive and cause issues either during subsequent
                # re-build attempts or when trying to move the application bundle. For binaries (and data files with
                # executable bit set), we manually set the executable bits after copying the file.
                shutil.copyfile(src_name, dest_path)
            if (
                typecode in ('EXTENSION', 'BINARY', 'EXECUTABLE')
                or (typecode == 'DATA' and os.access(src_name, os.X_OK))
            ):
                os.chmod(dest_path, 0o755)

        # Sign the bundle
        logger.info('Signing the BUNDLE...')
        try:
            osxutils.sign_binary(self.name, self.codesign_identity, self.entitlements_file, deep=True)
        except Exception as e:
            # Display a warning or re-raise the error, depending on the environment-variable setting.
            if os.environ.get("PYINSTALLER_STRICT_BUNDLE_CODESIGN_ERROR", "0") == "0":
                logger.warning("Error while signing the bundle: %s", e)
                logger.warning("You will need to sign the bundle manually!")
            else:
                raise RuntimeError("Failed to codesign the bundle!") from e

        logger.info("Building BUNDLE %s completed successfully.", self.tocbasename)

        # Optionally verify bundle's signature. This is primarily intended for our CI.
        if os.environ.get("PYINSTALLER_VERIFY_BUNDLE_SIGNATURE", "0") != "0":
            logger.info("Verifying signature for BUNDLE %s...", self.name)
            self.verify_bundle_signature(self.name)
            logger.info("BUNDLE verification complete!")

    @staticmethod
    def verify_bundle_signature(bundle_dir):
        # First, verify the bundle signature using codesign.
        cmd_args = ['codesign', '--verify', '--all-architectures', '--deep', '--strict', bundle_dir]
        p = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
        if p.returncode:
            raise SystemError(
                f"codesign command ({cmd_args}) failed with error code {p.returncode}!\noutput: {p.stdout}"
            )

        # Ensure that code-signing information is *NOT* embedded in the files' extended attributes.
        #
        # This happens when files other than binaries are present in `Contents/MacOS` or `Contents/Frameworks`
        # directory; as the signature cannot be embedded within the file itself (contrary to binaries with
        # `LC_CODE_SIGNATURE` section in their header), it ends up stores in the file's extended attributes. However,
        # if such bundle is transferred using a method that does not support extended attributes (for example, a zip
        # file), the signatures on these files are lost, and the signature of the bundle as a whole becomes invalid.
        # This is the primary reason why we need to relocate non-binaries into `Contents/Resources` - the signatures
        # for files in that directory end up stored in `Contents/_CodeSignature/CodeResources` file.
        #
        # This check therefore aims to ensure that all files have been properly relocated to their corresponding
        # locations w.r.t. the code-signing requirements.

        try:
            import xattr
        except ModuleNotFoundError:
            logger.info("xattr package not available; skipping verification of extended attributes!")
            return

        CODESIGN_ATTRS = (
            "com.apple.cs.CodeDirectory",
            "com.apple.cs.CodeRequirements",
            "com.apple.cs.CodeRequirements-1",
            "com.apple.cs.CodeSignature",
        )

        for entry in pathlib.Path(bundle_dir).rglob("*"):
            if not entry.is_file():
                continue

            file_attrs = xattr.listxattr(entry)
            if any([codesign_attr in file_attrs for codesign_attr in CODESIGN_ATTRS]):
                raise ValueError(f"Code-sign attributes found in extended attributes of {str(entry)!r}!")
