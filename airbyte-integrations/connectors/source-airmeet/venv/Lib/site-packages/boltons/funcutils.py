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

"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function
support. ``funcutils`` generally stays in the same vein, adding to and
correcting Python's standard metaprogramming facilities.
"""

import sys
import re
import inspect
import functools
import itertools
from inspect import formatannotation
from types import FunctionType, MethodType

# For legacy compatibility.
# boltons used to offer an implementation of total_ordering for Python <2.7
from functools import total_ordering as total_ordering

try:
    from .typeutils import make_sentinel
    NO_DEFAULT = make_sentinel(var_name='NO_DEFAULT')
except ImportError:
    NO_DEFAULT = object()


def inspect_formatargspec(
        args, varargs=None, varkw=None, defaults=None,
        kwonlyargs=(), kwonlydefaults={}, annotations={},
        formatarg=str,
        formatvarargs=lambda name: '*' + name,
        formatvarkw=lambda name: '**' + name,
        formatvalue=lambda value: '=' + repr(value),
        formatreturns=lambda text: ' -> ' + text,
        formatannotation=formatannotation):
    """Copy formatargspec from python 3.7 standard library.
    Python 3 has deprecated formatargspec and requested that Signature
    be used instead, however this requires a full reimplementation
    of formatargspec() in terms of creating Parameter objects and such.
    Instead of introducing all the object-creation overhead and having
    to reinvent from scratch, just copy their compatibility routine.
    """

    def formatargandannotation(arg):
        result = formatarg(arg)
        if arg in annotations:
            result += ': ' + formatannotation(annotations[arg])
        return result
    specs = []
    if defaults:
        firstdefault = len(args) - len(defaults)
    for i, arg in enumerate(args):
        spec = formatargandannotation(arg)
        if defaults and i >= firstdefault:
            spec = spec + formatvalue(defaults[i - firstdefault])
        specs.append(spec)
    if varargs is not None:
        specs.append(formatvarargs(formatargandannotation(varargs)))
    else:
        if kwonlyargs:
            specs.append('*')
    if kwonlyargs:
        for kwonlyarg in kwonlyargs:
            spec = formatargandannotation(kwonlyarg)
            if kwonlydefaults and kwonlyarg in kwonlydefaults:
                spec += formatvalue(kwonlydefaults[kwonlyarg])
            specs.append(spec)
    if varkw is not None:
        specs.append(formatvarkw(formatargandannotation(varkw)))
    result = '(' + ', '.join(specs) + ')'
    if 'return' in annotations:
        result += formatreturns(formatannotation(annotations['return']))
    return result


def get_module_callables(mod, ignore=None):
    """Returns two maps of (*types*, *funcs*) from *mod*, optionally
    ignoring based on the :class:`bool` return value of the *ignore*
    callable. *mod* can be a string name of a module in
    :data:`sys.modules` or the module instance itself.
    """
    if isinstance(mod, str):
        mod = sys.modules[mod]
    types, funcs = {}, {}
    for attr_name in dir(mod):
        if ignore and ignore(attr_name):
            continue
        try:
            attr = getattr(mod, attr_name)
        except Exception:
            continue
        try:
            attr_mod_name = attr.__module__
        except AttributeError:
            continue
        if attr_mod_name != mod.__name__:
            continue
        if isinstance(attr, type):
            types[attr_name] = attr
        elif callable(attr):
            funcs[attr_name] = attr
    return types, funcs


def mro_items(type_obj):
    """Takes a type and returns an iterator over all class variables
    throughout the type hierarchy (respecting the MRO).

    >>> sorted(set([k for k, v in mro_items(int) if not k.startswith('__') and 'bytes' not in k and not callable(v)]))
    ['denominator', 'imag', 'numerator', 'real']
    """
    # TODO: handle slots?
    return itertools.chain.from_iterable(ct.__dict__.items()
                                         for ct in type_obj.__mro__)


def dir_dict(obj, raise_exc=False):
    """Return a dictionary of attribute names to values for a given
    object. Unlike ``obj.__dict__``, this function returns all
    attributes on the object, including ones on parent classes.
    """
    # TODO: separate function for handling descriptors on types?
    ret = {}
    for k in dir(obj):
        try:
            ret[k] = getattr(obj, k)
        except Exception:
            if raise_exc:
                raise
    return ret


def copy_function(orig, copy_dict=True):
    """Returns a shallow copy of the function, including code object,
    globals, closure, etc.

    >>> func = lambda: func
    >>> func() is func
    True
    >>> func_copy = copy_function(func)
    >>> func_copy() is func
    True
    >>> func_copy is not func
    True

    Args:
        orig (function): The function to be copied. Must be a
            function, not just any method or callable.
        copy_dict (bool): Also copy any attributes set on the function
            instance. Defaults to ``True``.
    """
    ret = FunctionType(orig.__code__,
                       orig.__globals__,
                       name=orig.__name__,
                       argdefs=getattr(orig, "__defaults__", None),
                       closure=getattr(orig, "__closure__", None))
    if hasattr(orig, "__kwdefaults__"):
        ret.__kwdefaults__ = orig.__kwdefaults__
    if copy_dict:
        ret.__dict__.update(orig.__dict__)
    return ret


def partial_ordering(cls):
    """Class decorator, similar to :func:`functools.total_ordering`,
    except it is used to define `partial orderings`_ (i.e., it is
    possible that *x* is neither greater than, equal to, or less than
    *y*). It assumes the presence of the ``__le__()`` and ``__ge__()``
    method, but nothing else. It will not override any existing
    additional comparison methods.

    .. _partial orderings: https://en.wikipedia.org/wiki/Partially_ordered_set

    >>> @partial_ordering
    ... class MySet(set):
    ...     def __le__(self, other):
    ...         return self.issubset(other)
    ...     def __ge__(self, other):
    ...         return self.issuperset(other)
    ...
    >>> a = MySet([1,2,3])
    >>> b = MySet([1,2])
    >>> c = MySet([1,2,4])
    >>> b < a
    True
    >>> b > a
    False
    >>> b < c
    True
    >>> a < c
    False
    >>> c > a
    False
    """
    def __lt__(self, other): return self <= other and not self >= other
    def __gt__(self, other): return self >= other and not self <= other
    def __eq__(self, other): return self >= other and self <= other

    if not hasattr(cls, '__lt__'): cls.__lt__ = __lt__
    if not hasattr(cls, '__gt__'): cls.__gt__ = __gt__
    if not hasattr(cls, '__eq__'): cls.__eq__ = __eq__

    return cls


class InstancePartial(functools.partial):
    """:class:`functools.partial` is a huge convenience for anyone
    working with Python's great first-class functions. It allows
    developers to curry arguments and incrementally create simpler
    callables for a variety of use cases.

    Unfortunately there's one big gap in its usefulness:
    methods. Partials just don't get bound as methods and
    automatically handed a reference to ``self``. The
    ``InstancePartial`` type remedies this by inheriting from
    :class:`functools.partial` and implementing the necessary
    descriptor protocol. There are no other differences in
    implementation or usage. :class:`CachedInstancePartial`, below,
    has the same ability, but is slightly more efficient.

    """
    @property
    def _partialmethod(self):
        # py3.13 switched from _partialmethod to __partialmethod__, this is kept for backwards compat <=py3.12
        return self.__partialmethod__
    
    @property
    def __partialmethod__(self):
        return functools.partialmethod(self.func, *self.args, **self.keywords)

    def __get__(self, obj, obj_type):
        return MethodType(self, obj)



class CachedInstancePartial(functools.partial):
    """The ``CachedInstancePartial`` is virtually the same as
    :class:`InstancePartial`, adding support for method-usage to
    :class:`functools.partial`, except that upon first access, it
    caches the bound method on the associated object, speeding it up
    for future accesses, and bringing the method call overhead to
    about the same as non-``partial`` methods.

    See the :class:`InstancePartial` docstring for more details.
    """
    @property
    def _partialmethod(self):
        # py3.13 switched from _partialmethod to __partialmethod__, this is kept for backwards compat <=py3.12
        return self.__partialmethod__
    
    @property
    def __partialmethod__(self):
        return functools.partialmethod(self.func, *self.args, **self.keywords)

    def __set_name__(self, obj_type, name):
        self.__name__ = name

    def __get__(self, obj, obj_type):
        # These assignments could've been in __init__, but there was
        # no simple way to do it without breaking one of PyPy or Py3.
        self.__name__ = getattr(self, "__name__", None)
        self.__doc__ = self.func.__doc__
        self.__module__ = self.func.__module__

        name = self.__name__

        if obj is None:
            return MethodType(self, obj)
        try:
            # since this is a data descriptor, this block
            # is probably only hit once (per object)
            return obj.__dict__[name]
        except KeyError:
            obj.__dict__[name] = ret = MethodType(self, obj)
            return ret


partial = CachedInstancePartial


def format_invocation(name='', args=(), kwargs=None, **kw):
    """Given a name, positional arguments, and keyword arguments, format
    a basic Python-style function call.

    >>> print(format_invocation('func', args=(1, 2), kwargs={'c': 3}))
    func(1, 2, c=3)
    >>> print(format_invocation('a_func', args=(1,)))
    a_func(1)
    >>> print(format_invocation('kw_func', kwargs=[('a', 1), ('b', 2)]))
    kw_func(a=1, b=2)

    """
    _repr = kw.pop('repr', repr)
    if kw:
        raise TypeError('unexpected keyword args: %r' % ', '.join(kw.keys()))
    kwargs = kwargs or {}
    a_text = ', '.join([_repr(a) for a in args])
    if isinstance(kwargs, dict):
        kwarg_items = [(k, kwargs[k]) for k in sorted(kwargs)]
    else:
        kwarg_items = kwargs
    kw_text = ', '.join([f'{k}={_repr(v)}' for k, v in kwarg_items])

    all_args_text = a_text
    if all_args_text and kw_text:
        all_args_text += ', '
    all_args_text += kw_text

    return f'{name}({all_args_text})'


def format_exp_repr(obj, pos_names, req_names=None, opt_names=None, opt_key=None):
    """Render an expression-style repr of an object, based on attribute
    names, which are assumed to line up with arguments to an initializer.

    >>> class Flag(object):
    ...    def __init__(self, length, width, depth=None):
    ...        self.length = length
    ...        self.width = width
    ...        self.depth = depth
    ...

    That's our Flag object, here are some example reprs for it:

    >>> flag = Flag(5, 10)
    >>> print(format_exp_repr(flag, ['length', 'width'], [], ['depth']))
    Flag(5, 10)
    >>> flag2 = Flag(5, 15, 2)
    >>> print(format_exp_repr(flag2, ['length'], ['width', 'depth']))
    Flag(5, width=15, depth=2)

    By picking the pos_names, req_names, opt_names, and opt_key, you
    can fine-tune how you want the repr to look.

    Args:
       obj (object): The object whose type name will be used and
          attributes will be checked
       pos_names (list): Required list of attribute names which will be
          rendered as positional arguments in the output repr.
       req_names (list): List of attribute names which will always
          appear in the keyword arguments in the output repr. Defaults to None.
       opt_names (list): List of attribute names which may appear in
          the keyword arguments in the output repr, provided they pass
          the *opt_key* check. Defaults to None.
       opt_key (callable): A function or callable which checks whether
          an opt_name should be in the repr. Defaults to a
          ``None``-check.

    """
    cn = type(obj).__name__
    req_names = req_names or []
    opt_names = opt_names or []
    uniq_names, all_names = set(), []
    for name in req_names + opt_names:
        if name in uniq_names:
            continue
        uniq_names.add(name)
        all_names.append(name)

    if opt_key is None:
        opt_key = lambda v: v is None
    assert callable(opt_key)

    args = [getattr(obj, name, None) for name in pos_names]

    kw_items = [(name, getattr(obj, name, None)) for name in all_names]
    kw_items = [(name, val) for name, val in kw_items
                if not (name in opt_names and opt_key(val))]

    return format_invocation(cn, args, kw_items)


def format_nonexp_repr(obj, req_names=None, opt_names=None, opt_key=None):
    """Format a non-expression-style repr

    Some object reprs look like object instantiation, e.g., App(r=[], mw=[]).

    This makes sense for smaller, lower-level objects whose state
    roundtrips. But a lot of objects contain values that don't
    roundtrip, like types and functions.

    For those objects, there is the non-expression style repr, which
    mimic's Python's default style to make a repr like so:

    >>> class Flag(object):
    ...    def __init__(self, length, width, depth=None):
    ...        self.length = length
    ...        self.width = width
    ...        self.depth = depth
    ...
    >>> flag = Flag(5, 10)
    >>> print(format_nonexp_repr(flag, ['length', 'width'], ['depth']))
    <Flag length=5 width=10>

    If no attributes are specified or set, utilizes the id, not unlike Python's
    built-in behavior.

    >>> print(format_nonexp_repr(flag))
    <Flag id=...>
    """
    cn = obj.__class__.__name__
    req_names = req_names or []
    opt_names = opt_names or []
    uniq_names, all_names = set(), []
    for name in req_names + opt_names:
        if name in uniq_names:
            continue
        uniq_names.add(name)
        all_names.append(name)

    if opt_key is None:
        opt_key = lambda v: v is None
    assert callable(opt_key)

    items = [(name, getattr(obj, name, None)) for name in all_names]
    labels = [f'{name}={val!r}' for name, val in items
              if not (name in opt_names and opt_key(val))]
    if not labels:
        labels = ['id=%s' % id(obj)]
    ret = '<{} {}>'.format(cn, ' '.join(labels))
    return ret



# # #
# # # Function builder
# # #


def wraps(func, injected=None, expected=None, **kw):
    """Decorator factory to apply update_wrapper() to a wrapper function.

    Modeled after built-in :func:`functools.wraps`. Returns a decorator
    that invokes update_wrapper() with the decorated function as the wrapper
    argument and the arguments to wraps() as the remaining arguments.
    Default arguments are as for update_wrapper(). This is a convenience
    function to simplify applying partial() to update_wrapper().

    Same example as in update_wrapper's doc but with wraps:

        >>> from boltons.funcutils import wraps
        >>>
        >>> def print_return(func):
        ...     @wraps(func)
        ...     def wrapper(*args, **kwargs):
        ...         ret = func(*args, **kwargs)
        ...         print(ret)
        ...         return ret
        ...     return wrapper
        ...
        >>> @print_return
        ... def example():
        ...     '''docstring'''
        ...     return 'example return value'
        >>>
        >>> val = example()
        example return value
        >>> example.__name__
        'example'
        >>> example.__doc__
        'docstring'
    """
    return partial(update_wrapper, func=func, build_from=None,
                   injected=injected, expected=expected, **kw)


def update_wrapper(wrapper, func, injected=None, expected=None, build_from=None, **kw):
    """Modeled after the built-in :func:`functools.update_wrapper`,
    this function is used to make your wrapper function reflect the
    wrapped function's:

      * Name
      * Documentation
      * Module
      * Signature

    The built-in :func:`functools.update_wrapper` copies the first three, but
    does not copy the signature. This version of ``update_wrapper`` can copy
    the inner function's signature exactly, allowing seamless usage
    and :mod:`introspection <inspect>`. Usage is identical to the
    built-in version::

        >>> from boltons.funcutils import update_wrapper
        >>>
        >>> def print_return(func):
        ...     def wrapper(*args, **kwargs):
        ...         ret = func(*args, **kwargs)
        ...         print(ret)
        ...         return ret
        ...     return update_wrapper(wrapper, func)
        ...
        >>> @print_return
        ... def example():
        ...     '''docstring'''
        ...     return 'example return value'
        >>>
        >>> val = example()
        example return value
        >>> example.__name__
        'example'
        >>> example.__doc__
        'docstring'

    In addition, the boltons version of update_wrapper supports
    modifying the outer signature. By passing a list of
    *injected* argument names, those arguments will be removed from
    the outer wrapper's signature, allowing your decorator to provide
    arguments that aren't passed in.

    Args:

        wrapper (function) : The callable to which the attributes of
            *func* are to be copied.
        func (function): The callable whose attributes are to be copied.
        injected (list): An optional list of argument names which
            should not appear in the new wrapper's signature.
        expected (list): An optional list of argument names (or (name,
            default) pairs) representing new arguments introduced by
            the wrapper (the opposite of *injected*). See
            :meth:`FunctionBuilder.add_arg()` for more details.
        build_from (function): The callable from which the new wrapper
            is built. Defaults to *func*, unless *wrapper* is partial object
            built from *func*, in which case it defaults to *wrapper*.
            Useful in some specific cases where *wrapper* and *func* have the
            same arguments but differ on which are keyword-only and positional-only.
        update_dict (bool): Whether to copy other, non-standard
            attributes of *func* over to the wrapper. Defaults to True.
        inject_to_varkw (bool): Ignore missing arguments when a
            ``**kwargs``-type catch-all is present. Defaults to True.
        hide_wrapped (bool): Remove reference to the wrapped function(s)
            in the updated function.

    In opposition to the built-in :func:`functools.update_wrapper` bolton's
    version returns a copy of the function and does not modify anything in place.
    For more in-depth wrapping of functions, see the
    :class:`FunctionBuilder` type, on which update_wrapper was built.
    """
    if injected is None:
        injected = []
    elif isinstance(injected, str):
        injected = [injected]
    else:
        injected = list(injected)

    expected_items = _parse_wraps_expected(expected)

    if isinstance(func, (classmethod, staticmethod)):
        raise TypeError('wraps does not support wrapping classmethods and'
                        ' staticmethods, change the order of wrapping to'
                        ' wrap the underlying function: %r'
                        % (getattr(func, '__func__', None),))

    update_dict = kw.pop('update_dict', True)
    inject_to_varkw = kw.pop('inject_to_varkw', True)
    hide_wrapped = kw.pop('hide_wrapped', False)
    if kw:
        raise TypeError('unexpected kwargs: %r' % kw.keys())

    if isinstance(wrapper, functools.partial) and func is wrapper.func:
        build_from = build_from or wrapper

    fb = FunctionBuilder.from_func(build_from or func)

    for arg in injected:
        try:
            fb.remove_arg(arg)
        except MissingArgument:
            if inject_to_varkw and fb.varkw is not None:
                continue  # keyword arg will be caught by the varkw
            raise

    for arg, default in expected_items:
        fb.add_arg(arg, default)  # may raise ExistingArgument

    if fb.is_async:
        fb.body = 'return await _call(%s)' % fb.get_invocation_str()
    else:
        fb.body = 'return _call(%s)' % fb.get_invocation_str()

    execdict = dict(_call=wrapper, _func=func)
    fully_wrapped = fb.get_func(execdict, with_dict=update_dict)

    if hide_wrapped and hasattr(fully_wrapped, '__wrapped__'):
        del fully_wrapped.__dict__['__wrapped__']
    elif not hide_wrapped:
        fully_wrapped.__wrapped__ = func  # ref to the original function (#115)

    return fully_wrapped


def _parse_wraps_expected(expected):
    # expected takes a pretty powerful argument, it's processed
    # here. admittedly this would be less trouble if I relied on
    # OrderedDict (there's an impl of that in the commit history if
    # you look
    if expected is None:
        expected = []
    elif isinstance(expected, str):
        expected = [(expected, NO_DEFAULT)]

    expected_items = []
    try:
        expected_iter = iter(expected)
    except TypeError as e:
        raise ValueError('"expected" takes string name, sequence of string names,'
                         ' iterable of (name, default) pairs, or a mapping of '
                         ' {name: default}, not %r (got: %r)' % (expected, e))
    for argname in expected_iter:
        if isinstance(argname, str):
            # dict keys and bare strings
            try:
                default = expected[argname]
            except TypeError:
                default = NO_DEFAULT
        else:
            # pairs
            try:
                argname, default = argname
            except (TypeError, ValueError):
                raise ValueError('"expected" takes string name, sequence of string names,'
                                 ' iterable of (name, default) pairs, or a mapping of '
                                 ' {name: default}, not %r')
        if not isinstance(argname, str):
            raise ValueError(f'all "expected" argnames must be strings, not {argname!r}')

        expected_items.append((argname, default))

    return expected_items


class FunctionBuilder:
    """The FunctionBuilder type provides an interface for programmatically
    creating new functions, either based on existing functions or from
    scratch.

    Values are passed in at construction or set as attributes on the
    instance. For creating a new function based of an existing one,
    see the :meth:`~FunctionBuilder.from_func` classmethod. At any
    point, :meth:`~FunctionBuilder.get_func` can be called to get a
    newly compiled function, based on the values configured.

    >>> fb = FunctionBuilder('return_five', doc='returns the integer 5',
    ...                      body='return 5')
    >>> f = fb.get_func()
    >>> f()
    5
    >>> fb.varkw = 'kw'
    >>> f_kw = fb.get_func()
    >>> f_kw(ignored_arg='ignored_val')
    5

    Note that function signatures themselves changed quite a bit in
    Python 3, so several arguments are only applicable to
    FunctionBuilder in Python 3. Except for *name*, all arguments to
    the constructor are keyword arguments.

    Args:
        name (str): Name of the function.
        doc (str): `Docstring`_ for the function, defaults to empty.
        module (str): Name of the module from which this function was
            imported. Defaults to None.
        body (str): String version of the code representing the body
            of the function. Defaults to ``'pass'``, which will result
            in a function which does nothing and returns ``None``.
        args (list): List of argument names, defaults to empty list,
            denoting no arguments.
        varargs (str): Name of the catch-all variable for positional
            arguments. E.g., "args" if the resultant function is to have
            ``*args`` in the signature. Defaults to None.
        varkw (str): Name of the catch-all variable for keyword
            arguments. E.g., "kwargs" if the resultant function is to have
            ``**kwargs`` in the signature. Defaults to None.
        defaults (tuple): A tuple containing default argument values for
            those arguments that have defaults.
        kwonlyargs (list): Argument names which are only valid as
            keyword arguments. **Python 3 only.**
        kwonlydefaults (dict): A mapping, same as normal *defaults*,
            but only for the *kwonlyargs*. **Python 3 only.**
        annotations (dict): Mapping of type hints and so
            forth. **Python 3 only.**
        filename (str): The filename that will appear in
            tracebacks. Defaults to "boltons.funcutils.FunctionBuilder".
        indent (int): Number of spaces with which to indent the
            function *body*. Values less than 1 will result in an error.
        dict (dict): Any other attributes which should be added to the
            functions compiled with this FunctionBuilder.

    All of these arguments are also made available as attributes which
    can be mutated as necessary.

    .. _Docstring: https://en.wikipedia.org/wiki/Docstring#Python

    """

    _argspec_defaults = {'args': list,
                         'varargs': lambda: None,
                         'varkw': lambda: None,
                         'defaults': lambda: None,
                         'kwonlyargs': list,
                         'kwonlydefaults': dict,
                         'annotations': dict}

    @classmethod
    def _argspec_to_dict(cls, f):
        argspec = inspect.getfullargspec(f)
        return {attr: getattr(argspec, attr)
                    for attr in cls._argspec_defaults}

    _defaults = {'doc': str,
                 'dict': dict,
                 'is_async': lambda: False,
                 'module': lambda: None,
                 'body': lambda: 'pass',
                 'indent': lambda: 4,
                 "annotations": dict,
                 'filename': lambda: 'boltons.funcutils.FunctionBuilder'}

    _defaults.update(_argspec_defaults)

    _compile_count = itertools.count()

    def __init__(self, name, **kw):
        self.name = name
        for a, default_factory in self._defaults.items():
            val = kw.pop(a, None)
            if val is None:
                val = default_factory()
            setattr(self, a, val)

        if kw:
            raise TypeError('unexpected kwargs: %r' % kw.keys())
        return

    # def get_argspec(self):  # TODO

    def get_sig_str(self, with_annotations=True):
        """Return function signature as a string.

        with_annotations is ignored on Python 2.  On Python 3 signature
        will omit annotations if it is set to False.
        """
        if with_annotations:
            annotations = self.annotations
        else:
            annotations = {}

        return inspect_formatargspec(self.args,
                                     self.varargs,
                                     self.varkw,
                                     [],
                                     self.kwonlyargs,
                                     {},
                                     annotations)

    _KWONLY_MARKER = re.compile(r"""
    \*     # a star
    \s*    # followed by any amount of whitespace
    ,      # followed by a comma
    \s*    # followed by any amount of whitespace
    """, re.VERBOSE)

    def get_invocation_str(self):
        kwonly_pairs = None
        formatters = {}
        if self.kwonlyargs:
            kwonly_pairs = {arg: arg
                                for arg in self.kwonlyargs}
            formatters['formatvalue'] = lambda value: '=' + value

        sig = inspect_formatargspec(self.args,
                                    self.varargs,
                                    self.varkw,
                                    [],
                                    kwonly_pairs,
                                    kwonly_pairs,
                                    {},
                                    **formatters)
        sig = self._KWONLY_MARKER.sub('', sig)
        return sig[1:-1]

    @classmethod
    def from_func(cls, func):
        """Create a new FunctionBuilder instance based on an existing
        function. The original function will not be stored or
        modified.
        """
        # TODO: copy_body? gonna need a good signature regex.
        # TODO: might worry about __closure__?
        if not callable(func):
            raise TypeError(f'expected callable object, not {func!r}')

        if isinstance(func, functools.partial):
            kwargs = {'name': func.func.__name__,
                      'doc': func.func.__doc__,
                      'module': getattr(func.func, '__module__', None),  # e.g., method_descriptor
                      'annotations': getattr(func.func, "__annotations__", {}),
                      'dict': getattr(func.func, '__dict__', {})}
        else:
            kwargs = {'name': func.__name__,
                      'doc': func.__doc__,
                      'module': getattr(func, '__module__', None),  # e.g., method_descriptor
                      'annotations': getattr(func, "__annotations__", {}),
                      'dict': getattr(func, '__dict__', {})}

        kwargs.update(cls._argspec_to_dict(func))

        if inspect.iscoroutinefunction(func):
            kwargs['is_async'] = True

        return cls(**kwargs)

    def get_func(self, execdict=None, add_source=True, with_dict=True):
        """Compile and return a new function based on the current values of
        the FunctionBuilder.

        Args:
            execdict (dict): The dictionary representing the scope in
                which the compilation should take place. Defaults to an empty
                dict.
            add_source (bool): Whether to add the source used to a
                special ``__source__`` attribute on the resulting
                function. Defaults to True.
            with_dict (bool): Add any custom attributes, if
                applicable. Defaults to True.

        To see an example of usage, see the implementation of
        :func:`~boltons.funcutils.wraps`.
        """
        execdict = execdict or {}
        body = self.body or self._default_body

        tmpl = 'def {name}{sig_str}:'
        tmpl += '\n{body}'

        if self.is_async:
            tmpl = 'async ' + tmpl

        body = _indent(self.body, ' ' * self.indent)

        name = self.name.replace('<', '_').replace('>', '_')  # lambdas
        src = tmpl.format(name=name, sig_str=self.get_sig_str(with_annotations=False),
                          doc=self.doc, body=body)
        self._compile(src, execdict)
        func = execdict[name]

        func.__name__ = self.name
        func.__doc__ = self.doc
        func.__defaults__ = self.defaults
        func.__kwdefaults__ = self.kwonlydefaults
        func.__annotations__ = self.annotations

        if with_dict:
            func.__dict__.update(self.dict)
        func.__module__ = self.module
        # TODO: caller module fallback?

        if add_source:
            func.__source__ = src

        return func

    def get_defaults_dict(self):
        """Get a dictionary of function arguments with defaults and the
        respective values.
        """
        ret = dict(reversed(list(zip(reversed(self.args),
                                     reversed(self.defaults or [])))))
        kwonlydefaults = getattr(self, 'kwonlydefaults', None)
        if kwonlydefaults:
            ret.update(kwonlydefaults)
        return ret

    def get_arg_names(self, only_required=False):
        arg_names = tuple(self.args) + tuple(getattr(self, 'kwonlyargs', ()))
        if only_required:
            defaults_dict = self.get_defaults_dict()
            arg_names = tuple([an for an in arg_names if an not in defaults_dict])
        return arg_names

    def add_arg(self, arg_name, default=NO_DEFAULT, kwonly=False):
        """Add an argument with optional *default* (defaults to
        ``funcutils.NO_DEFAULT``). Pass *kwonly=True* to add a
        keyword-only argument
        """
        if arg_name in self.args:
            raise ExistingArgument(f'arg {arg_name!r} already in func {self.name} arg list')
        if arg_name in self.kwonlyargs:
            raise ExistingArgument(f'arg {arg_name!r} already in func {self.name} kwonly arg list')
        if not kwonly:
            self.args.append(arg_name)
            if default is not NO_DEFAULT:
                self.defaults = (self.defaults or ()) + (default,)
        else:
            self.kwonlyargs.append(arg_name)
            if default is not NO_DEFAULT:
                self.kwonlydefaults[arg_name] = default

    def remove_arg(self, arg_name):
        """Remove an argument from this FunctionBuilder's argument list. The
        resulting function will have one less argument per call to
        this function.

        Args:
            arg_name (str): The name of the argument to remove.

        Raises a :exc:`ValueError` if the argument is not present.

        """
        args = self.args
        d_dict = self.get_defaults_dict()
        try:
            args.remove(arg_name)
        except ValueError:
            try:
                self.kwonlyargs.remove(arg_name)
            except (AttributeError, ValueError):
                # missing from both
                exc = MissingArgument('arg %r not found in %s argument list:'
                                      ' %r' % (arg_name, self.name, args))
                exc.arg_name = arg_name
                raise exc
            else:
                self.kwonlydefaults.pop(arg_name, None)
        else:
            d_dict.pop(arg_name, None)
            self.defaults = tuple([d_dict[a] for a in args if a in d_dict])
        return

    def _compile(self, src, execdict):

        filename = ('<%s-%d>'
                    % (self.filename, next(self._compile_count),))
        try:
            code = compile(src, filename, 'single')
            exec(code, execdict)
        except Exception:
            raise
        return execdict


class MissingArgument(ValueError):
    pass


class ExistingArgument(ValueError):
    pass


def _indent(text, margin, newline='\n', key=bool):
    "based on boltons.strutils.indent"
    indented_lines = [(margin + line if key(line) else line)
                      for line in text.splitlines()]
    return newline.join(indented_lines)


def noop(*args, **kwargs):
    """
    Simple function that should be used when no effect is desired.
    An alternative to checking for  an optional function type parameter.

    e.g.
    def decorate(func, pre_func=None, post_func=None):
        if pre_func:
            pre_func()
        func()
        if post_func:
            post_func()

    vs

    def decorate(func, pre_func=noop, post_func=noop):
        pre_func()
        func()
        post_func()
    """
    return None

# end funcutils.py
