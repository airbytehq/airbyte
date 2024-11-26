# This module is part of GitPython and is released under the
# 3-Clause BSD License: https://opensource.org/license/bsd-3-clause/

import os
import sys
from typing import (  # noqa: F401
    Dict,
    NoReturn,
    Sequence as Sequence,
    Tuple,
    Union,
    Any,
    Optional,
    Callable,
    TYPE_CHECKING,
    TypeVar,
)

if sys.version_info >= (3, 8):
    from typing import (  # noqa: F401
        Literal,
        TypedDict,
        Protocol,
        SupportsIndex as SupportsIndex,
        runtime_checkable,
    )
else:
    from typing_extensions import (  # noqa: F401
        Literal,
        SupportsIndex as SupportsIndex,
        TypedDict,
        Protocol,
        runtime_checkable,
    )

# if sys.version_info >= (3, 10):
#     from typing import TypeGuard  # noqa: F401
# else:
#     from typing_extensions import TypeGuard  # noqa: F401

PathLike = Union[str, "os.PathLike[str]"]

if TYPE_CHECKING:
    from git.repo import Repo
    from git.objects import Commit, Tree, TagObject, Blob

    # from git.refs import SymbolicReference

TBD = Any
_T = TypeVar("_T")

Tree_ish = Union["Commit", "Tree"]
Commit_ish = Union["Commit", "TagObject", "Blob", "Tree"]
Lit_commit_ish = Literal["commit", "tag", "blob", "tree"]

# Config_levels ---------------------------------------------------------

Lit_config_levels = Literal["system", "global", "user", "repository"]

# Progress parameter type alias -----------------------------------------

CallableProgress = Optional[Callable[[int, Union[str, float], Union[str, float, None], str], None]]

# def is_config_level(inp: str) -> TypeGuard[Lit_config_levels]:
#     # return inp in get_args(Lit_config_level)  # only py >= 3.8
#     return inp in ("system", "user", "global", "repository")


ConfigLevels_Tup = Tuple[Literal["system"], Literal["user"], Literal["global"], Literal["repository"]]

# -----------------------------------------------------------------------------------


def assert_never(inp: NoReturn, raise_error: bool = True, exc: Union[Exception, None] = None) -> None:
    """For use in exhaustive checking of literal or Enum in if/else chain.

    Should only be reached if all members not handled OR attempt to pass non-members through chain.

    If all members handled, type is Empty. Otherwise, will cause mypy error.

    If non-members given, should cause mypy error at variable creation.

    If raise_error is True, will also raise AssertionError or the Exception passed to exc.
    """
    if raise_error:
        if exc is None:
            raise ValueError(f"An unhandled Literal ({inp}) in an if/else chain was found")
        else:
            raise exc


class Files_TD(TypedDict):
    insertions: int
    deletions: int
    lines: int


class Total_TD(TypedDict):
    insertions: int
    deletions: int
    lines: int
    files: int


class HSH_TD(TypedDict):
    total: Total_TD
    files: Dict[PathLike, Files_TD]


@runtime_checkable
class Has_Repo(Protocol):
    repo: "Repo"


@runtime_checkable
class Has_id_attribute(Protocol):
    _id_attribute_: str
