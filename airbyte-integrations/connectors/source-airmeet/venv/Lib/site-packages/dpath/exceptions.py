class InvalidGlob(Exception):
    """The glob passed is invalid."""
    pass


class PathNotFound(Exception):
    """One or more elements of the requested path did not exist in the object"""
    pass


class InvalidKeyName(Exception):
    """This key contains the separator character or another invalid character"""
    pass


class FilteredValue(Exception):
    """Unable to return a value, since the filter rejected it"""
    pass
