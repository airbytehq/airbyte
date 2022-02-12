#!/usr/bin/env python3

import os
import sys
import pty
from select import select


def waitstatus_to_exitcode(status):
    """
    https://github.com/python/cpython/blob/e0bc8ee945af96f9395659bbe3cc30b082e7a361/Modules/posixmodule.c#L14658-L14748
    """

    if os.WIFEXITED(status):
        exitcode = os.WEXITSTATUS(status)
        if exitcode < 0: raise ValueError("invalid WEXITSTATUS: %i" % exitcode)
        return exitcode
    elif os.WIFSIGNALED(status):
        signum = os.WTERMSIG(status)
        if signum <= 0: raise ValueError("invalid WTERMSIG: %i" % signum)
        return -signum
    elif os.WIFSTOPPED(status):
        raise ValueError("process stopped by delivery of signal %i" % os.WSTOPSIG(status))
    else:
        raise ValueError("invalid wait status: %i" % status)


def _writen(fd, data):
    """Write all the data to a descriptor."""
    while data:
        n = os.write(fd, data)
        data = data[n:]


def _read(fd):
    """Default read function."""
    return os.read(fd, 1024)


def _copy(master_fd, master_read=_read, stdin_read=_read):
    """Parent copy loop.
    Copies
            pty master -> standard output   (master_read)
            standard input -> pty master    (stdin_read)"""
    fds = [master_fd, pty.STDIN_FILENO]
    while True:
        rfds, wfds, xfds = select(fds, [], [], 120)
        if master_fd in rfds:
            data = master_read(master_fd)
            if not data:  # Reached EOF.
                fds.remove(master_fd)
            else:
                os.write(pty.STDOUT_FILENO, data)
        if pty.STDIN_FILENO in rfds:
            data = stdin_read(pty.STDIN_FILENO)
            if not data:
                fds.remove(pty.STDIN_FILENO)
            else:
                _writen(master_fd, data)
        if not rfds:
            os.write(pty.STDOUT_FILENO, b"timeout" + b"." * 2000 + b"\r\n")

def spawn(argv, master_read=_read, stdin_read=_read):
    """Create a spawned process."""
    if type(argv) == type(''):
        argv = (argv,)
    pid, master_fd = pty.fork()
    if pid == pty.CHILD:
        os.execlp(argv[0], *argv)
    try:
        mode = pty.tty.tcgetattr(pty.STDIN_FILENO)
        pty.tty.setraw(pty.STDIN_FILENO)
        restore = 1
    except pty.tty.error:    # This is the same as termios.error
        restore = 0
    try:
        _copy(master_fd, master_read, stdin_read)
    except OSError:
        if restore:
            pty.tty.tcsetattr(pty.STDIN_FILENO, pty.tty.TCSAFLUSH, mode)

    os.close(master_fd)
    return os.waitpid(pid, 0)[1]


status = spawn(sys.argv[1:])
exitcode = waitstatus_to_exitcode(status)
sys.exit(exitcode)
