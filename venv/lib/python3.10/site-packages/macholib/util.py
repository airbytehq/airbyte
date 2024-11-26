import os
import shutil
import stat
import struct
import sys

from macholib import mach_o

MAGIC = [
    struct.pack("!L", getattr(mach_o, "MH_" + _))
    for _ in ["MAGIC", "CIGAM", "MAGIC_64", "CIGAM_64"]
]
FAT_MAGIC_BYTES = struct.pack("!L", mach_o.FAT_MAGIC)
MAGIC_LEN = 4
STRIPCMD = ["/usr/bin/strip", "-x", "-S", "-"]

try:
    unicode
except NameError:
    unicode = str


def fsencoding(s, encoding=sys.getfilesystemencoding()):  # noqa: M511,B008
    """
    Ensure the given argument is in filesystem encoding (not unicode)
    """
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return s


def move(src, dst):
    """
    move that ensures filesystem encoding of paths
    """
    shutil.move(fsencoding(src), fsencoding(dst))


def copy2(src, dst):
    """
    copy2 that ensures filesystem encoding of paths
    """
    shutil.copy2(fsencoding(src), fsencoding(dst))


def flipwritable(fn, mode=None):
    """
    Flip the writability of a file and return the old mode. Returns None
    if the file is already writable.
    """
    if os.access(fn, os.W_OK):
        return None
    old_mode = os.stat(fn).st_mode
    os.chmod(fn, stat.S_IWRITE | old_mode)
    return old_mode


class fileview(object):
    """
    A proxy for file-like objects that exposes a given view of a file
    """

    def __init__(self, fileobj, start, size):
        self._fileobj = fileobj
        self._start = start
        self._end = start + size

    def __repr__(self):
        return "<fileview [%d, %d] %r>" % (self._start, self._end, self._fileobj)

    def tell(self):
        return self._fileobj.tell() - self._start

    def _checkwindow(self, seekto, op):
        if not (self._start <= seekto <= self._end):
            raise IOError(
                "%s to offset %d is outside window [%d, %d]"
                % (op, seekto, self._start, self._end)
            )

    def seek(self, offset, whence=0):
        seekto = offset
        if whence == 0:
            seekto += self._start
        elif whence == 1:
            seekto += self._fileobj.tell()
        elif whence == 2:
            seekto += self._end
        else:
            raise IOError("Invalid whence argument to seek: %r" % (whence,))
        self._checkwindow(seekto, "seek")
        self._fileobj.seek(seekto)

    def write(self, bytes):
        here = self._fileobj.tell()
        self._checkwindow(here, "write")
        self._checkwindow(here + len(bytes), "write")
        self._fileobj.write(bytes)

    def read(self, size=sys.maxsize):
        if size < 0:
            raise ValueError(
                "Invalid size %s while reading from %s", size, self._fileobj
            )
        here = self._fileobj.tell()
        self._checkwindow(here, "read")
        bytes = min(size, self._end - here)
        return self._fileobj.read(bytes)


def mergecopy(src, dest):
    """
    copy2, but only if the destination isn't up to date
    """
    if os.path.exists(dest) and os.stat(dest).st_mtime >= os.stat(src).st_mtime:
        return

    copy2(src, dest)


def mergetree(src, dst, condition=None, copyfn=mergecopy, srcbase=None):
    """
    Recursively merge a directory tree using mergecopy().
    """
    src = fsencoding(src)
    dst = fsencoding(dst)
    if srcbase is None:
        srcbase = src
    names = map(fsencoding, os.listdir(src))
    try:
        os.makedirs(dst)
    except OSError:
        pass
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if condition is not None and not condition(srcname):
            continue
        try:
            if os.path.islink(srcname):
                realsrc = os.readlink(srcname)
                os.symlink(realsrc, dstname)
            elif os.path.isdir(srcname):
                mergetree(
                    srcname,
                    dstname,
                    condition=condition,
                    copyfn=copyfn,
                    srcbase=srcbase,
                )
            else:
                copyfn(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, why))
    if errors:
        raise IOError(errors)


def sdk_normalize(filename):
    """
    Normalize a path to strip out the SDK portion, normally so that it
    can be decided whether it is in a system path or not.
    """
    if filename.startswith("/Developer/SDKs/"):
        pathcomp = filename.split("/")
        del pathcomp[1:4]
        filename = "/".join(pathcomp)
    return filename


NOT_SYSTEM_FILES = []


def in_system_path(filename):
    """
    Return True if the file is in a system path
    """
    fn = sdk_normalize(os.path.realpath(filename))
    if fn.startswith("/usr/local/"):
        return False
    elif fn.startswith("/System/") or fn.startswith("/usr/"):
        if fn in NOT_SYSTEM_FILES:
            return False
        return True
    else:
        return False


def has_filename_filter(module):
    """
    Return False if the module does not have a filename attribute
    """
    return getattr(module, "filename", None) is not None


def get_magic():
    """
    Get a list of valid Mach-O header signatures, not including the fat header
    """
    return MAGIC


def is_platform_file(path):
    """
    Return True if the file is Mach-O
    """
    if not os.path.exists(path) or os.path.islink(path):
        return False
    # If the header is fat, we need to read into the first arch
    with open(path, "rb") as fileobj:
        bytes = fileobj.read(MAGIC_LEN)
        if bytes == FAT_MAGIC_BYTES:
            # Read in the fat header
            fileobj.seek(0)
            header = mach_o.fat_header.from_fileobj(fileobj, _endian_=">")
            if header.nfat_arch < 1:
                return False
            # Read in the first fat arch header
            arch = mach_o.fat_arch.from_fileobj(fileobj, _endian_=">")
            fileobj.seek(arch.offset)
            # Read magic off the first header
            bytes = fileobj.read(MAGIC_LEN)
    for magic in MAGIC:
        if bytes == magic:
            return True
    return False


def iter_platform_files(dst):
    """
    Walk a directory and yield each full path that is a Mach-O file
    """
    for root, _dirs, files in os.walk(dst):
        for fn in files:
            fn = os.path.join(root, fn)
            if is_platform_file(fn):
                yield fn


def strip_files(files, argv_max=(256 * 1024)):
    """
    Strip a list of files
    """
    tostrip = [(fn, flipwritable(fn)) for fn in files]
    while tostrip:
        cmd = list(STRIPCMD)
        flips = []
        pathlen = sum(len(s) + 1 for s in cmd)
        while pathlen < argv_max:
            if not tostrip:
                break
            added, flip = tostrip.pop()
            pathlen += len(added) + 1
            cmd.append(added)
            flips.append((added, flip))
        else:
            cmd.pop()
            tostrip.append(flips.pop())
        os.spawnv(os.P_WAIT, cmd[0], cmd)
        for args in flips:
            flipwritable(*args)
