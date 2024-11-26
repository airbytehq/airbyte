"""
Exception classes.

.. versionadded:: 1.0.0
"""

__all__ = ("InvalidMethod",)


# NOTE: This needs to subclass AttributeError due to compatibility with typing.Protocol and
#  runtime_checkable. See https://github.com/dgilland/pydash/issues/165
class InvalidMethod(AttributeError):
    """
    Raised when an invalid pydash method is invoked through :func:`pydash.chaining.chain`.

    .. versionadded:: 1.0.0
    """

    pass
