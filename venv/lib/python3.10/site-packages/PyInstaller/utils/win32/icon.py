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
The code in this module supports the --icon parameter on Windows.
(For --icon support under Mac OS, see building/osx.py.)

The only entry point, called from api.py, is CopyIcons(), below. All the elaborate structure of classes that follows
is used to support the operation of CopyIcons_FromIco(). None of these classes and globals are referenced outside
this module.
"""

import os.path
import struct

import PyInstaller.log as logging
from PyInstaller import config
from PyInstaller.compat import pywintypes, win32api
from PyInstaller.building.icon import normalize_icon_type

logger = logging.getLogger(__name__)

RT_ICON = 3
RT_GROUP_ICON = 14
LOAD_LIBRARY_AS_DATAFILE = 2


class Structure:
    def __init__(self):
        size = self._sizeInBytes = struct.calcsize(self._format_)
        self._fields_ = list(struct.unpack(self._format_, b'\000' * size))
        indexes = self._indexes_ = {}
        for i, nm in enumerate(self._names_):
            indexes[nm] = i

    def dump(self):
        logger.info("DUMP of %s", self)
        for name in self._names_:
            if not name.startswith('_'):
                logger.info("%20s = %s", name, getattr(self, name))
        logger.info("")

    def __getattr__(self, name):
        if name in self._names_:
            index = self._indexes_[name]
            return self._fields_[index]
        try:
            return self.__dict__[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def __setattr__(self, name, value):
        if name in self._names_:
            index = self._indexes_[name]
            self._fields_[index] = value
        else:
            self.__dict__[name] = value

    def tostring(self):
        return struct.pack(self._format_, *self._fields_)

    def fromfile(self, file):
        data = file.read(self._sizeInBytes)
        self._fields_ = list(struct.unpack(self._format_, data))


class ICONDIRHEADER(Structure):
    _names_ = "idReserved", "idType", "idCount"
    _format_ = "hhh"


class ICONDIRENTRY(Structure):
    _names_ = ("bWidth", "bHeight", "bColorCount", "bReserved", "wPlanes", "wBitCount", "dwBytesInRes", "dwImageOffset")
    _format_ = "bbbbhhii"


class GRPICONDIR(Structure):
    _names_ = "idReserved", "idType", "idCount"
    _format_ = "hhh"


class GRPICONDIRENTRY(Structure):
    _names_ = ("bWidth", "bHeight", "bColorCount", "bReserved", "wPlanes", "wBitCount", "dwBytesInRes", "nID")
    _format_ = "bbbbhhih"


# An IconFile instance is created for each .ico file given.
class IconFile:
    def __init__(self, path):
        self.path = path
        try:
            # The path is from the user parameter, don't trust it.
            file = open(self.path, "rb")
        except OSError:
            # The icon file can't be opened for some reason. Stop the
            # program with an informative message.
            raise SystemExit(f'Unable to open icon file {self.path}!')
        with file:
            self.entries = []
            self.images = []
            header = self.header = ICONDIRHEADER()
            header.fromfile(file)
            for i in range(header.idCount):
                entry = ICONDIRENTRY()
                entry.fromfile(file)
                self.entries.append(entry)
            for e in self.entries:
                file.seek(e.dwImageOffset, 0)
                self.images.append(file.read(e.dwBytesInRes))

    def grp_icon_dir(self):
        return self.header.tostring()

    def grp_icondir_entries(self, id=1):
        data = b''
        for entry in self.entries:
            e = GRPICONDIRENTRY()
            for n in e._names_[:-1]:
                setattr(e, n, getattr(entry, n))
            e.nID = id
            id = id + 1
            data = data + e.tostring()
        return data


def CopyIcons_FromIco(dstpath, srcpath, id=1):
    """
    Use the Win API UpdateResource facility to apply the icon resource(s) to the .exe file.

    :param str dstpath: absolute path of the .exe file being built.
    :param str srcpath: list of 1 or more .ico file paths
    """
    icons = map(IconFile, srcpath)
    logger.debug("Copying icons from %s", srcpath)

    hdst = win32api.BeginUpdateResource(dstpath, 0)

    iconid = 1
    # Each step in the following enumerate() will instantiate an IconFile object, as a result of deferred execution
    # of the map() above.
    for i, f in enumerate(icons):
        data = f.grp_icon_dir()
        data = data + f.grp_icondir_entries(iconid)
        win32api.UpdateResource(hdst, RT_GROUP_ICON, i + 1, data)
        logger.debug("Writing RT_GROUP_ICON %d resource with %d bytes", i + 1, len(data))
        for data in f.images:
            win32api.UpdateResource(hdst, RT_ICON, iconid, data)
            logger.debug("Writing RT_ICON %d resource with %d bytes", iconid, len(data))
            iconid = iconid + 1

    win32api.EndUpdateResource(hdst, 0)


def CopyIcons(dstpath, srcpath):
    """
    Called from building/api.py to handle icons. If the input was by --icon on the command line, srcpath is a single
    string. However, it is possible to modify the spec file adding icon=['foo.ico','bar.ico'] to the EXE() statement.
    In that case, srcpath is a list of strings.

    The string format is either path-to-.ico or path-to-.exe,n for n an integer resource index in the .exe. In either
    case, the path can be relative or absolute.
    """

    if isinstance(srcpath, str):
        # Just a single string, make it a one-element list.
        srcpath = [srcpath]

    def splitter(s):
        """
        Convert "pathname" to tuple ("pathname", None)
        Convert "pathname,n" to tuple ("pathname", n)
        """
        try:
            srcpath, index = s.split(',')
            return srcpath.strip(), int(index)
        except ValueError:
            return s, None

    # split all the items in the list into tuples as above.
    srcpath = list(map(splitter, srcpath))

    if len(srcpath) > 1:
        # More than one icon source given. We currently handle multiple icons by calling CopyIcons_FromIco(), which only
        # allows .ico, but will convert to that format if needed.
        #
        # Note that a ",index" on a .ico is just ignored in the single or multiple case.
        srcs = []
        for s in srcpath:
            srcs.append(normalize_icon_type(s[0], ("ico",), "ico", config.CONF["workpath"]))
        return CopyIcons_FromIco(dstpath, srcs)

    # Just one source given.
    srcpath, index = srcpath[0]

    # Makes sure the icon exists and attempts to convert to the proper format if applicable
    srcpath = normalize_icon_type(srcpath, ("exe", "ico"), "ico", config.CONF["workpath"])

    srcext = os.path.splitext(srcpath)[1]

    # Handle the simple case of foo.ico, ignoring any index.
    if srcext.lower() == '.ico':
        return CopyIcons_FromIco(dstpath, [srcpath])

    # Single source is not .ico, presumably it is .exe (and if not, some error will occur).
    if index is not None:
        logger.debug("Copying icon from %s, %d", srcpath, index)
    else:
        logger.debug("Copying icons from %s", srcpath)

    try:
        # Attempt to load the .ico or .exe containing the icon into memory using the same mechanism as if it were a DLL.
        # If this fails for any reason (for example if the file does not exist or is not a .ico/.exe) then LoadLibraryEx
        # returns a null handle and win32api raises a unique exception with a win error code and a string.
        hsrc = win32api.LoadLibraryEx(srcpath, 0, LOAD_LIBRARY_AS_DATAFILE)
    except pywintypes.error as W32E:
        # We could continue with no icon (i.e., just return), but it seems best to terminate the build with a message.
        raise SystemExit(
            "Unable to load icon file {}\n    {} (Error code {})".format(srcpath, W32E.strerror, W32E.winerror)
        )
    hdst = win32api.BeginUpdateResource(dstpath, 0)
    if index is None:
        grpname = win32api.EnumResourceNames(hsrc, RT_GROUP_ICON)[0]
    elif index >= 0:
        grpname = win32api.EnumResourceNames(hsrc, RT_GROUP_ICON)[index]
    else:
        grpname = -index
    data = win32api.LoadResource(hsrc, RT_GROUP_ICON, grpname)
    win32api.UpdateResource(hdst, RT_GROUP_ICON, grpname, data)
    for iconname in win32api.EnumResourceNames(hsrc, RT_ICON):
        data = win32api.LoadResource(hsrc, RT_ICON, iconname)
        win32api.UpdateResource(hdst, RT_ICON, iconname, data)
    win32api.FreeLibrary(hsrc)
    win32api.EndUpdateResource(hdst, 0)


if __name__ == "__main__":
    import sys

    dstpath = sys.argv[1]
    srcpath = sys.argv[2:]
    CopyIcons(dstpath, srcpath)
