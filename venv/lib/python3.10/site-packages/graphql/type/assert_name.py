from ..error import GraphQLError
from ..language.character_classes import is_name_start, is_name_continue

__all__ = ["assert_name", "assert_enum_value_name"]


def assert_name(name: str) -> str:
    """Uphold the spec rules about naming."""
    if name is None:
        raise TypeError("Must provide name.")
    if not isinstance(name, str):
        raise TypeError("Expected name to be a string.")
    if not name:
        raise GraphQLError("Expected name to be a non-empty string.")
    if not all(is_name_continue(char) for char in name[1:]):
        raise GraphQLError(
            f"Names must only contain [_a-zA-Z0-9] but {name!r} does not."
        )
    if not is_name_start(name[0]):
        raise GraphQLError(f"Names must start with [_a-zA-Z] but {name!r} does not.")
    return name


def assert_enum_value_name(name: str) -> str:
    """Uphold the spec rules about naming enum values."""
    assert_name(name)
    if name in {"true", "false", "null"}:
        raise GraphQLError(f"Enum values cannot be named: {name}.")
    return name
