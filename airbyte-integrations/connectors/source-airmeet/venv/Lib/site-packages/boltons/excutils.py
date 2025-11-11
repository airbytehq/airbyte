# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import traceback
import linecache
from collections import namedtuple

# TODO: last arg or first arg?  (last arg makes it harder to *args
#       into, but makes it more readable in the default exception
#       __repr__ output)
# TODO: Multiexception wrapper


__all__ = ['ExceptionCauseMixin']


class ExceptionCauseMixin(Exception):
    """
    A mixin class for wrapping an exception in another exception, or
    otherwise indicating an exception was caused by another exception.

    This is most useful in concurrent or failure-intolerant scenarios,
    where just because one operation failed, doesn't mean the remainder
    should be aborted, or that it's the appropriate time to raise
    exceptions.

    This is still a work in progress, but an example use case at the
    bottom of this module.

    NOTE: when inheriting, you will probably want to put the
    ExceptionCauseMixin first. Builtin exceptions are not good about
    calling super()
    """

    cause = None

    def __new__(cls, *args, **kw):
        cause = None
        if args and isinstance(args[0], Exception):
            cause, args = args[0], args[1:]
        ret = super().__new__(cls, *args, **kw)
        ret.cause = cause
        if cause is None:
            return ret
        root_cause = getattr(cause, 'root_cause', None)
        if root_cause is None:
            ret.root_cause = cause
        else:
            ret.root_cause = root_cause

        full_trace = getattr(cause, 'full_trace', None)
        if full_trace is not None:
            ret.full_trace = list(full_trace)
            ret._tb = list(cause._tb)
            ret._stack = list(cause._stack)
            return ret

        try:
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_type is None and exc_value is None:
                return ret
            if cause is exc_value or root_cause is exc_value:
                # handles when cause is the current exception or when
                # there are multiple wraps while handling the original
                # exception, but a cause was never provided
                ret._tb = _extract_from_tb(exc_tb)
                ret._stack = _extract_from_frame(exc_tb.tb_frame)
                ret.full_trace = ret._stack[:-1] + ret._tb
        finally:
            del exc_tb
        return ret

    def get_str(self):
        """
        Get formatted the formatted traceback and exception
        message. This function exists separately from __str__()
        because __str__() is somewhat specialized for the built-in
        traceback module's particular usage.
        """
        ret = []
        trace_str = self._get_trace_str()
        if trace_str:
            ret.extend(['Traceback (most recent call last):\n', trace_str])
        ret.append(self._get_exc_str())
        return ''.join(ret)

    def _get_message(self):
        args = getattr(self, 'args', [])
        if self.cause:
            args = args[1:]
        if args and args[0]:
            return args[0]
        return ''

    def _get_trace_str(self):
        if not self.cause:
            return super().__repr__()
        if self.full_trace:
            return ''.join(traceback.format_list(self.full_trace))
        return ''

    def _get_exc_str(self, incl_name=True):
        cause_str = _format_exc(self.root_cause)
        message = self._get_message()
        ret = []
        if incl_name:
            ret = [self.__class__.__name__, ': ']
        if message:
            ret.extend([message, ' (caused by ', cause_str, ')'])
        else:
            ret.extend([' caused by ', cause_str])
        return ''.join(ret)

    def __str__(self):
        if not self.cause:
            return super().__str__()
        trace_str = self._get_trace_str()
        ret = []
        if trace_str:
            message = self._get_message()
            if message:
                ret.extend([message, ' --- '])
            ret.extend(['Wrapped traceback (most recent call last):\n',
                        trace_str,
                        self._get_exc_str(incl_name=True)])
            return ''.join(ret)
        else:
            return self._get_exc_str(incl_name=False)


def _format_exc(exc, message=None):
    if message is None:
        message = exc
    exc_str = traceback._format_final_exc_line(exc.__class__.__name__, message)
    return exc_str.rstrip()


_BaseTBItem = namedtuple('_BaseTBItem', 'filename, lineno, name, line')


class _TBItem(_BaseTBItem):
    def __repr__(self):
        ret = super().__repr__()
        ret += ' <%r>' % self.frame_id
        return ret


class _DeferredLine:
    def __init__(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        module_globals = module_globals or {}
        self.module_globals = {k: v for k, v in module_globals.items()
                                    if k in ('__name__', '__loader__')}

    def __eq__(self, other):
        return (self.lineno, self.filename) == (other.lineno, other.filename)

    def __ne__(self, other):
        return (self.lineno, self.filename) != (other.lineno, other.filename)

    def __str__(self):
        if hasattr(self, '_line'):
            return self._line
        linecache.checkcache(self.filename)
        line = linecache.getline(self.filename,
                                 self.lineno,
                                 self.module_globals)
        if line:
            line = line.strip()
        else:
            line = None
        self._line = line
        return line

    def __repr__(self):
        return repr(str(self))

    def __len__(self):
        return len(str(self))

    def strip(self):
        return str(self).strip()


def _extract_from_frame(f=None, limit=None):
    ret = []
    if f is None:
        f = sys._getframe(1)  # cross-impl yadayada
    if limit is None:
        limit = getattr(sys, 'tracebacklimit', 1000)
    n = 0
    while f is not None and n < limit:
        filename = f.f_code.co_filename
        lineno = f.f_lineno
        name = f.f_code.co_name
        line = _DeferredLine(filename, lineno, f.f_globals)
        item = _TBItem(filename, lineno, name, line)
        item.frame_id = id(f)
        ret.append(item)
        f = f.f_back
        n += 1
    ret.reverse()
    return ret


def _extract_from_tb(tb, limit=None):
    ret = []
    if limit is None:
        limit = getattr(sys, 'tracebacklimit', 1000)
    n = 0
    while tb is not None and n < limit:
        filename = tb.tb_frame.f_code.co_filename
        lineno = tb.tb_lineno
        name = tb.tb_frame.f_code.co_name
        line = _DeferredLine(filename, lineno, tb.tb_frame.f_globals)
        item = _TBItem(filename, lineno, name, line)
        item.frame_id = id(tb.tb_frame)
        ret.append(item)
        tb = tb.tb_next
        n += 1
    return ret


# An Example/Prototest:


class MathError(ExceptionCauseMixin, ValueError):
    pass


def whoops_math():
    return 1/0


def math_lol(n=0):
    if n < 3:
        return math_lol(n=n+1)
    try:
        return whoops_math()
    except ZeroDivisionError as zde:
        exc = MathError(zde, 'ya done messed up')
        raise exc

def main():
    try:
        math_lol()
    except ValueError as me:
        exc = MathError(me, 'hi')
        raise exc


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import pdb;pdb.post_mortem()
        raise
