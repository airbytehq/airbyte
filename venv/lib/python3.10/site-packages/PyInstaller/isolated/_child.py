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
"""
The child process to be invoked by IsolatedPython().

This file is to be run directly with pipe handles for reading from and writing to the parent process as command line
arguments.

"""

import sys
import os
import types
from marshal import loads, dumps
from base64 import b64encode, b64decode
from traceback import format_exception

if os.name == "nt":
    from msvcrt import open_osfhandle

    def _open(osf_handle, mode):
        # Convert system file handles to file descriptors before opening them.
        return open(open_osfhandle(osf_handle, 0), mode)
else:
    _open = open


def run_next_command(read_fh, write_fh):
    """
    Listen to **read_fh** for the next function to run. Write the result to **write_fh**.
    """

    # Check the first line of input. Receiving an empty line is the signal that there are no more tasks to be ran.
    first_line = read_fh.readline()
    if first_line == b"\n":
        # It's time to end this child process
        return False

    # There are 5 lines to read: The function's code, its default args, its default kwargs, its args, and its kwargs.
    code = loads(b64decode(first_line.strip()))
    _defaults = loads(b64decode(read_fh.readline().strip()))
    _kwdefaults = loads(b64decode(read_fh.readline().strip()))
    args = loads(b64decode(read_fh.readline().strip()))
    kwargs = loads(b64decode(read_fh.readline().strip()))

    try:
        # Define the global namespace available to the function.
        GLOBALS = {"__builtins__": __builtins__, "__isolated__": True}
        # Reconstruct the function.
        function = types.FunctionType(code, GLOBALS)
        function.__defaults__ = _defaults
        function.__kwdefaults__ = _kwdefaults

        # Run it.
        output = function(*args, **kwargs)

        # Verify that the output is serialise-able (i.e. no custom types or module or function references) here so that
        # it's caught if it fails.
        marshalled = dumps((True, output))

    except BaseException as ex:
        # An exception happened whilst either running the function or serialising its output. Send back a string
        # version of the traceback (unfortunately raw traceback objects are not marshal-able) and a boolean to say
        # that it failed.
        tb_lines = format_exception(type(ex), ex, ex.__traceback__)
        if tb_lines[0] == "Traceback (most recent call last):\n":
            # This particular line is distracting. Get rid of it.
            tb_lines = tb_lines[1:]
        marshalled = dumps((False, "".join(tb_lines).rstrip()))

    # Send the output (return value or traceback) back to the parent.
    write_fh.write(b64encode(marshalled))
    write_fh.write(b"\n")
    write_fh.flush()

    # Signal that an instruction was ran (successfully or otherwise).
    return True


if __name__ == '__main__':
    read_from_parent, write_to_parent = map(int, sys.argv[1:])

    with _open(read_from_parent, "rb") as read_fh:
        with _open(write_to_parent, "wb") as write_fh:
            sys.path = loads(b64decode(read_fh.readline()))

            # Keep receiving and running instructions until the parent sends the signal to stop.
            while run_next_command(read_fh, write_fh):
                pass
