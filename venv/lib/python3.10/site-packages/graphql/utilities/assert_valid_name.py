from typing import Optional

from ..type.assert_name import assert_name
from ..error import GraphQLError

__all__ = ["assert_valid_name", "is_valid_name_error"]


def assert_valid_name(name: str) -> str:
    """Uphold the spec rules about naming.

    .. deprecated:: 3.2
       Please use ``assert_name`` instead. Will be removed in v3.3.
    """
    error = is_valid_name_error(name)
    if error:
        raise error
    return name


def is_valid_name_error(name: str) -> Optional[GraphQLError]:
    """Return an Error if a name is invalid.

    .. deprecated:: 3.2
       Please use ``assert_name`` instead. Will be removed in v3.3.
    """
    if not isinstance(name, str):
        raise TypeError("Expected name to be a string.")
    if name.startswith("__"):
        return GraphQLError(
            f"Name {name!r} must not begin with '__',"
            " which is reserved by GraphQL introspection."
        )
    try:
        assert_name(name)
    except GraphQLError as error:
        return error
    return None
