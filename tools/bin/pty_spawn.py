#!/usr/bin/env python3

import os
import sys
import pty


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


status = pty.spawn(sys.argv[1:])
exitcode = waitstatus_to_exitcode(status)
sys.exit(exitcode)
