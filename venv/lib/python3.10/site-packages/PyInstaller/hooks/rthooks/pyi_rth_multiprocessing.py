#-----------------------------------------------------------------------------
# Copyright (c) 2017-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------


def _pyi_rthook():
    import os
    import sys

    import threading
    import multiprocessing
    import multiprocessing.spawn

    from subprocess import _args_from_interpreter_flags

    # Prevent `spawn` from trying to read `__main__` in from the main script
    multiprocessing.process.ORIGINAL_DIR = None

    def _freeze_support():
        # We want to catch the two processes that are spawned by the multiprocessing code:
        # - the semaphore tracker, which cleans up named semaphores in the `spawn` multiprocessing mode
        # - the fork server, which keeps track of worker processes in the `forkserver` mode.
        # Both of these processes are started by spawning a new copy of the running executable, passing it the flags
        # from `_args_from_interpreter_flags` and then "-c" and an import statement.
        # Look for those flags and the import statement, then `exec()` the code ourselves.

        if (
            len(sys.argv) >= 2 and sys.argv[-2] == '-c' and sys.argv[-1].startswith(
                ('from multiprocessing.resource_tracker import main', 'from multiprocessing.forkserver import main')
            ) and set(sys.argv[1:-2]) == set(_args_from_interpreter_flags())
        ):
            exec(sys.argv[-1])
            sys.exit()

        if multiprocessing.spawn.is_forking(sys.argv):
            kwds = {}
            for arg in sys.argv[2:]:
                name, value = arg.split('=')
                if value == 'None':
                    kwds[name] = None
                else:
                    kwds[name] = int(value)
            multiprocessing.spawn.spawn_main(**kwds)
            sys.exit()

    multiprocessing.freeze_support = multiprocessing.spawn.freeze_support = _freeze_support

    # Bootloader clears the `_MEIPASS2` environment variable, which allows a PyInstaller-frozen executable to run a
    # different PyInstaller-frozen executable. However, in the case of `multiprocessing`, we are actually trying
    # to run the same executable, so we need to restore `_MEIPASS2` to prevent onefile executable from unpacking
    # again in a different directory.
    #
    # This is needed for `spawn` start method (default on Windows and macOS) and also with `forkserver` start method
    # (available on Linux and macOS). It is not needed for `fork` start method (default on Linux and other Unix OSes),
    # because fork copies the parent process instead of starting it from scratch.

    # Mix-in to re-set _MEIPASS2 from sys._MEIPASS.
    class FrozenSupportMixIn:
        _lock = threading.Lock()

        def __init__(self, *args, **kw):
            # The whole code block needs be executed under a lock to prevent race conditions between `os.putenv` and
            # `os.unsetenv` calls when processes are spawned concurrently from multiple threads. See #7410.
            with self._lock:
                # We have to set original _MEIPASS2 value from sys._MEIPASS to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)  # @UndefinedVariable
                try:
                    super().__init__(*args, **kw)
                finally:
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not available. In those cases we cannot delete the
                    # variable but only set it to the empty string. The bootloader can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    if sys.platform.startswith('win'):
        # Windows; patch `Popen` for `spawn` start method
        from multiprocessing import popen_spawn_win32

        class _SpawnPopen(FrozenSupportMixIn, popen_spawn_win32.Popen):
            pass

        popen_spawn_win32.Popen = _SpawnPopen
    else:
        # UNIX OSes; patch `Popen` for `spawn` and `forkserver` start methods
        from multiprocessing import popen_spawn_posix
        from multiprocessing import popen_forkserver

        class _SpawnPopen(FrozenSupportMixIn, popen_spawn_posix.Popen):
            pass

        class _ForkserverPopen(FrozenSupportMixIn, popen_forkserver.Popen):
            pass

        popen_spawn_posix.Popen = _SpawnPopen
        popen_forkserver.Popen = _ForkserverPopen


_pyi_rthook()
del _pyi_rthook
