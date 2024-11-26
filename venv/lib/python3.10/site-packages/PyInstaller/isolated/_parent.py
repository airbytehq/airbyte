# -----------------------------------------------------------------------------
# Copyright (c) 2021-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) or, at the user's discretion, the MIT License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception OR MIT)
# -----------------------------------------------------------------------------

import os
from pathlib import Path
from marshal import loads, dumps
from base64 import b64encode, b64decode
import functools
import subprocess
import sys

from PyInstaller import compat
from PyInstaller import log as logging

logger = logging.getLogger(__name__)

# WinAPI bindings for Windows-specific codepath
if os.name == "nt":
    import msvcrt
    import ctypes
    import ctypes.wintypes

    # CreatePipe
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [
            ("nLength", ctypes.wintypes.DWORD),
            ("lpSecurityDescriptor", ctypes.wintypes.LPVOID),
            ("bInheritHandle", ctypes.wintypes.BOOL),
        ]

    HANDLE_FLAG_INHERIT = 0x0001

    LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)

    CreatePipe = ctypes.windll.kernel32.CreatePipe
    CreatePipe.argtypes = [
        ctypes.POINTER(ctypes.wintypes.HANDLE),
        ctypes.POINTER(ctypes.wintypes.HANDLE),
        LPSECURITY_ATTRIBUTES,
        ctypes.wintypes.DWORD,
    ]
    CreatePipe.restype = ctypes.wintypes.BOOL

    # CloseHandle
    CloseHandle = ctypes.windll.kernel32.CloseHandle
    CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
    CloseHandle.restype = ctypes.wintypes.BOOL

CHILD_PY = Path(__file__).with_name("_child.py")


def create_pipe(read_handle_inheritable, write_handle_inheritable):
    """
    Create a one-way pipe for sending data to child processes.

    Args:
        read_handle_inheritable:
            A boolean flag indicating whether the handle corresponding to the read end-point of the pipe should be
            marked as inheritable by subprocesses.
        write_handle_inheritable:
            A boolean flag indicating whether the handle corresponding to the write end-point of the pipe should be
            marked as inheritable by subprocesses.

    Returns:
        A read/write pair of file descriptors (which are just integers) on posix or system file handles on Windows.

    The pipe may be used either by this process or subprocesses of this process but not globally.
    """
    return _create_pipe_impl(read_handle_inheritable, write_handle_inheritable)


def close_pipe_endpoint(pipe_handle):
    """
    Close the file descriptor (posix) or handle (Windows) belonging to a pipe.
    """
    return _close_pipe_endpoint_impl(pipe_handle)


if os.name == "nt":

    def _create_pipe_impl(read_handle_inheritable, write_handle_inheritable):
        # Use WinAPI CreatePipe function to create the pipe. Python's os.pipe() does the same, but wraps the resulting
        # handles into inheritable file descriptors (https://github.com/python/cpython/issues/77046). Instead, we want
        # just handles, and will set the inheritable flag on corresponding handle ourselves.
        read_handle = ctypes.wintypes.HANDLE()
        write_handle = ctypes.wintypes.HANDLE()

        # SECURITY_ATTRIBUTES with inherit handle set to True
        security_attributes = SECURITY_ATTRIBUTES()
        security_attributes.nLength = ctypes.sizeof(security_attributes)
        security_attributes.bInheritHandle = True
        security_attributes.lpSecurityDescriptor = None

        # CreatePipe()
        succeeded = CreatePipe(
            ctypes.byref(read_handle),  # hReadPipe
            ctypes.byref(write_handle),  # hWritePipe
            ctypes.byref(security_attributes),  # lpPipeAttributes
            0,  # nSize
        )
        if not succeeded:
            raise ctypes.WinError()

        # Set inheritable flags. Instead of binding and using SetHandleInformation WinAPI function, we can use
        # os.set_handle_inheritable().
        os.set_handle_inheritable(read_handle.value, read_handle_inheritable)
        os.set_handle_inheritable(write_handle.value, write_handle_inheritable)

        return read_handle.value, write_handle.value

    def _close_pipe_endpoint_impl(pipe_handle):
        succeeded = CloseHandle(pipe_handle)
        if not succeeded:
            raise ctypes.WinError()
else:

    def _create_pipe_impl(read_fd_inheritable, write_fd_inheritable):
        # Create pipe, using os.pipe()
        read_fd, write_fd = os.pipe()

        # The default behaviour of pipes is that they are process specific. I.e., they can only be used by this
        # process to talk to itself. Setting inheritable flags means that child processes may also use these pipes.
        os.set_inheritable(read_fd, read_fd_inheritable)
        os.set_inheritable(write_fd, write_fd_inheritable)

        return read_fd, write_fd

    def _close_pipe_endpoint_impl(pipe_fd):
        os.close(pipe_fd)


def child(read_from_parent: int, write_to_parent: int):
    """
    Spawn a Python subprocess sending it the two file descriptors it needs to talk back to this parent process.
    """
    if os.name != 'nt':
        # Explicitly disabling close_fds is a requirement for making file descriptors inheritable by child processes.
        extra_kwargs = {
            "env": _subprocess_env(),
            "close_fds": False,
        }
    else:
        # On Windows, we can use subprocess.STARTUPINFO to explicitly pass the list of file handles to be inherited,
        # so we can avoid disabling close_fds
        extra_kwargs = {
            "env": _subprocess_env(),
            "close_fds": True,
            "startupinfo": subprocess.STARTUPINFO(lpAttributeList={"handle_list": [read_from_parent, write_to_parent]})
        }

    # Run the _child.py script directly passing it the two file descriptors it needs to talk back to the parent.
    cmd, options = compat.__wrap_python([str(CHILD_PY), str(read_from_parent), str(write_to_parent)], extra_kwargs)

    # I'm intentionally leaving stdout and stderr alone so that print() can still be used for emergency debugging and
    # unhandled errors in the child are still visible.
    return subprocess.Popen(cmd, **options)


def _subprocess_env():
    """
    Define the environment variables to be readable in a child process.
    """
    from PyInstaller.config import CONF
    python_path = CONF["pathex"]
    if "PYTHONPATH" in os.environ:
        python_path = python_path + [os.environ["PYTHONPATH"]]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(python_path)
    return env


class SubprocessDiedError(RuntimeError):
    pass


class Python:
    """
    Start and connect to a separate Python subprocess.

    This is the lowest level of public API provided by this module. The advantage of using this class directly is
    that it allows multiple functions to be evaluated in a single subprocess, making it faster than multiple calls to
    :func:`call`.

    The ``strict_mode`` argument controls behavior when the child process fails to shut down; if strict mode is enabled,
    an error is raised, otherwise only warning is logged. If the value of ``strict_mode`` is ``None``, the value of
    ``PyInstaller.compat.strict_collect_mode`` is used (which in turn is controlled by the
    ``PYINSTALLER_STRICT_COLLECT_MODE`` environment variable.

    Examples:
        To call some predefined functions ``x = foo()``, ``y = bar("numpy")`` and ``z = bazz(some_flag=True)`` all using
        the same isolated subprocess use::

            with isolated.Python() as child:
                x = child.call(foo)
                y = child.call(bar, "numpy")
                z = child.call(bazz, some_flag=True)

    """
    def __init__(self, strict_mode=None):
        self._child = None

        # Re-use the compat.strict_collect_mode and its PYINSTALLER_STRICT_COLLECT_MODE environment variable for
        # default strict-mode setting.
        self._strict_mode = strict_mode if strict_mode is not None else compat.strict_collect_mode

    def __enter__(self):
        # We need two pipes. One for the child to send data to the parent. The (write) end-point passed to the
        # child needs to be marked as inheritable.
        read_from_child, write_to_parent = create_pipe(False, True)
        # And one for the parent to send data to the child. The (read) end-point passed to the child needs to be
        # marked as inheritable.
        read_from_parent, write_to_child = create_pipe(True, False)

        # Spawn a Python subprocess sending it the two file descriptors it needs to talk back to this parent process.
        self._child = child(read_from_parent, write_to_parent)

        # Close the end-points that were inherited by the child.
        close_pipe_endpoint(read_from_parent)
        close_pipe_endpoint(write_to_parent)
        del read_from_parent
        del write_to_parent

        # Open file handles to talk to the child. This should fully transfer ownership of the underlying file
        # descriptor to the opened handle; so when we close the latter, the former should be closed as well.
        if os.name == 'nt':
            # On Windows, we must first open file descriptor on top of the handle using _open_osfhandle (which
            # python wraps in msvcrt.open_osfhandle). According to MSDN, this transfers the ownership of the
            # underlying file handle to the file descriptors; i.e., they are both closed when the file descriptor
            # is closed).
            self._write_handle = os.fdopen(msvcrt.open_osfhandle(write_to_child, 0), "wb")
            self._read_handle = os.fdopen(msvcrt.open_osfhandle(read_from_child, 0), "rb")
        else:
            self._write_handle = os.fdopen(write_to_child, "wb")
            self._read_handle = os.fdopen(read_from_child, "rb")

        self._send(sys.path)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, SubprocessDiedError):
            self._write_handle.close()
            self._read_handle.close()
            del self._read_handle, self._write_handle
            self._child = None
            return
        # Send the signal (a blank line) to the child to tell it that it's time to stop.
        self._write_handle.write(b"\n")
        self._write_handle.flush()

        # Wait for the child process to exit. The timeout is necessary for corner cases when the sub-process fails to
        # exit (such as due to dangling non-daemon threads; see #7290). At this point, the subprocess already did all
        # its work, so it should be safe to terminate. And as we expect it to shut down quickly (or not at all), the
        # timeout is relatively short.
        #
        # In strict build mode, we raise an error when the subprocess fails to exit on its own, but do so only after
        # we attempt to kill the subprocess, to avoid leaving zombie processes.
        shutdown_error = False

        try:
            self._child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Timed out while waiting for the child process to exit!")
            shutdown_error = True
            self._child.kill()
            try:
                self._child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                logger.warning("Timed out while waiting for the child process to be killed!")
                # Give up and fall through

        # Close the handles. This should also close the underlying file descriptors.
        self._write_handle.close()
        self._read_handle.close()
        del self._read_handle, self._write_handle

        self._child = None

        # Raise an error in strict mode, after all clean-up has been performed.
        if shutdown_error and self._strict_mode:
            raise RuntimeError("Timed out while waiting for the child process to exit!")

    def call(self, function, *args, **kwargs):
        """
        Call a function in the child Python. Retrieve its return value. Usage of this method is identical to that
        of the :func:`call` function.
        """
        if self._child is None:
            raise RuntimeError("An isolated.Python object must be used in a 'with' clause.")

        self._send(function.__code__, function.__defaults__, function.__kwdefaults__, args, kwargs)

        # Read a single line of output back from the child. This contains if the function worked and either its return
        # value or a traceback. This will block indefinitely until it receives a '\n' byte.
        try:
            ok, output = loads(b64decode(self._read_handle.readline()))
        except (EOFError, BrokenPipeError):
            # Subprocess appears to have died in an unhandleable way (e.g. SIGSEV). Raise an error.
            raise SubprocessDiedError(
                f"Child process died calling {function.__name__}() with args={args} and "
                f"kwargs={kwargs}. Its exit code was {self._child.wait()}."
            ) from None

        # If all went well, then ``output`` is the return value.
        if ok:
            return output

        # Otherwise an error happened and ``output`` is a string-ified stacktrace. Raise an error appending the
        # stacktrace. Having the output in this order gives a nice fluent transition from parent to child in the stack
        # trace.
        raise RuntimeError(f"Child process call to {function.__name__}() failed with:\n" + output)

    def _send(self, *objects):
        for object in objects:
            self._write_handle.write(b64encode(dumps(object)))
            self._write_handle.write(b"\n")
        # Flushing is very important. Without it, the data is not sent but forever sits in a buffer so that the child is
        # forever waiting for its data and the parent in turn is forever waiting for the child's response.
        self._write_handle.flush()


def call(function, *args, **kwargs):
    r"""
    Call a function with arguments in a separate child Python. Retrieve its return value.

    Args:
        function:
            The function to send and invoke.
        *args:
        **kwargs:
            Positional and keyword arguments to send to the function. These must be simple builtin types - not custom
            classes.
    Returns:
        The return value of the function. Again, these must be basic types serialisable by :func:`marshal.dumps`.
    Raises:
        RuntimeError:
            Any exception which happens inside an isolated process is caught and reraised in the parent process.

    To use, define a function which returns the information you're looking for. Any imports it requires must happen in
    the body of the function. For example, to safely check the output of ``matplotlib.get_data_path()`` use::

        # Define a function to be ran in isolation.
        def get_matplotlib_data_path():
            import matplotlib
            return matplotlib.get_data_path()

        # Call it with isolated.call().
        get_matplotlib_data_path = isolated.call(matplotlib_data_path)

    For single use functions taking no arguments like the above you can abuse the decorator syntax slightly to define
    and execute a function in one go. ::

        >>> @isolated.call
        ... def matplotlib_data_dir():
        ...     import matplotlib
        ...     return matplotlib.get_data_path()
        >>> matplotlib_data_dir
        '/home/brenainn/.pyenv/versions/3.9.6/lib/python3.9/site-packages/matplotlib/mpl-data'

    Functions may take positional and keyword arguments and return most generic Python data types. ::

        >>> def echo_parameters(*args, **kwargs):
        ...     return args, kwargs
        >>> isolated.call(echo_parameters, 1, 2, 3)
        (1, 2, 3), {}
        >>> isolated.call(echo_parameters, foo=["bar"])
        (), {'foo': ['bar']}

    Notes:
        To make a function behave differently if it's isolated, check for the ``__isolated__`` global. ::

            if globals().get("__isolated__", False):
                # We're inside a child process.
                ...
            else:
                # This is the master process.
                ...

    """
    with Python() as isolated:
        return isolated.call(function, *args, **kwargs)


def decorate(function):
    """
    Decorate a function so that it is always called in an isolated subprocess.

    Examples:

        To use, write a function then prepend ``@isolated.decorate``. ::

            @isolated.decorate
            def add_1(x):
                '''Add 1 to ``x``, displaying the current process ID.'''
                import os
                print(f"Process {os.getpid()}: Adding 1 to {x}.")
                return x + 1

        The resultant ``add_1()`` function can now be called as you would a
        normal function and it'll automatically use a subprocess.

            >>> add_1(4)
            Process 4920: Adding 1 to 4.
            5
            >>> add_1(13.2)
            Process 4928: Adding 1 to 13.2.
            14.2

    """
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        return call(function, *args, **kwargs)

    return wrapped
