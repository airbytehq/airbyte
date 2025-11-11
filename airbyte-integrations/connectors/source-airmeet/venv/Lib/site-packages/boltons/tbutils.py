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

"""One of the oft-cited tenets of Python is that it is better to ask
forgiveness than permission. That is, there are many cases where it is
more inclusive and correct to handle exceptions than spend extra lines
and execution time checking for conditions. This philosophy makes good
exception handling features all the more important. Unfortunately
Python's :mod:`traceback` module is woefully behind the times.

The ``tbutils`` module provides two disparate but complementary featuresets:

  1. With :class:`ExceptionInfo` and :class:`TracebackInfo`, the
     ability to extract, construct, manipulate, format, and serialize
     exceptions, tracebacks, and callstacks.
  2. With :class:`ParsedException`, the ability to find and parse tracebacks
     from captured output such as logs and stdout.

There is also the :class:`ContextualTracebackInfo` variant of
:class:`TracebackInfo`, which includes much more information from each
frame of the callstack, including values of locals and neighboring
lines of code.
"""


import re
import sys
import linecache


# TODO: chaining primitives?  what are real use cases where these help?

# TODO: print_* for backwards compatibility
# __all__ = ['extract_stack', 'extract_tb', 'format_exception',
#            'format_exception_only', 'format_list', 'format_stack',
#            'format_tb', 'print_exc', 'format_exc', 'print_exception',
#            'print_last', 'print_stack', 'print_tb']


__all__ = ['ExceptionInfo', 'TracebackInfo', 'Callpoint',
           'ContextualExceptionInfo', 'ContextualTracebackInfo',
           'ContextualCallpoint', 'print_exception', 'ParsedException']


class Callpoint:
    """The Callpoint is a lightweight object used to represent a single
    entry in the code of a call stack. It stores the code-related
    metadata of a given frame. Available attributes are the same as
    the parameters below.

    Args:
        func_name (str): the function name
        lineno (int): the line number
        module_name (str): the module name
        module_path (str): the filesystem path of the module
        lasti (int): the index of bytecode execution
        line (str): the single-line code content (if available)

    """
    __slots__ = ('func_name', 'lineno', 'module_name', 'module_path', 'lasti',
                 'line')

    def __init__(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = lineno
        self.module_name = module_name
        self.module_path = module_path
        self.lasti = lasti
        self.line = line

    def to_dict(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    @classmethod
    def from_current(cls, level=1):
        "Creates a Callpoint from the location of the calling function."
        frame = sys._getframe(level)
        return cls.from_frame(frame)

    @classmethod
    def from_frame(cls, frame):
        "Create a Callpoint object from data extracted from the given frame."
        func_name = frame.f_code.co_name
        lineno = frame.f_lineno
        module_name = frame.f_globals.get('__name__', '')
        module_path = frame.f_code.co_filename
        lasti = frame.f_lasti
        line = _DeferredLine(module_path, lineno, frame.f_globals)
        return cls(module_name, module_path, func_name,
                   lineno, lasti, line=line)

    @classmethod
    def from_tb(cls, tb):
        """Create a Callpoint from the traceback of the current
        exception. Main difference with :meth:`from_frame` is that
        ``lineno`` and ``lasti`` come from the traceback, which is to
        say the line that failed in the try block, not the line
        currently being executed (in the except block).
        """
        func_name = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        lasti = tb.tb_lasti
        module_name = tb.tb_frame.f_globals.get('__name__', '')
        module_path = tb.tb_frame.f_code.co_filename
        line = _DeferredLine(module_path, lineno, tb.tb_frame.f_globals)
        return cls(module_name, module_path, func_name,
                   lineno, lasti, line=line)

    def __repr__(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def tb_frame_str(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret


class _DeferredLine:
    """The _DeferredLine type allows Callpoints and TracebackInfos to be
    constructed without potentially hitting the filesystem, as is the
    normal behavior of the standard Python :mod:`traceback` and
    :mod:`linecache` modules. Calling :func:`str` fetches and caches
    the line.

    Args:
        filename (str): the path of the file containing the line
        lineno (int): the number of the line in question
        module_globals (dict): an optional dict of module globals,
            used to handle advanced use cases using custom module loaders.

    """
    __slots__ = ('filename', 'lineno', '_line', '_mod_name', '_mod_loader')

    def __init__(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__loader__')

    def __eq__(self, other):
        return (self.lineno, self.filename) == (other.lineno, other.filename)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def __repr__(self):
        return repr(str(self))

    def __len__(self):
        return len(str(self))


# TODO: dedup frames, look at __eq__ on _DeferredLine
class TracebackInfo:
    """The TracebackInfo class provides a basic representation of a stack
    trace, be it from an exception being handled or just part of
    normal execution. It is basically a wrapper around a list of
    :class:`Callpoint` objects representing frames.

    Args:
        frames (list): A list of frame objects in the stack.

    .. note ::

      ``TracebackInfo`` can represent both exception tracebacks and
      non-exception tracebacks (aka stack traces). As a result, there
      is no ``TracebackInfo.from_current()``, as that would be
      ambiguous. Instead, call :meth:`TracebackInfo.from_frame`
      without the *frame* argument for a stack trace, or
      :meth:`TracebackInfo.from_traceback` without the *tb* argument
      for an exception traceback.
    """
    callpoint_type = Callpoint

    def __init__(self, frames):
        self.frames = frames

    @classmethod
    def from_frame(cls, frame=None, level=1, limit=None):
        """Create a new TracebackInfo *frame* by recurring up in the stack a
        max of *limit* times. If *frame* is unset, get the frame from
        :func:`sys._getframe` using *level*.

        Args:
            frame (types.FrameType): frame object from
                :func:`sys._getframe` or elsewhere. Defaults to result
                of :func:`sys.get_frame`.
            level (int): If *frame* is unset, the desired frame is
                this many levels up the stack from the invocation of
                this method. Default ``1`` (i.e., caller of this method).
            limit (int): max number of parent frames to extract
                (defaults to :data:`sys.tracebacklimit`)

        """
        ret = []
        if frame is None:
            frame = sys._getframe(level)
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', 1000)
        n = 0
        while frame is not None and n < limit:
            item = cls.callpoint_type.from_frame(frame)
            ret.append(item)
            frame = frame.f_back
            n += 1
        ret.reverse()
        return cls(ret)

    @classmethod
    def from_traceback(cls, tb=None, limit=None):
        """Create a new TracebackInfo from the traceback *tb* by recurring
        up in the stack a max of *limit* times. If *tb* is unset, get
        the traceback from the currently handled exception. If no
        exception is being handled, raise a :exc:`ValueError`.

        Args:

            frame (types.TracebackType): traceback object from
                :func:`sys.exc_info` or elsewhere. If absent or set to
                ``None``, defaults to ``sys.exc_info()[2]``, and
                raises a :exc:`ValueError` if no exception is
                currently being handled.
            limit (int): max number of parent frames to extract
                (defaults to :data:`sys.tracebacklimit`)

        """
        ret = []
        if tb is None:
            tb = sys.exc_info()[2]
            if tb is None:
                raise ValueError('no tb set and no exception being handled')
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', 1000)
        n = 0
        while tb is not None and n < limit:
            item = cls.callpoint_type.from_tb(tb)
            ret.append(item)
            tb = tb.tb_next
            n += 1
        return cls(ret)

    @classmethod
    def from_dict(cls, d):
        "Complements :meth:`TracebackInfo.to_dict`."
        # TODO: check this.
        return cls(d['frames'])

    def to_dict(self):
        """Returns a dict with a list of :class:`Callpoint` frames converted
        to dicts.
        """
        return {'frames': [f.to_dict() for f in self.frames]}

    def __len__(self):
        return len(self.frames)

    def __iter__(self):
        return iter(self.frames)

    def __repr__(self):
        cn = self.__class__.__name__

        if self.frames:
            frame_part = f' last={self.frames[-1]!r}'
        else:
            frame_part = ''

        return f'<{cn} frames={len(self.frames)}{frame_part}>'

    def __str__(self):
        return self.get_formatted()

    def get_formatted(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'Traceback (most recent call last):\n'
        ret += ''.join([f.tb_frame_str() for f in self.frames])
        return ret


class ExceptionInfo:
    """An ExceptionInfo object ties together three main fields suitable
    for representing an instance of an exception: The exception type
    name, a string representation of the exception itself (the
    exception message), and information about the traceback (stored as
    a :class:`TracebackInfo` object).

    These fields line up with :func:`sys.exc_info`, but unlike the
    values returned by that function, ExceptionInfo does not hold any
    references to the real exception or traceback. This property makes
    it suitable for serialization or long-term retention, without
    worrying about formatting pitfalls, circular references, or leaking memory.

    Args:

        exc_type (str): The exception type name.
        exc_msg (str): String representation of the exception value.
        tb_info (TracebackInfo): Information about the stack trace of the
            exception.

    Like the :class:`TracebackInfo`, ExceptionInfo is most commonly
    instantiated from one of its classmethods: :meth:`from_exc_info`
    or :meth:`from_current`.
    """

    #: Override this in inherited types to control the TracebackInfo type used
    tb_info_type = TracebackInfo

    def __init__(self, exc_type, exc_msg, tb_info):
        # TODO: additional fields for SyntaxErrors
        self.exc_type = exc_type
        self.exc_msg = exc_msg
        self.tb_info = tb_info

    @classmethod
    def from_exc_info(cls, exc_type, exc_value, traceback):
        """Create an :class:`ExceptionInfo` object from the exception's type,
        value, and traceback, as returned by :func:`sys.exc_info`. See
        also :meth:`from_current`.
        """
        type_str = exc_type.__name__
        type_mod = exc_type.__module__
        if type_mod not in ("__main__", "__builtin__", "exceptions", "builtins"):
            type_str = f'{type_mod}.{type_str}'
        val_str = _some_str(exc_value)
        tb_info = cls.tb_info_type.from_traceback(traceback)
        return cls(type_str, val_str, tb_info)

    @classmethod
    def from_current(cls):
        """Create an :class:`ExceptionInfo` object from the current exception
        being handled, by way of :func:`sys.exc_info`. Will raise an
        exception if no exception is currently being handled.
        """
        return cls.from_exc_info(*sys.exc_info())

    def to_dict(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'exc_tb': self.tb_info.to_dict()}

    def __repr__(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def get_formatted(self):
        """Returns a string formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_exception`.
        """
        # TODO: add SyntaxError formatting
        tb_str = self.tb_info.get_formatted()
        return ''.join([tb_str, f'{self.exc_type}: {self.exc_msg}'])

    def get_formatted_exception_only(self):
        return f'{self.exc_type}: {self.exc_msg}'


class ContextualCallpoint(Callpoint):
    """The ContextualCallpoint is a :class:`Callpoint` subtype with the
    exact same API and storing two additional values:

      1. :func:`repr` outputs for local variables from the Callpoint's scope
      2. A number of lines before and after the Callpoint's line of code

    The ContextualCallpoint is used by the :class:`ContextualTracebackInfo`.
    """
    def __init__(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)

    @classmethod
    def from_frame(cls, frame):
        "Identical to :meth:`Callpoint.from_frame`"
        ret = super().from_frame(frame)
        ret._populate_local_reprs(frame.f_locals)
        ret._populate_context_lines()
        return ret

    @classmethod
    def from_tb(cls, tb):
        "Identical to :meth:`Callpoint.from_tb`"
        ret = super().from_tb(tb)
        ret._populate_local_reprs(tb.tb_frame.f_locals)
        ret._populate_context_lines()
        return ret

    def _populate_context_lines(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def _populate_local_reprs(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = '<unprintable %s object>' % type(v).__name__
                local_reprs[k] = surrogate
        return

    def to_dict(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret


class ContextualTracebackInfo(TracebackInfo):
    """The ContextualTracebackInfo type is a :class:`TracebackInfo`
    subtype that is used by :class:`ContextualExceptionInfo` and uses
    the :class:`ContextualCallpoint` as its frame-representing
    primitive.
    """
    callpoint_type = ContextualCallpoint


class ContextualExceptionInfo(ExceptionInfo):
    """The ContextualTracebackInfo type is a :class:`TracebackInfo`
    subtype that uses the :class:`ContextualCallpoint` as its
    frame-representing primitive.

    It carries with it most of the exception information required to
    recreate the widely recognizable "500" page for debugging Django
    applications.
    """
    tb_info_type = ContextualTracebackInfo


# TODO: clean up & reimplement -- specifically for syntax errors
def format_exception_only(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: use asciify, improved if necessary
def _some_str(value):
    try:
        return str(value)
    except Exception:
        pass
    return '<unprintable %s object>' % type(value).__name__


def _format_final_exc_line(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def print_exception(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def fix_print_exception():
    """
    Sets the default exception hook :func:`sys.excepthook` to the
    :func:`tbutils.print_exception` that uses all the ``tbutils``
    facilities to provide a consistent output behavior.
    """
    sys.excepthook = print_exception


_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)'
                       r', in (?P<funcname>.+)$')
_se_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)')
_underline_re = re.compile(r'^[~^ ]*$')

# TODO: ParsedException generator over large bodies of text

class ParsedException:
    """Stores a parsed traceback and exception as would be typically
    output by :func:`sys.excepthook` or
    :func:`traceback.print_exception`.

    .. note:

       Does not currently store SyntaxError details such as column.

    """
    def __init__(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = exc_msg
        self.frames = list(frames or [])

    @property
    def source_file(self):
        """
        The file path of module containing the function that raised the
        exception, or None if not available.
        """
        try:
            return self.frames[-1]['filepath']
        except IndexError:
            return None

    def to_dict(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(self.frames)}

    def __repr__(self):
        cn = self.__class__.__name__
        return ('%s(%r, %r, frames=%r)'
                % (cn, self.exc_type, self.exc_msg, self.frames))

    def to_string(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    @classmethod
    def from_string(cls, tb_str):
        """Parse a traceback and exception from the text *tb_str*. This text
        is expected to have been decoded, otherwise it will be
        interpreted as UTF-8.

        This method does not search a larger body of text for
        tracebacks. If the first line of the text passed does not
        match one of the known patterns, a :exc:`ValueError` will be
        raised. This method will ignore trailing text after the end of
        the first traceback.

        Args:
            tb_str (str): The traceback text (:class:`unicode` or UTF-8 bytes)
        """
        if not isinstance(tb_str, str):
            tb_str = tb_str.decode('utf-8')
        tb_lines = tb_str.lstrip().splitlines()

        # First off, handle some ignored exceptions. These can be the
        # result of exceptions raised by __del__ during garbage
        # collection
        while tb_lines:
            cl = tb_lines[-1]
            if cl.startswith('Exception ') and cl.endswith('ignored'):
                tb_lines.pop()
            else:
                break
        if tb_lines and tb_lines[0].strip() == 'Traceback (most recent call last):':
            start_line = 1
            frame_re = _frame_re
        elif len(tb_lines) > 1 and tb_lines[-2].lstrip().startswith('^'):
            # This is to handle the slight formatting difference
            # associated with SyntaxErrors, which also don't really
            # have tracebacks
            start_line = 0
            frame_re = _se_frame_re
        else:
            raise ValueError('unrecognized traceback string format')

        frames = []
        line_no = start_line
        while True:
            frame_line = tb_lines[line_no].strip()
            frame_match = frame_re.match(frame_line)
            if frame_match:
                frame_dict = frame_match.groupdict()
                try:
                    next_line = tb_lines[line_no + 1]
                except IndexError:
                    # We read what we could
                    next_line = ''
                next_line_stripped = next_line.strip()
                if (
                        frame_re.match(next_line_stripped) or
                        # The exception message will not be indented
                        # This check is to avoid overrunning on eval-like
                        # tracebacks where the last frame doesn't have source
                        # code in the traceback
                        not next_line.startswith(' ')
                ):
                    frame_dict['source_line'] = ''
                else:
                    frame_dict['source_line'] = next_line_stripped
                    line_no += 1
                if _underline_re.match(tb_lines[line_no + 1]):
                  # To deal with anchors
                  line_no += 1
            else:
                break
            line_no += 1
            frames.append(frame_dict)

        try:
            exc_line = '\n'.join(tb_lines[line_no:])
            exc_type, _, exc_msg = exc_line.partition(': ')
        except Exception:
            exc_type, exc_msg = '', ''

        return cls(exc_type, exc_msg, frames)


ParsedTB = ParsedException  # legacy alias
