__all__ = ["FrozenError"]


class FrozenError(TypeError):
    """Error when trying to change a frozen (read only) collection."""
