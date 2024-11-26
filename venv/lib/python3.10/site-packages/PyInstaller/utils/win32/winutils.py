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
Utilities for Windows platform.
"""

from PyInstaller import compat


def get_windows_dir():
    """
    Return the Windows directory, e.g., C:\\Windows.
    """
    windir = compat.win32api.GetWindowsDirectory()
    if not windir:
        raise SystemExit("Error: Cannot determine Windows directory!")
    return windir


def get_system_path():
    """
    Return the required Windows system paths.
    """
    sys_dir = compat.win32api.GetSystemDirectory()
    # Ensure C:\Windows\system32  and C:\Windows directories are always present in PATH variable.
    # C:\Windows\system32 is valid even for 64-bit Windows. Access do DLLs are transparently redirected to
    # C:\Windows\syswow64 for 64bit applactions.
    # See http://msdn.microsoft.com/en-us/library/aa384187(v=vs.85).aspx
    return [sys_dir, get_windows_dir()]


def get_pe_file_machine_type(filename):
    """
    Return the machine type code from the header of the given PE file.
    """
    import pefile

    with pefile.PE(filename, fast_load=True) as pe:
        return pe.FILE_HEADER.Machine


def set_exe_build_timestamp(exe_path, timestamp):
    """
    Modifies the executable's build timestamp by updating values in the corresponding PE headers.
    """
    import pefile

    with pefile.PE(exe_path, fast_load=True) as pe:
        # Manually perform a full load. We need it to load all headers, but specifying it in the constructor triggers
        # byte statistics gathering that takes forever with large files. So we try to go around that...
        pe.full_load()

        # Set build timestamp.
        # See: https://0xc0decafe.com/malware-analyst-guide-to-pe-timestamps
        timestamp = int(timestamp)
        # Set timestamp field in FILE_HEADER
        pe.FILE_HEADER.TimeDateStamp = timestamp
        # MSVC-compiled executables contain (at least?) one DIRECTORY_ENTRY_DEBUG entry that also contains timestamp
        # with same value as set in FILE_HEADER. So modify that as well, as long as it is set.
        debug_entries = getattr(pe, 'DIRECTORY_ENTRY_DEBUG', [])
        for debug_entry in debug_entries:
            if debug_entry.struct.TimeDateStamp:
                debug_entry.struct.TimeDateStamp = timestamp

        # Generate updated EXE data
        data = pe.write()

    # Rewrite the exe
    with open(exe_path, 'wb') as fp:
        fp.write(data)


def update_exe_pe_checksum(exe_path):
    """
    Compute the executable's PE checksum, and write it to PE headers.

    This optional checksum is supposed to protect the executable against corruption but some anti-viral software have
    taken to flagging anything without it set correctly as malware. See issue #5579.
    """
    import pefile

    # Compute checksum using our equivalent of the MapFileAndCheckSumW - for large files, it is significantly faster
    # than pure-pyton pefile.PE.generate_checksum(). However, it requires the file to be on disk (i.e., cannot operate
    # on a memory buffer).
    try:
        checksum = compute_exe_pe_checksum(exe_path)
    except Exception as e:
        raise RuntimeError("Failed to compute PE checksum!") from e

    # Update the checksum
    with pefile.PE(exe_path, fast_load=True) as pe:
        pe.OPTIONAL_HEADER.CheckSum = checksum

        # Generate updated EXE data
        data = pe.write()

    # Rewrite the exe
    with open(exe_path, 'wb') as fp:
        fp.write(data)


def compute_exe_pe_checksum(exe_path):
    """
    This is a replacement for the MapFileAndCheckSumW function. As noted in MSDN documentation, the Microsoft's
    implementation of MapFileAndCheckSumW internally calls its ASCII variant (MapFileAndCheckSumA), and therefore
    cannot handle paths that contain characters that are not representable in the current code page.
    See: https://docs.microsoft.com/en-us/windows/win32/api/imagehlp/nf-imagehlp-mapfileandchecksumw

    This function is based on Wine's implementation of MapFileAndCheckSumW, and due to being based entirely on
    the pure widechar-API functions, it is not limited by the current code page.
    """
    # ctypes bindings for relevant win32 API functions
    import ctypes
    from ctypes import windll, wintypes

    INVALID_HANDLE = wintypes.HANDLE(-1).value

    GetLastError = ctypes.windll.kernel32.GetLastError
    GetLastError.argtypes = ()
    GetLastError.restype = wintypes.DWORD

    CloseHandle = windll.kernel32.CloseHandle
    CloseHandle.argtypes = (
        wintypes.HANDLE,  # hObject
    )
    CloseHandle.restype = wintypes.BOOL

    CreateFileW = windll.kernel32.CreateFileW
    CreateFileW.argtypes = (
        wintypes.LPCWSTR,  # lpFileName
        wintypes.DWORD,  # dwDesiredAccess
        wintypes.DWORD,  # dwShareMode
        wintypes.LPVOID,  # lpSecurityAttributes
        wintypes.DWORD,  # dwCreationDisposition
        wintypes.DWORD,  # dwFlagsAndAttributes
        wintypes.HANDLE,  # hTemplateFile
    )
    CreateFileW.restype = wintypes.HANDLE

    CreateFileMappingW = windll.kernel32.CreateFileMappingW
    CreateFileMappingW.argtypes = (
        wintypes.HANDLE,  # hFile
        wintypes.LPVOID,  # lpSecurityAttributes
        wintypes.DWORD,  # flProtect
        wintypes.DWORD,  # dwMaximumSizeHigh
        wintypes.DWORD,  # dwMaximumSizeLow
        wintypes.LPCWSTR,  # lpName
    )
    CreateFileMappingW.restype = wintypes.HANDLE

    MapViewOfFile = windll.kernel32.MapViewOfFile
    MapViewOfFile.argtypes = (
        wintypes.HANDLE,  # hFileMappingObject
        wintypes.DWORD,  # dwDesiredAccess
        wintypes.DWORD,  # dwFileOffsetHigh
        wintypes.DWORD,  # dwFileOffsetLow
        wintypes.DWORD,  # dwNumberOfBytesToMap
    )
    MapViewOfFile.restype = wintypes.LPVOID

    UnmapViewOfFile = windll.kernel32.UnmapViewOfFile
    UnmapViewOfFile.argtypes = (
        wintypes.LPCVOID,  # lpBaseAddress
    )
    UnmapViewOfFile.restype = wintypes.BOOL

    GetFileSizeEx = windll.kernel32.GetFileSizeEx
    GetFileSizeEx.argtypes = (
        wintypes.HANDLE,  # hFile
        wintypes.PLARGE_INTEGER,  # lpFileSize
    )

    CheckSumMappedFile = windll.imagehlp.CheckSumMappedFile
    CheckSumMappedFile.argtypes = (
        wintypes.LPVOID,  # BaseAddress
        wintypes.DWORD,  # FileLength
        wintypes.PDWORD,  # HeaderSum
        wintypes.PDWORD,  # CheckSum
    )
    CheckSumMappedFile.restype = wintypes.LPVOID

    # Open file
    hFile = CreateFileW(
        ctypes.c_wchar_p(exe_path),
        0x80000000,  # dwDesiredAccess = GENERIC_READ
        0x00000001 | 0x00000002,  # dwShareMode = FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,  # lpSecurityAttributes = NULL
        3,  # dwCreationDisposition = OPEN_EXISTING
        0x80,  # dwFlagsAndAttributes = FILE_ATTRIBUTE_NORMAL
        None  # hTemplateFile = NULL
    )
    if hFile == INVALID_HANDLE:
        err = GetLastError()
        raise RuntimeError(f"Failed to open file {exe_path}! Error code: {err}")

    # Query file size
    fileLength = wintypes.LARGE_INTEGER(0)
    if GetFileSizeEx(hFile, fileLength) == 0:
        err = GetLastError()
        CloseHandle(hFile)
        raise RuntimeError(f"Failed to query file size file! Error code: {err}")
    fileLength = fileLength.value
    if fileLength > (2**32 - 1):
        raise RuntimeError("Executable size exceeds maximum allowed executable size on Windows (4 GiB)!")

    # Map the file
    hMapping = CreateFileMappingW(
        hFile,
        None,  # lpFileMappingAttributes = NULL
        0x02,  # flProtect = PAGE_READONLY
        0,  # dwMaximumSizeHigh = 0
        0,  # dwMaximumSizeLow = 0
        None  # lpName = NULL
    )
    if not hMapping:
        err = GetLastError()
        CloseHandle(hFile)
        raise RuntimeError(f"Failed to map file! Error code: {err}")

    # Create map view
    baseAddress = MapViewOfFile(
        hMapping,
        4,  # dwDesiredAccess = FILE_MAP_READ
        0,  # dwFileOffsetHigh = 0
        0,  # dwFileOffsetLow = 0
        0  # dwNumberOfBytesToMap = 0
    )
    if baseAddress == 0:
        err = GetLastError()
        CloseHandle(hMapping)
        CloseHandle(hFile)
        raise RuntimeError(f"Failed to create map view! Error code: {err}")

    # Finally, compute the checksum
    headerSum = wintypes.DWORD(0)
    checkSum = wintypes.DWORD(0)
    ret = CheckSumMappedFile(baseAddress, fileLength, ctypes.byref(headerSum), ctypes.byref(checkSum))
    if ret is None:
        err = GetLastError()

    # Cleanup
    UnmapViewOfFile(baseAddress)
    CloseHandle(hMapping)
    CloseHandle(hFile)

    if ret is None:
        raise RuntimeError(f"CheckSumMappedFile failed! Error code: {err}")

    return checkSum.value
