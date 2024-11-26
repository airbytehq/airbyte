#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **path testers** (i.e., low-level callables testing various aspects
of on-disk files and directories and raising exceptions when those files and
directories fail to satisfy various constraints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilPathException
from beartype._data.hint.datahinttyping import (
    PathnameLike,
    # PathnameLikeTuple,
    TypeException,
)
from os import (
    X_OK,
    access as is_path_permissions,
)
from pathlib import Path

# ....................{ RAISERS ~ dir                      }....................
#FIXME: Unit test us up, please.
def die_unless_dir(
    # Mandatory parameters.
    dirname: PathnameLike,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilPathException,
) -> None:
    '''
    Raise an exception of the passed type if *no* directory with the passed
    dirname exists.

    Parameters
    ----------
    dirname : PathnameLike
        Dirname to be validated.
    exception_cls : Type[Exception], optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilPathException`.

    Raises
    ----------
    :exc:`exception_cls`
        If *no* directory with the passed dirname exists.
    '''

    # High-level "Path" object encapsulating this dirname.
    dirname_path = Path(dirname)

    # If either no path with this pathname exists *OR* a path with this pathname
    # exists but this path is not a directory...
    if not dirname_path.is_dir():
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')

        # If no path with this pathname exists, raise an appropriate exception.
        if not dirname_path.exists():
            raise exception_cls(f'Directory "{dirname_path}" not found.')
        # Else, a path with this pathname exists.

        # By elimination, a path with this pathname exists but this path is not
        # a directory. In this case, raise an appropriate exception.
        raise exception_cls(f'Path "{dirname_path}" not directory.')
    # Else, a directory with this dirname exists.

# ....................{ RAISERS ~ file                     }....................
#FIXME: Unit test us up, please.
def die_unless_file(
    # Mandatory parameters.
    filename: PathnameLike,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilPathException,
) -> None:
    '''
    Raise an exception of the passed type if *no* file with the passed filename
    exists.

    Parameters
    ----------
    filename : PathnameLike
        Dirname to be validated.
    exception_cls : Type[Exception], optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilPathException`.

    Raises
    ----------
    :exc:`exception_cls`
        If *no* file with the passed filename exists.
    '''

    # High-level "Path" object encapsulating this filename.
    filename_path = Path(filename)

    # If either no path with this pathname exists *OR* a path with this pathname
    # exists but this path is not a file...
    if not filename_path.is_file():
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')

        # If no path with this pathname exists, raise an appropriate exception.
        if not filename_path.exists():
            raise exception_cls(f'File "{filename_path}" not found.')
        # Else, a path with this pathname exists.

        # By elimination, a path with this pathname exists but this path is not
        # a file. In this case, raise an appropriate exception.
        raise exception_cls(f'Path "{filename_path}" not file.')
    # Else, a file with this filename exists.


#FIXME: Unit test us up, please.
def die_unless_file_executable(
    # Mandatory parameters.
    filename: PathnameLike,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilPathException,
) -> None:
    '''
    Raise an exception of the passed type if either no file with the passed
    filename exists *or* this file exists but is not **executable** (i.e., the
    current user lacks sufficient permissions to execute this file).

    Parameters
    ----------
    filename : PathnameLike
        Dirname to be validated.
    exception_cls : Type[Exception], optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilPathException`.

    Raises
    ----------
    :exc:`exception_cls`
        If either:

        * No file with the passed filename exists.
        * This file exists but is not executable by the current user.
    '''

    # If *NO* file with this filename exists, raise an exception.
    die_unless_file(filename=filename, exception_cls=exception_cls)
    # Else, a file with this filename exists.

    # Note that this logic necessarily leverages the low-level "os.path"
    # submodule rather than the object-oriented "pathlib.Path" class, which
    # currently lacks *ANY* public facilities for introspecting permissions
    # (including executability) as of Python 3.12. This is why we sigh.

    # Reduce this possible high-level "Path" object to a low-level filename.
    filename_str = str(filename)

    # If the current user has *NO* permission to execute this file...
    if not is_path_permissions(filename_str, X_OK):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')

        # Raise an appropriate exception.
        raise exception_cls(f'File "{filename_str}" not executable.')
    # Else, the current user has permission to execute this file. Ergo, this
    # file is an executable file with respect to this user.
