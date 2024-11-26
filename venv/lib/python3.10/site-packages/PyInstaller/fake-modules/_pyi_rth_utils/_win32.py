# -----------------------------------------------------------------------------
# Copyright (c) 2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
# -----------------------------------------------------------------------------

import ctypes
import ctypes.wintypes

# Constants from win32 headers
TOKEN_QUERY = 0x0008

TokenUser = 1  # from TOKEN_INFORMATION_CLASS enum

ERROR_INSUFFICIENT_BUFFER = 122

INVALID_HANDLE = -1

FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x00000100
FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000

SDDL_REVISION1 = 1

# Structures for ConvertSidToStringSidW
PSID = ctypes.wintypes.LPVOID


class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Sid", PSID),
        ("Attributes", ctypes.wintypes.DWORD),
    ]


class TOKEN_USER(ctypes.Structure):
    _fields_ = [
        ("User", SID_AND_ATTRIBUTES),
    ]


PTOKEN_USER = ctypes.POINTER(TOKEN_USER)

# SECURITY_ATTRIBUTES structure for CreateDirectoryW
PSECURITY_DESCRIPTOR = ctypes.wintypes.LPVOID


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", ctypes.wintypes.DWORD),
        ("lpSecurityDescriptor", PSECURITY_DESCRIPTOR),
        ("bInheritHandle", ctypes.wintypes.BOOL),
    ]


# win32 API functions, bound via ctypes.
# NOTE: we do not use ctypes.windll.<dll_name> to avoid modifying its (global) function prototypes, which might affect
# user's code.
advapi32 = ctypes.WinDLL("advapi32")
kernel32 = ctypes.WinDLL("kernel32")

advapi32.ConvertSidToStringSidW.restype = ctypes.wintypes.BOOL
advapi32.ConvertSidToStringSidW.argtypes = (
    PSID,  # [in] PSID Sid
    ctypes.POINTER(ctypes.wintypes.LPWSTR),  # [out] LPWSTR *StringSid
)

advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = ctypes.wintypes.BOOL
advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = (
    ctypes.wintypes.LPCWSTR,  # [in] LPCWSTR StringSecurityDescriptor
    ctypes.wintypes.DWORD,  # [in] DWORD StringSDRevision
    ctypes.POINTER(PSECURITY_DESCRIPTOR),  # [out] PSECURITY_DESCRIPTOR *SecurityDescriptor
    ctypes.wintypes.PULONG,  # [out] PULONG SecurityDescriptorSize
)

advapi32.GetTokenInformation.restype = ctypes.wintypes.BOOL
advapi32.GetTokenInformation.argtypes = (
    ctypes.wintypes.HANDLE,  # [in] HANDLE TokenHandle
    ctypes.c_int,  # [in] TOKEN_INFORMATION_CLASS TokenInformationClass
    ctypes.wintypes.LPVOID,  # [out, optional] LPVOID TokenInformation
    ctypes.wintypes.DWORD,  # [in] DWORD TokenInformationLength
    ctypes.wintypes.PDWORD,  # [out] PDWORD ReturnLength
)

kernel32.CloseHandle.restype = ctypes.wintypes.BOOL
kernel32.CloseHandle.argtypes = (
    ctypes.wintypes.HANDLE,  # [in] HANDLE hObject
)

kernel32.CreateDirectoryW.restype = ctypes.wintypes.BOOL
kernel32.CreateDirectoryW.argtypes = (
    ctypes.wintypes.LPCWSTR,  # [in] LPCWSTR lpPathName
    ctypes.POINTER(SECURITY_ATTRIBUTES),  # [in, optional] LPSECURITY_ATTRIBUTES lpSecurityAttributes
)

kernel32.FormatMessageW.restype = ctypes.wintypes.DWORD
kernel32.FormatMessageW.argtypes = (
    ctypes.wintypes.DWORD,  # [in] DWORD dwFlags
    ctypes.wintypes.LPCVOID,  # [in, optional] LPCVOID lpSource
    ctypes.wintypes.DWORD,  # [in] DWORD dwMessageId
    ctypes.wintypes.DWORD,  # [in] DWORD dwLanguageId
    ctypes.wintypes.LPWSTR,  # [out] LPWSTR lpBuffer
    ctypes.wintypes.DWORD,  # [in] DWORD nSize
    ctypes.wintypes.LPVOID,  # [in, optional] va_list *Arguments
)

kernel32.GetCurrentProcess.restype = ctypes.wintypes.HANDLE
# kernel32.GetCurrentProcess has no arguments

kernel32.GetLastError.restype = ctypes.wintypes.DWORD
# kernel32.GetLastError has no arguments

kernel32.LocalFree.restype = ctypes.wintypes.BOOL
kernel32.LocalFree.argtypes = (
    ctypes.wintypes.HLOCAL,  # [in] _Frees_ptr_opt_ HLOCAL hMem
)

kernel32.OpenProcessToken.restype = ctypes.wintypes.BOOL
kernel32.OpenProcessToken.argtypes = (
    ctypes.wintypes.HANDLE,  # [in] HANDLE ProcessHandle
    ctypes.wintypes.DWORD,  # [in] DWORD DesiredAccess
    ctypes.wintypes.PHANDLE,  # [out] PHANDLE TokenHandle
)


def _win_error_to_message(error_code):
    """
    Convert win32 error code to message.
    """
    message_wstr = ctypes.wintypes.LPWSTR(None)
    ret = kernel32.FormatMessageW(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
        None,  # lpSource
        error_code,  # dwMessageId
        0x400,  # dwLanguageId = MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT)
        ctypes.cast(
            ctypes.byref(message_wstr),
            ctypes.wintypes.LPWSTR,
        ),  # pointer to LPWSTR due to FORMAT_MESSAGE_ALLOCATE_BUFFER; needs to be cast to LPWSTR
        64,  # due to FORMAT_MESSAGE_ALLOCATE_BUFFER, this is minimum number of characters to allocate
        None,
    )
    if ret == 0:
        return None

    message = message_wstr.value
    kernel32.LocalFree(message_wstr)

    # Strip trailing CR/LF.
    if message:
        message = message.strip()
    return message


def _get_user_sid():
    """
    Obtain the SID for the current user.
    """
    process_token = ctypes.wintypes.HANDLE(INVALID_HANDLE)

    try:
        # Get access token for the current process
        ret = kernel32.OpenProcessToken(
            kernel32.GetCurrentProcess(),
            TOKEN_QUERY,
            ctypes.pointer(process_token),
        )
        if ret == 0:
            error_code = kernel32.GetLastError()
            raise RuntimeError(f"Failed to open process token! Error code: 0x{error_code:X}")

        # Query buffer size for user info structure
        user_info_size = ctypes.wintypes.DWORD(0)

        ret = advapi32.GetTokenInformation(
            process_token,
            TokenUser,
            None,
            0,
            ctypes.byref(user_info_size),
        )

        # We expect this call to fail with ERROR_INSUFFICIENT_BUFFER
        if ret == 0:
            error_code = kernel32.GetLastError()
            if error_code != ERROR_INSUFFICIENT_BUFFER:
                raise RuntimeError(f"Failed to query token information buffer size! Error code: 0x{error_code:X}")
        else:
            raise RuntimeError("Unexpected return value from GetTokenInformation!")

        # Allocate buffer
        user_info = ctypes.create_string_buffer(user_info_size.value)
        ret = advapi32.GetTokenInformation(
            process_token,
            TokenUser,
            user_info,
            user_info_size,
            ctypes.byref(user_info_size),
        )
        if ret == 0:
            error_code = kernel32.GetLastError()
            raise RuntimeError(f"Failed to query token information! Error code: 0x{error_code:X}")

        # Convert SID to string
        # Technically, we need to pass user_info->User.Sid, but as they are at the beginning of the
        # buffer, just pass the buffer instead...
        sid_wstr = ctypes.wintypes.LPWSTR(None)
        ret = advapi32.ConvertSidToStringSidW(
            ctypes.cast(user_info, PTOKEN_USER).contents.User.Sid,
            ctypes.pointer(sid_wstr),
        )
        if ret == 0:
            error_code = kernel32.GetLastError()
            raise RuntimeError(f"Failed to convert SID to string! Error code: 0x{error_code:X}")
        sid = sid_wstr.value
        kernel32.LocalFree(sid_wstr)
    except Exception:
        sid = None
    finally:
        # Close the process token
        if process_token.value != INVALID_HANDLE:
            kernel32.CloseHandle(process_token)

    return sid


# Get and cache current user's SID
_user_sid = _get_user_sid()


def secure_mkdir(dir_name):
    """
    Replacement for mkdir that limits the access to created directory to current user.
    """

    # Create security descriptor
    # Prefer actual user SID over SID S-1-3-4 (current owner), because at the time of writing, Wine does not properly
    # support the latter.
    sid = _user_sid or "S-1-3-4"

    # DACL descriptor (D):
    # ace_type;ace_flags;rights;object_guid;inherit_object_guid;account_sid;(resource_attribute)
    # - ace_type = SDDL_ACCESS_ALLOWED (A)
    # - rights = SDDL_FILE_ALL (FA)
    # - account_sid = current user (queried SID)
    security_desc_str = f"D:(A;;FA;;;{sid})"
    security_desc = ctypes.wintypes.LPVOID(None)

    ret = advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
        security_desc_str,
        SDDL_REVISION1,
        ctypes.byref(security_desc),
        None,
    )
    if ret == 0:
        error_code = kernel32.GetLastError()
        raise RuntimeError(
            f"Failed to create security descriptor! Error code: 0x{error_code:X}, "
            f"message: {_win_error_to_message(error_code)}"
        )

    security_attr = SECURITY_ATTRIBUTES()
    security_attr.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
    security_attr.lpSecurityDescriptor = security_desc
    security_attr.bInheritHandle = False

    # Create directory
    ret = kernel32.CreateDirectoryW(
        dir_name,
        security_attr,
    )
    if ret == 0:
        # Call failed; store error code immediately, to avoid it being overwritten in cleanup below.
        error_code = kernel32.GetLastError()

    # Free security descriptor
    kernel32.LocalFree(security_desc)

    # Exit on succeess
    if ret != 0:
        return

    # Construct OSError from win error code
    error_message = _win_error_to_message(error_code)

    # Strip trailing dot to match error message from os.mkdir().
    if error_message and error_message[-1] == '.':
        error_message = error_message[:-1]

    raise OSError(
        None,  # errno
        error_message,  # strerror
        dir_name,  # filename
        error_code,  # winerror
        None,  # filename2
    )
