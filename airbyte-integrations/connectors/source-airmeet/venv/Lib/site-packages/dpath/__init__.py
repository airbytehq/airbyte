# Needed for pre-3.10 versions
from __future__ import annotations

__all__ = [
    "new",
    "delete",
    "set",
    "get",
    "values",
    "search",
    "merge",
    "exceptions",
    "options",
    "segments",
    "types",
    "version",
    "MergeType",
    "PathSegment",
    "Filter",
    "Glob",
    "Path",
    "Hints",
    "Creator",
]

from collections.abc import MutableMapping, MutableSequence
from typing import Union, List, Any, Callable, Optional

from dpath import segments, options
from dpath.exceptions import InvalidKeyName, PathNotFound
from dpath.types import MergeType, PathSegment, Creator, Filter, Glob, Path, Hints

_DEFAULT_SENTINEL = object()


def _split_path(path: Path, separator: Optional[str] = "/") -> Union[List[PathSegment], PathSegment]:
    """
    Given a path and separator, return a tuple of segments. If path is
    already a non-leaf thing, return it.

    Note that a string path with the separator at index[0] will have the
    separator stripped off. If you pass a list path, the separator is
    ignored, and is assumed to be part of each key glob. It will not be
    stripped.
    """
    if not segments.leaf(path):
        split_segments = path
    else:
        split_segments = path.lstrip(separator).split(separator)

    return split_segments


def new(obj: MutableMapping, path: Path, value, separator="/", creator: Creator | None = None) -> MutableMapping:
    """
    Set the element at the terminus of path to value, and create
    it if it does not exist (as opposed to 'set' that can only
    change existing keys).

    path will NOT be treated like a glob. If it has globbing
    characters in it, they will become part of the resulting
    keys

    creator allows you to pass in a creator method that is
    responsible for creating missing keys at arbitrary levels of
    the path (see the help for dpath.path.set)
    """
    split_segments = _split_path(path, separator)
    if creator:
        return segments.set(obj, split_segments, value, creator=creator)
    return segments.set(obj, split_segments, value)


def delete(obj: MutableMapping, glob: Glob, separator="/", afilter: Filter | None = None) -> int:
    """
    Given a obj, delete all elements that match the glob.

    Returns the number of deleted objects. Raises PathNotFound if no paths are
    found to delete.
    """
    globlist = _split_path(glob, separator)

    def f(obj, pair, counter):
        (path_segments, value) = pair

        # Skip segments if they no longer exist in obj.
        if not segments.has(obj, path_segments):
            return

        matched = segments.match(path_segments, globlist)
        selected = afilter and segments.leaf(value) and afilter(value)

        if (matched and not afilter) or selected:
            key = path_segments[-1]
            parent = segments.get(obj, path_segments[:-1])

            # Deletion behavior depends on parent type
            if isinstance(parent, MutableMapping):
                del parent[key]

            else:
                # Handle sequence types
                # TODO: Consider cases where type isn't a simple list (e.g. set)

                if len(parent) - 1 == key:
                    # Removing the last element of a sequence. It can be
                    # truly removed without affecting the ordering of
                    # remaining items.
                    #
                    # Note: In order to achieve proper behavior we are
                    # relying on the reverse iteration of
                    # non-dictionaries from segments.kvs().
                    # Otherwise we'd be unable to delete all the tails
                    # of a list and end up with None values when we
                    # don't need them.
                    del parent[key]

                else:
                    # This key can't be removed completely because it
                    # would affect the order of items that remain in our
                    # result.
                    parent[key] = None

            counter[0] += 1

    [deleted] = segments.foldm(obj, f, [0])
    if not deleted:
        raise PathNotFound(f"Could not find {glob} to delete it")

    return deleted


def set(obj: MutableMapping, glob: Glob, value, separator="/", afilter: Filter | None = None) -> int:
    """
    Given a path glob, set all existing elements in the document
    to the given value. Returns the number of elements changed.
    """
    globlist = _split_path(glob, separator)

    def f(obj, pair, counter):
        (path_segments, found) = pair

        # Skip segments if they no longer exist in obj.
        if not segments.has(obj, path_segments):
            return

        matched = segments.match(path_segments, globlist)
        selected = afilter and segments.leaf(found) and afilter(found)

        if (matched and not afilter) or (matched and selected):
            segments.set(obj, path_segments, value, creator=None)
            counter[0] += 1

    [changed] = segments.foldm(obj, f, [0])
    return changed


def get(
        obj: MutableMapping,
        glob: Glob,
        separator="/",
        default: Any = _DEFAULT_SENTINEL
) -> Union[MutableMapping, object, Callable]:
    """
    Given an object which contains only one possible match for the given glob,
    return the value for the leaf matching the given glob.
    If the glob is not found and a default is provided,
    the default is returned.

    If more than one leaf matches the glob, ValueError is raised. If the glob is
    not found and a default is not provided, KeyError is raised.
    """
    if isinstance(glob, str) and glob == "/" or len(glob) == 0:
        return obj

    globlist = _split_path(glob, separator)

    def f(_, pair, results):
        (path_segments, found) = pair

        if segments.match(path_segments, globlist):
            results.append(found)
        if len(results) > 1:
            return False

    results = segments.fold(obj, f, [])

    if len(results) == 0:
        if default is not _DEFAULT_SENTINEL:
            return default

        raise KeyError(glob)
    elif len(results) > 1:
        raise ValueError(f"dpath.get() globs must match only one leaf: {glob}")

    return results[0]


def values(obj: MutableMapping, glob: Glob, separator="/", afilter: Filter | None = None, dirs=True):
    """
    Given an object and a path glob, return an array of all values which match
    the glob. The arguments to this function are identical to those of search().
    """
    yielded = True

    return [v for p, v in search(obj, glob, yielded, separator, afilter, dirs)]


def search(obj: MutableMapping, glob: Glob, yielded=False, separator="/", afilter: Filter | None = None, dirs=True):
    """
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead, tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob.
    """

    split_glob = _split_path(glob, separator)

    def keeper(path, found):
        """
        Generalized test for use in both yielded and folded cases.
        Returns True if we want this result. Otherwise, returns False.
        """
        if not dirs and not segments.leaf(found):
            return False

        matched = segments.match(path, split_glob)
        selected = afilter and afilter(found)

        return (matched and not afilter) or (matched and selected)

    if yielded:
        def yielder():
            for path, found in segments.walk(obj):
                if keeper(path, found):
                    yield separator.join(map(segments.int_str, path)), found

        return yielder()
    else:
        def f(obj, pair, result):
            (path, found) = pair

            if keeper(path, found):
                segments.set(result, path, found, hints=segments.types(obj, path))

        return segments.fold(obj, f, {})


def merge(
        dst: MutableMapping,
        src: MutableMapping,
        separator="/",
        afilter: Filter | None = None,
        flags=MergeType.ADDITIVE
):
    """
    Merge source into destination. Like dict.update() but performs deep
    merging.

    NOTE: This does not do a deep copy of the source object. Applying merge
    will result in references to src being present in the dst tree. If you do
    not want src to potentially be modified by other changes in dst (e.g. more
    merge calls), then use a deep copy of src.

    NOTE that merge() does NOT copy objects - it REFERENCES. If you merge
    take these two dictionaries:

    >>> a = {'a': [0] }
    >>> b = {'a': [1] }

    ... and you merge them into an empty dictionary, like so:

    >>> d = {}
    >>> dpath.merge(d, a)
    >>> dpath.merge(d, b)

    ... you might be surprised to find that a['a'] now contains [0, 1].
    This is because merge() says (d['a'] = a['a']), and thus creates a reference.
    This reference is then modified when b is merged, causing both d and
    a to have ['a'][0, 1]. To avoid this, make your own deep copies of source
    objects that you intend to merge. For further notes see
    https://github.com/akesterson/dpath-python/issues/58

    flags is an OR'ed combination of MergeType enum members.
    """
    filtered_src = search(src, '**', afilter=afilter, separator='/')

    def are_both_mutable(o1, o2):
        mapP = isinstance(o1, MutableMapping) and isinstance(o2, MutableMapping)
        seqP = isinstance(o1, MutableSequence) and isinstance(o2, MutableSequence)

        if mapP or seqP:
            return True

        return False

    def merger(dst, src, _segments=()):
        for key, found in segments.make_walkable(src):
            # Our current path in the source.
            current_path = _segments + (key,)

            if len(key) == 0 and not options.ALLOW_EMPTY_STRING_KEYS:
                raise InvalidKeyName("Empty string keys not allowed without "
                                     "dpath.options.ALLOW_EMPTY_STRING_KEYS=True: "
                                     f"{current_path}")

            # Validate src and dst types match.
            if flags & MergeType.TYPESAFE:
                if segments.has(dst, current_path):
                    target = segments.get(dst, current_path)
                    tt = type(target)
                    ft = type(found)
                    if tt != ft:
                        path = separator.join(current_path)
                        raise TypeError(f"Cannot merge objects of type {tt} and {ft} at {path}")

            # Path not present in destination, create it.
            if not segments.has(dst, current_path):
                segments.set(dst, current_path, found)
                continue

            # Retrieve the value in the destination.
            target = segments.get(dst, current_path)

            # If the types don't match, replace it.
            if type(found) is not type(target) and not are_both_mutable(found, target):
                segments.set(dst, current_path, found)
                continue

            # If target is a leaf, the replace it.
            if segments.leaf(target):
                segments.set(dst, current_path, found)
                continue

            # At this point we know:
            #
            # * The target exists.
            # * The types match.
            # * The target isn't a leaf.
            #
            # Pretend we have a sequence and account for the flags.
            try:
                if flags & MergeType.ADDITIVE:
                    target += found
                    continue

                if flags & MergeType.REPLACE:
                    try:
                        target[""]
                    except TypeError:
                        segments.set(dst, current_path, found)
                        continue
                    except Exception:
                        raise
            except Exception:
                # We have a dictionary like thing and we need to attempt to
                # recursively merge it.
                merger(dst, found, current_path)

    merger(dst, filtered_src)

    return dst
