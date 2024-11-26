"""
# 🌱 Turn any object into a module 🌱

Callable modules!  Indexable modules!?

Ever wanted to call a module directly, or index it?  Or just sick of seeing
`from foo import foo` in your examples?

Give your module the awesome power of an object, or maybe just save a
little typing, with `xmod`.

`xmod` is a tiny library that lets a module to do things that normally
only a class could do - handy for modules that "just do one thing".

## Example: Make a module callable like a function!

    # In your_module.py
    import xmod

    @xmod
    def a_function():
        return 'HERE!!'


    # Test at the command line
    >>> import your_module
    >>> your_module()
    HERE!!

## Example: Make a module look like a list!?!

    # In your_module.py
    import xmod

    xmod(list(), __name__)

    # Test at the command line
    >>> import your_module
    >>> assert your_module == []
    >>> your_module.extend(range(3))
    >>> print(your_module)
    [0, 1, 2]
"""
__all__ = ('xmod',)

import functools
import sys
import typing as t

_OMIT = {
    '__class__',
    '__getattr__',
    '__getattribute__',
    '__init__',
    '__init_subclass__',
    '__new__',
    '__setattr__',
}

_EXTENSION_ATTRIBUTE = '_xmod_extension'
_WRAPPED_ATTRIBUTE = '_xmod_wrapped'


def xmod(
    extension: t.Any = None,
    name: t.Optional[str] = None,
    full: t.Optional[bool] = None,
    omit: t.Optional[t.Sequence[str]] = None,
    mutable: bool = False,
) -> t.Any:
    """
    Extend the system module at `name` with any Python object.

    The original module is replaced in `sys.modules` by a proxy class
    which delegates attributes to the original module, and then adds
    attributes from the extension.

    In the most common use case, the extension is a callable and only the
    `__call__` method is delegated, so `xmod` can also be used as a
    decorator, both with and without parameters.

    Args:
      extension: The object whose methods and properties extend the namespace.
        This includes magic methods like __call__ and __getitem__.

      name: The name of this symbol in `sys.modules`.  If this is `None`
        then `xmod` will use `extension.__module__`.

        This only needs to be be set if `extension` is _not_ a function or
        class defined in the module that's being extended.

        If the `name` argument is given, it should almost certainly be
        `__name__`.

      full: If `False`, just add extension as a callable.

        If `True`, extend the module with all members of `extension`.

        If `None`, the default, add the extension if it's a callable, otherwise
        extend the module with all members of `extension`.

      mutable: If `True`, the attributes on the proxy are mutable and write
        through to the underlying module.  If `False`, the default, attributes
        on the proxy cannot be changed.

      omit: A list of methods _not_ to delegate from the proxy to the extension

        If `omit` is None, it defaults to `xmod._OMIT`, which seems to
        work well.

    Returns:
        `extension`, the original item that got decorated
    """
    if extension is None:
        # It's a decorator with properties
        return functools.partial(
            xmod, name=name, full=full, omit=omit, mutable=mutable
        )

    def method(f) -> t.Callable:
        @functools.wraps(f)
        def wrapped(self, *args, **kwargs):
            return f(*args, **kwargs)

        return wrapped

    def mutator(f) -> t.Callable:
        def fail(*args, **kwargs):
            raise TypeError(f'Class is immutable {args} {kwargs}')

        return method(f) if mutable else fail

    def prop(k) -> property:
        return property(
            method(lambda: getattr(extension, k)),
            mutator(lambda v: setattr(extension, k, v)),
            mutator(lambda: delattr(extension, k)),
        )

    name = name or getattr(extension, '__module__', None)
    if not name:
        raise ValueError('`name` parameter must be set')

    module = sys.modules[name]

    def _getattr(k) -> t.Any:
        try:
            return getattr(extension, k)
        except AttributeError:
            return getattr(module, k)

    def _setattr(k, v) -> None:
        if hasattr(extension, k):
            setattr(extension, k, v)
        else:
            setattr(module, k, v)

    def _delattr(k) -> None:
        success = True
        try:
            delattr(extension, k)
        except AttributeError:
            success = False
        try:
            delattr(module, k)
        except AttributeError:
            if not success:
                raise

    members = {
        _WRAPPED_ATTRIBUTE: module,
        '__getattr__': method(_getattr),
        '__setattr__': mutator(_setattr),
        '__delattr__': mutator(_delattr),
        '__doc__': getattr(module, '__doc__'),
    }

    if callable(extension):
        members['__call__'] = method(extension)
        members[_EXTENSION_ATTRIBUTE] = staticmethod(extension)

    elif full is False:
        raise ValueError('extension must be callable if full is False')

    else:
        members[_EXTENSION_ATTRIBUTE] = extension
        full = True

    om = _OMIT if omit is None else set(omit)
    for a in dir(extension) if full else ():
        if a not in om:
            value = getattr(extension, a)
            is_magic = a.startswith('__') and callable(value)
            if is_magic:
                members[a] = method(value)
            elif False:  # TODO: enable or delete this
                members[a] = prop(a)

    def directory(self) -> t.List:
        return sorted(set(members).union(dir(module)))

    members['__dir__'] = directory

    proxy_class = type(name, (object,), members)
    sys.modules[name] = proxy_class()
    return extension


xmod(xmod)
