import dataclasses
import inspect

from ._types import APIName


@dataclasses.dataclass(slots=True, kw_only=True)
class Parameter:
    """Parameter from function signature in :py:class:`FunctionResolver`."""

    name: APIName
    signature: inspect.Parameter
    resolved_type: type
    doc: str | None

    @property
    def is_optional(self) -> bool:
        return self.signature.default is not inspect.Signature.empty


@dataclasses.dataclass(slots=True, frozen=True)
class Arg:
    """An alternative name when exposing a function argument to the API.

    Useful to avoid conflicts with reserved words.

    Example usage:

    >>> @function
    ... def pull(from_: Annotated[str, Arg("from")]):
    ...     ...
    """

    name: APIName
