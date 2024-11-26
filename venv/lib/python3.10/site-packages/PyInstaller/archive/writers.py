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
Utilities to create data structures for embedding Python modules and additional files into the executable.
"""

import marshal
import os
import shutil
import struct
import sys
import zlib

from PyInstaller.building.utils import get_code_object, strip_paths_in_code
from PyInstaller.compat import BYTECODE_MAGIC, is_win, strict_collect_mode
from PyInstaller.loader.pyimod01_archive import PYZ_ITEM_MODULE, PYZ_ITEM_NSPKG, PYZ_ITEM_PKG


class ZlibArchiveWriter:
    """
    Writer for PyInstaller's PYZ (ZlibArchive) archive. The archive is used to store collected byte-compiled Python
    modules, as individually-compressed entries.
    """
    _PYZ_MAGIC_PATTERN = b'PYZ\0'
    _HEADER_LENGTH = 12 + 5
    _COMPRESSION_LEVEL = 6  # zlib compression level

    def __init__(self, filename, entries, code_dict=None):
        """
        filename
            Target filename of the archive.
        entries
            An iterable containing entries in the form of tuples: (name, src_path, typecode), where `name` is the name
            under which the resource is stored (e.g., python module name, without suffix), `src_path` is name of the
            file from which the resource is read, and `typecode` is the Analysis-level TOC typecode (`PYMODULE`).
        code_dict
            Optional code dictionary containing code objects for analyzed/collected python modules.
        """
        code_dict = code_dict or {}

        with open(filename, "wb") as fp:
            # Reserve space for the header.
            fp.write(b'\0' * self._HEADER_LENGTH)

            # Write entries' data and collect TOC entries
            toc = []
            for entry in entries:
                toc_entry = self._write_entry(fp, entry, code_dict)
                toc.append(toc_entry)

            # Write TOC
            toc_offset = fp.tell()
            toc_data = marshal.dumps(toc)
            fp.write(toc_data)

            # Write header:
            #  - PYZ magic pattern (4 bytes)
            #  - python bytecode magic pattern (4 bytes)
            #  - TOC offset (32-bit int, 4 bytes)
            #  - 4 unused bytes
            fp.seek(0, os.SEEK_SET)

            fp.write(self._PYZ_MAGIC_PATTERN)
            fp.write(BYTECODE_MAGIC)
            fp.write(struct.pack('!i', toc_offset))

    @classmethod
    def _write_entry(cls, fp, entry, code_dict):
        name, src_path, typecode = entry
        assert typecode == 'PYMODULE'

        typecode = PYZ_ITEM_MODULE
        if src_path in ('-', None):
            # This is a NamespacePackage, modulegraph marks them by using the filename '-'. (But wants to use None,
            # so check for None, too, to be forward-compatible.)
            typecode = PYZ_ITEM_NSPKG
        else:
            src_basename, _ = os.path.splitext(os.path.basename(src_path))
            if src_basename == '__init__':
                typecode = PYZ_ITEM_PKG
        data = marshal.dumps(code_dict[name])

        # First compress, then encrypt.
        obj = zlib.compress(data, cls._COMPRESSION_LEVEL)

        # Create TOC entry
        toc_entry = (name, (typecode, fp.tell(), len(obj)))

        # Write data blob
        fp.write(obj)

        return toc_entry


class CArchiveWriter:
    """
    Writer for PyInstaller's CArchive (PKG) archive.

    This archive contains all files that are bundled within an executable; a PYZ (ZlibArchive), DLLs, Python C
    extensions, and other data files that are bundled in onefile mode.

    The archive can be read from either C (bootloader code at application's run-time) or Python (for debug purposes).
    """
    _COOKIE_MAGIC_PATTERN = b'MEI\014\013\012\013\016'

    # For cookie and TOC entry structure, see `PyInstaller.archive.readers.CArchiveReader`.
    _COOKIE_FORMAT = '!8sIIii64s'
    _COOKIE_LENGTH = struct.calcsize(_COOKIE_FORMAT)

    _TOC_ENTRY_FORMAT = '!iIIIBB'
    _TOC_ENTRY_LENGTH = struct.calcsize(_TOC_ENTRY_FORMAT)

    _COMPRESSION_LEVEL = 9  # zlib compression level

    def __init__(self, filename, entries, pylib_name):
        """
        filename
            Target filename of the archive.
        entries
            An iterable containing entries in the form of tuples: (dest_name, src_name, compress, typecode), where
            `dest_name` is the name under which the resource is stored in the archive (and name under which it is
            extracted at runtime), `src_name` is name of the file from which the resouce is read, `compress` is a
            boolean compression flag, and `typecode` is the Analysis-level TOC typecode.
        pylib_name
            Name of the python shared library.
        """
        self._collected_names = set()  # Track collected names for strict package mode.

        with open(filename, "wb") as fp:
            # Write entries' data and collect TOC entries
            toc = []
            for entry in entries:
                toc_entry = self._write_entry(fp, entry)
                toc.append(toc_entry)

            # Write TOC
            toc_offset = fp.tell()
            toc_data = self._serialize_toc(toc)
            toc_length = len(toc_data)

            fp.write(toc_data)

            # Write cookie
            archive_length = toc_offset + toc_length + self._COOKIE_LENGTH
            pyvers = sys.version_info[0] * 100 + sys.version_info[1]
            cookie_data = struct.pack(
                self._COOKIE_FORMAT,
                self._COOKIE_MAGIC_PATTERN,
                archive_length,
                toc_offset,
                toc_length,
                pyvers,
                pylib_name.encode('ascii'),
            )

            fp.write(cookie_data)

    def _write_entry(self, fp, entry):
        dest_name, src_name, compress, typecode = entry

        # Write OPTION entries as-is, without normalizing them. This also exempts them from duplication check,
        # allowing them to be specified multiple times.
        if typecode == 'o':
            return self._write_blob(fp, b"", dest_name, typecode)

        # Ensure forward slashes in paths are on Windows converted to back slashes '\\', as on Windows the bootloader
        # works only with back slashes.
        dest_name = os.path.normpath(dest_name)
        if is_win and os.path.sep == '/':
            # When building under MSYS, the above path normalization uses Unix-style separators, so replace them
            # manually.
            dest_name = dest_name.replace(os.path.sep, '\\')

        # Strict pack/collect mode: keep track of the destination names, and raise an error if we try to add a duplicate
        # (a file with same destination name, subject to OS case normalization rules).
        if strict_collect_mode:
            normalized_dest = None
            if typecode in ('s', 'm', 'M'):
                # Exempt python source scripts and modules from the check.
                pass
            else:
                # Everything else; normalize the case
                normalized_dest = os.path.normcase(dest_name)
            # Check for existing entry, if applicable
            if normalized_dest:
                if normalized_dest in self._collected_names:
                    raise ValueError(
                        f"Attempting to collect a duplicated file into CArchive: {normalized_dest} (type: {typecode})"
                    )
                self._collected_names.add(normalized_dest)

        if typecode == 'd':
            # Dependency; merge src_name (= reference path prefix) and dest_name (= name) into single-string format that
            # is parsed by bootloader.
            return self._write_blob(fp, b"", f"{src_name}:{dest_name}", typecode)
        elif typecode == 's':
            # If it is a source code file, compile it to a code object and marshal the object, so it can be unmarshalled
            # by the bootloader.
            code = get_code_object(dest_name, src_name)
            code = strip_paths_in_code(code)
            return self._write_blob(fp, marshal.dumps(code), dest_name, typecode, compress=compress)
        elif typecode in ('m', 'M'):
            # Read the PYC file
            with open(src_name, "rb") as in_fp:
                data = in_fp.read()
            assert data[:4] == BYTECODE_MAGIC
            # Skip the PYC header, load the code object.
            code = marshal.loads(data[16:])
            code = strip_paths_in_code(code)
            # These module entries are loaded and executed within the bootloader, which requires only the code
            # object, without the PYC header.
            return self._write_blob(fp, marshal.dumps(code), dest_name, typecode, compress=compress)
        elif typecode == 'n':
            # Symbolic link; store target name (as NULL-terminated string)
            data = src_name.encode('utf-8') + b'\x00'
            return self._write_blob(fp, data, dest_name, typecode, compress=compress)
        else:
            return self._write_file(fp, src_name, dest_name, typecode, compress=compress)

    def _write_blob(self, out_fp, blob: bytes, dest_name, typecode, compress=False):
        """
        Write the binary contents (**blob**) of a small file to the archive and return the corresponding CArchive TOC
        entry.
        """
        data_offset = out_fp.tell()
        data_length = len(blob)
        if compress:
            blob = zlib.compress(blob, level=self._COMPRESSION_LEVEL)
        out_fp.write(blob)

        return (data_offset, len(blob), data_length, int(compress), typecode, dest_name)

    def _write_file(self, out_fp, src_name, dest_name, typecode, compress=False):
        """
        Stream copy a large file into the archive and return the corresponding CArchive TOC entry.
        """
        data_offset = out_fp.tell()
        data_length = os.stat(src_name).st_size
        with open(src_name, 'rb') as in_fp:
            if compress:
                tmp_buffer = bytearray(16 * 1024)
                compressor = zlib.compressobj(self._COMPRESSION_LEVEL)
                while True:
                    num_read = in_fp.readinto(tmp_buffer)
                    if not num_read:
                        break
                    out_fp.write(compressor.compress(tmp_buffer[:num_read]))
                out_fp.write(compressor.flush())
            else:
                shutil.copyfileobj(in_fp, out_fp)

        return (data_offset, out_fp.tell() - data_offset, data_length, int(compress), typecode, dest_name)

    @classmethod
    def _serialize_toc(cls, toc):
        serialized_toc = []
        for toc_entry in toc:
            data_offset, compressed_length, data_length, compress, typecode, name = toc_entry

            # Encode names as UTF-8. This should be safe as standard python modules only contain ASCII-characters (and
            # standard shared libraries should have the same), and thus the C-code still can handle this correctly.
            name = name.encode('utf-8')
            name_length = len(name) + 1  # Add 1 for string-terminating zero byte.

            # Ensure TOC entries are aligned on 16-byte boundary, so they can be read by bootloader (C code) on
            # platforms with strict data alignment requirements (for example linux on `armhf`/`armv7`, such as 32-bit
            # Debian Buster on Raspberry Pi).
            entry_length = cls._TOC_ENTRY_LENGTH + name_length
            if entry_length % 16 != 0:
                padding_length = 16 - (entry_length % 16)
                name_length += padding_length

            # Serialize
            serialized_entry = struct.pack(
                cls._TOC_ENTRY_FORMAT + f"{name_length}s",  # "Ns" format automatically pads the string with zero bytes.
                cls._TOC_ENTRY_LENGTH + name_length,
                data_offset,
                compressed_length,
                data_length,
                compress,
                ord(typecode),
                name,
            )
            serialized_toc.append(serialized_entry)

        return b''.join(serialized_toc)


class SplashWriter:
    """
    Writer for the splash screen resources archive.

    The resulting archive is added as an entry into the CArchive with the typecode PKG_ITEM_SPLASH.
    """
    # This struct describes the splash resources as it will be in an buffer inside the bootloader. All necessary parts
    # are bundled, the *_len and *_offset fields describe the data beyond this header definition.
    # Whereas script and image fields are binary data, the requirements fields describe an array of strings. Each string
    # is null-terminated in order to easily iterate over this list from within C.
    #
    #   typedef struct _splash_data_header {
    #       char tcl_libname[16];  /* Name of tcl library, e.g. tcl86t.dll */
    #       char tk_libname[16];   /* Name of tk library, e.g. tk86t.dll */
    #       char tk_lib[16];       /* Tk Library generic, e.g. "tk/" */
    #       char rundir[16];       /* temp folder inside extraction path in
    #                               * which the dependencies are extracted */
    #
    #       int script_len;        /* Length of the script */
    #       int script_offset;     /* Offset (rel to start) of the script */
    #
    #       int image_len;         /* Length of the image data */
    #       int image_offset;      /* Offset (rel to start) of the image */
    #
    #       int requirements_len;
    #       int requirements_offset;
    #
    #   } SPLASH_DATA_HEADER;
    #
    _HEADER_FORMAT = '!16s 16s 16s 16s ii ii ii'
    _HEADER_LENGTH = struct.calcsize(_HEADER_FORMAT)

    # The created archive is compressed by the CArchive, so no need to compress the data here.

    def __init__(self, filename, name_list, tcl_libname, tk_libname, tklib, rundir, image, script):
        """
        Writer for splash screen resources that are bundled into the CArchive as a single archive/entry.

        :param filename: The filename of the archive to create
        :param name_list: List of filenames for the requirements array
        :param str tcl_libname: Name of the tcl shared library file
        :param str tk_libname: Name of the tk shared library file
        :param str tklib: Root of tk library (e.g. tk/)
        :param str rundir: Unique path to extract requirements to
        :param Union[str, bytes] image: Image like object
        :param str script: The tcl/tk script to execute to create the screen.
        """

        # Ensure forward slashes in dependency names are on Windows converted to back slashes '\\', as on Windows the
        # bootloader works only with back slashes.
        def _normalize_filename(filename):
            filename = os.path.normpath(filename)
            if is_win and os.path.sep == '/':
                # When building under MSYS, the above path normalization uses Unix-style separators, so replace them
                # manually.
                filename = filename.replace(os.path.sep, '\\')
            return filename

        name_list = [_normalize_filename(name) for name in name_list]

        with open(filename, "wb") as fp:
            # Reserve space for the header.
            fp.write(b'\0' * self._HEADER_LENGTH)

            # Serialize the requirements list. This list (more an array) contains the names of all files the bootloader
            # needs to extract before the splash screen can be started. The implementation terminates every name with a
            # null-byte, that keeps the list short memory wise and makes it iterable from C.
            requirements_len = 0
            requirements_offset = fp.tell()
            for name in name_list:
                name = name.encode('utf-8') + b'\0'
                fp.write(name)
                requirements_len += len(name)

            # Write splash script
            script_offset = fp.tell()
            script_len = len(script)
            fp.write(script.encode("utf-8"))

            # Write splash image. If image is a bytes buffer, it is written directly into the archive. Otherwise, it
            # is assumed to be a path and the file is copied into the archive.
            image_offset = fp.tell()
            if isinstance(image, bytes):
                # Image was converted by PIL/Pillow and is already in buffer
                image_len = len(image)
                fp.write(image)
            else:
                # Read image into buffer
                with open(image, 'rb') as image_fp:
                    image_data = image_fp.read()
                image_len = len(image_data)
                fp.write(image_data)
                del image_data

            # Write header
            header_data = struct.pack(
                self._HEADER_FORMAT,
                tcl_libname.encode("utf-8"),
                tk_libname.encode("utf-8"),
                tklib.encode("utf-8"),
                rundir.encode("utf-8"),
                script_len,
                script_offset,
                image_len,
                image_offset,
                requirements_len,
                requirements_offset,
            )

            fp.seek(0, os.SEEK_SET)
            fp.write(header_data)
