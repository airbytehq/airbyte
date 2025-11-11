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

"""
A small set of utilities useful for debugging misbehaving
applications. Currently this focuses on ways to use :mod:`pdb`, the
built-in Python debugger.
"""

import sys
import time
from reprlib import Repr

try:
    from .typeutils import make_sentinel
    _UNSET = make_sentinel(var_name='_UNSET')
except ImportError:
    _UNSET = object()

__all__ = ['pdb_on_signal', 'pdb_on_exception', 'wrap_trace']


def pdb_on_signal(signalnum=None):
    """Installs a signal handler for *signalnum*, which defaults to
    ``SIGINT``, or keyboard interrupt/ctrl-c. This signal handler
    launches a :mod:`pdb` breakpoint. Results vary in concurrent
    systems, but this technique can be useful for debugging infinite
    loops, or easily getting into deep call stacks.

    Args:
        signalnum (int): The signal number of the signal to handle
            with pdb. Defaults to :mod:`signal.SIGINT`, see
            :mod:`signal` for more information.
    """
    import pdb
    import signal
    if not signalnum:
        signalnum = signal.SIGINT

    old_handler = signal.getsignal(signalnum)

    def pdb_int_handler(sig, frame):
        signal.signal(signalnum, old_handler)
        pdb.set_trace()
        pdb_on_signal(signalnum)  # use 'u' to find your code and 'h' for help

    signal.signal(signalnum, pdb_int_handler)
    return


def pdb_on_exception(limit=100):
    """Installs a handler which, instead of exiting, attaches a
    post-mortem pdb console whenever an unhandled exception is
    encountered.

    Args:
        limit (int): the max number of stack frames to display when
            printing the traceback

    A similar effect can be achieved from the command-line using the
    following command::

      python -m pdb your_code.py

    But ``pdb_on_exception`` allows you to do this conditionally and within
    your application. To restore default behavior, just do::

      sys.excepthook = sys.__excepthook__
    """
    import pdb
    import sys
    import traceback

    def pdb_excepthook(exc_type, exc_val, exc_tb):
        traceback.print_tb(exc_tb, limit=limit)
        pdb.post_mortem(exc_tb)

    sys.excepthook = pdb_excepthook
    return

_repr_obj = Repr()
_repr_obj.maxstring = 50
_repr_obj.maxother = 50
brief_repr = _repr_obj.repr


# events: call, return, get, set, del, raise
def trace_print_hook(event, label, obj, attr_name,
                     args=(), kwargs={}, result=_UNSET):
    fargs = (event.ljust(6), time.time(), label.rjust(10),
             obj.__class__.__name__, attr_name)
    if event == 'get':
        tmpl = '%s %s - %s - %s.%s -> %s'
        fargs += (brief_repr(result),)
    elif event == 'set':
        tmpl = '%s %s - %s - %s.%s = %s'
        fargs += (brief_repr(args[0]),)
    elif event == 'del':
        tmpl = '%s %s - %s - %s.%s'
    else:  # call/return/raise
        tmpl = '%s %s - %s - %s.%s(%s)'
        fargs += (', '.join([brief_repr(a) for a in args]),)
        if kwargs:
            tmpl = '%s %s - %s - %s.%s(%s, %s)'
            fargs += (', '.join([f'{k}={brief_repr(v)}'
                                 for k, v in kwargs.items()]),)
        if result is not _UNSET:
            tmpl += ' -> %s'
            fargs += (brief_repr(result),)
    print(tmpl % fargs)
    return


def wrap_trace(obj, hook=trace_print_hook,
               which=None, events=None, label=None):
    """Monitor an object for interactions. Whenever code calls a method,
    gets an attribute, or sets an attribute, an event is called. By
    default the trace output is printed, but a custom tracing *hook*
    can be passed.

    Args:
       obj (object): New- or old-style object to be traced. Built-in
           objects like lists and dicts also supported.
       hook (callable): A function called once for every event. See
           below for details.
       which (str): One or more attribute names to trace, or a
           function accepting attribute name and value, and returning
           True/False.
       events (str): One or more kinds of events to call *hook*
           on. Expected values are ``['get', 'set', 'del', 'call',
           'raise', 'return']``. Defaults to all events.
       label (str): A name to associate with the traced object
           Defaults to hexadecimal memory address, similar to repr.

    The object returned is not the same object as the one passed
    in. It will not pass identity checks. However, it will pass
    :func:`isinstance` checks, as it is a new instance of a new
    subtype of the object passed.

    """
    # other actions: pdb.set_trace, print, aggregate, aggregate_return
    # (like aggregate but with the return value)

    # TODO: test classmethod/staticmethod/property
    # TODO: wrap __dict__ for old-style classes?

    if isinstance(which, str):
        which_func = lambda attr_name, attr_val: attr_name == which
    elif callable(getattr(which, '__contains__', None)):
        which_func = lambda attr_name, attr_val: attr_name in which
    elif which is None or callable(which):
        which_func = which
    else:
        raise TypeError('expected attr name(s) or callable, not: %r' % which)

    label = label or hex(id(obj))

    if isinstance(events, str):
        events = [events]
    do_get = not events or 'get' in events
    do_set = not events or 'set' in events
    do_del = not events or 'del' in events
    do_call = not events or 'call' in events
    do_raise = not events or 'raise' in events
    do_return = not events or 'return' in events

    def wrap_method(attr_name, func, _hook=hook, _label=label):
        def wrapped(*a, **kw):
            a = a[1:]
            if do_call:
                hook(event='call', label=_label, obj=obj,
                     attr_name=attr_name, args=a, kwargs=kw)
            if do_raise:
                try:
                    ret = func(*a, **kw)
                except Exception:
                    if not hook(event='raise', label=_label, obj=obj,
                                attr_name=attr_name, args=a, kwargs=kw,
                                result=sys.exc_info()):
                        raise
            else:
                ret = func(*a, **kw)
            if do_return:
                hook(event='return', label=_label, obj=obj,
                     attr_name=attr_name, args=a, kwargs=kw, result=ret)
            return ret

        wrapped.__name__ = func.__name__
        wrapped.__doc__ = func.__doc__
        try:
            wrapped.__module__ = func.__module__
        except Exception:
            pass
        try:
            if func.__dict__:
                wrapped.__dict__.update(func.__dict__)
        except Exception:
            pass
        return wrapped

    def __getattribute__(self, attr_name):
        ret = type(obj).__getattribute__(obj, attr_name)
        if callable(ret):  # wrap any bound methods
            ret = type(obj).__getattribute__(self, attr_name)
        if do_get:
            hook('get', label, obj, attr_name, (), {}, result=ret)
        return ret

    def __setattr__(self, attr_name, value):
        type(obj).__setattr__(obj, attr_name, value)
        if do_set:
            hook('set', label, obj, attr_name, (value,), {})
        return

    def __delattr__(self, attr_name):
        type(obj).__delattr__(obj, attr_name)
        if do_del:
            hook('del', label, obj, attr_name, (), {})
        return

    attrs = {}
    for attr_name in dir(obj):
        try:
            attr_val = getattr(obj, attr_name)
        except Exception:
            continue

        if not callable(attr_val) or attr_name in ('__new__',):
            continue
        elif which_func and not which_func(attr_name, attr_val):
            continue

        if attr_name == '__getattribute__':
            wrapped_method = __getattribute__
        elif attr_name == '__setattr__':
            wrapped_method = __setattr__
        elif attr_name == '__delattr__':
            wrapped_method = __delattr__
        else:
            wrapped_method = wrap_method(attr_name, attr_val)
        attrs[attr_name] = wrapped_method

    cls_name = obj.__class__.__name__
    if cls_name == cls_name.lower():
        type_name = 'traced_' + cls_name
    else:
        type_name = 'Traced' + cls_name

    if hasattr(obj, '__mro__'):
        bases = (obj.__class__,)
    else:
        # need new-style class for even basic wrapping of callables to
        # work. getattribute won't work for old-style classes of course.
        bases = (obj.__class__, object)

    trace_type = type(type_name, bases, attrs)
    for cls in trace_type.__mro__:
        try:
            return cls.__new__(trace_type)
        except Exception:
            pass
    raise TypeError('unable to wrap_trace %r instance %r'
                    % (obj.__class__, obj))


