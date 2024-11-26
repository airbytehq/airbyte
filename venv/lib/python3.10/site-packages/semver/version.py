"""Version handling by a semver compatible version class."""

import re
from functools import wraps
from typing import (
    Any,
    ClassVar,
    Dict,
    Iterable,
    Optional,
    Pattern,
    SupportsInt,
    Tuple,
    Union,
    cast,
    Callable,
    Collection,
    Type,
    TypeVar,
)

from ._types import (
    VersionTuple,
    VersionDict,
    VersionIterator,
    String,
    VersionPart,
)

# These types are required here because of circular imports
Comparable = Union["Version", Dict[str, VersionPart], Collection[VersionPart], str]
Comparator = Callable[["Version", Comparable], bool]

T = TypeVar("T", bound="Version")


def _comparator(operator: Comparator) -> Comparator:
    """Wrap a Version binary op method in a type-check."""

    @wraps(operator)
    def wrapper(self: "Version", other: Comparable) -> bool:
        comparable_types = (
            Version,
            dict,
            tuple,
            list,
            *String.__args__,  # type: ignore
        )
        if not isinstance(other, comparable_types):
            return NotImplemented
        return operator(self, other)

    return wrapper


def _cmp(a, b):  # TODO: type hints
    """Return negative if a<b, zero if a==b, positive if a>b."""
    return (a > b) - (a < b)


class Version:
    """
    A semver compatible version class.

    See specification at https://semver.org.

    :param major: version when you make incompatible API changes.
    :param minor: version when you add functionality in a backwards-compatible manner.
    :param patch: version when you make backwards-compatible bug fixes.
    :param prerelease: an optional prerelease string
    :param build: an optional build string
    """

    __slots__ = ("_major", "_minor", "_patch", "_prerelease", "_build")

    #: The names of the different parts of a version
    NAMES: ClassVar[Tuple[str, ...]] = tuple([item[1:] for item in __slots__])

    #: Regex for number in a prerelease
    _LAST_NUMBER: ClassVar[Pattern[str]] = re.compile(r"(?:[^\d]*(\d+)[^\d]*)+")
    #: Regex template for a semver version
    _REGEX_TEMPLATE: ClassVar[
        str
    ] = r"""
            ^
            (?P<major>0|[1-9]\d*)
            (?:
                \.
                (?P<minor>0|[1-9]\d*)
                (?:
                    \.
                    (?P<patch>0|[1-9]\d*)
                ){opt_patch}
            ){opt_minor}
            (?:-(?P<prerelease>
                (?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)
                (?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*
            ))?
            (?:\+(?P<build>
                [0-9a-zA-Z-]+
                (?:\.[0-9a-zA-Z-]+)*
            ))?
            $
        """
    #: Regex for a semver version
    _REGEX: ClassVar[Pattern[str]] = re.compile(
        _REGEX_TEMPLATE.format(opt_patch="", opt_minor=""),
        re.VERBOSE,
    )
    #: Regex for a semver version that might be shorter
    _REGEX_OPTIONAL_MINOR_AND_PATCH: ClassVar[Pattern[str]] = re.compile(
        _REGEX_TEMPLATE.format(opt_patch="?", opt_minor="?"),
        re.VERBOSE,
    )

    def __init__(
        self,
        major: SupportsInt,
        minor: SupportsInt = 0,
        patch: SupportsInt = 0,
        prerelease: Optional[Union[String, int]] = None,
        build: Optional[Union[String, int]] = None,
    ):
        # Build a dictionary of the arguments except prerelease and build
        version_parts = {"major": int(major), "minor": int(minor), "patch": int(patch)}

        for name, value in version_parts.items():
            if value < 0:
                raise ValueError(
                    "{!r} is negative. A version can only be positive.".format(name)
                )

        self._major = version_parts["major"]
        self._minor = version_parts["minor"]
        self._patch = version_parts["patch"]
        self._prerelease = None if prerelease is None else str(prerelease)
        self._build = None if build is None else str(build)

    @classmethod
    def _nat_cmp(cls, a, b):  # TODO: type hints
        def cmp_prerelease_tag(a, b):
            if isinstance(a, int) and isinstance(b, int):
                return _cmp(a, b)
            elif isinstance(a, int):
                return -1
            elif isinstance(b, int):
                return 1
            else:
                return _cmp(a, b)

        a, b = a or "", b or ""
        a_parts, b_parts = a.split("."), b.split(".")
        a_parts = [int(x) if re.match(r"^\d+$", x) else x for x in a_parts]
        b_parts = [int(x) if re.match(r"^\d+$", x) else x for x in b_parts]
        for sub_a, sub_b in zip(a_parts, b_parts):
            cmp_result = cmp_prerelease_tag(sub_a, sub_b)
            if cmp_result != 0:
                return cmp_result
        else:
            return _cmp(len(a), len(b))

    @property
    def major(self) -> int:
        """The major part of a version (read-only)."""
        return self._major

    @major.setter
    def major(self, value):
        raise AttributeError("attribute 'major' is readonly")

    @property
    def minor(self) -> int:
        """The minor part of a version (read-only)."""
        return self._minor

    @minor.setter
    def minor(self, value):
        raise AttributeError("attribute 'minor' is readonly")

    @property
    def patch(self) -> int:
        """The patch part of a version (read-only)."""
        return self._patch

    @patch.setter
    def patch(self, value):
        raise AttributeError("attribute 'patch' is readonly")

    @property
    def prerelease(self) -> Optional[str]:
        """The prerelease part of a version (read-only)."""
        return self._prerelease

    @prerelease.setter
    def prerelease(self, value):
        raise AttributeError("attribute 'prerelease' is readonly")

    @property
    def build(self) -> Optional[str]:
        """The build part of a version (read-only)."""
        return self._build

    @build.setter
    def build(self, value):
        raise AttributeError("attribute 'build' is readonly")

    def to_tuple(self) -> VersionTuple:
        """
        Convert the Version object to a tuple.

        .. versionadded:: 2.10.0
           Renamed :meth:`Version._astuple` to :meth:`Version.to_tuple` to
           make this function available in the public API.

        :return: a tuple with all the parts

        >>> semver.Version(5, 3, 1).to_tuple()
        (5, 3, 1, None, None)
        """
        return (self.major, self.minor, self.patch, self.prerelease, self.build)

    def to_dict(self) -> VersionDict:
        """
        Convert the Version object to an dict.

        .. versionadded:: 2.10.0
           Renamed :meth:`Version._asdict` to :meth:`Version.to_dict` to
           make this function available in the public API.

        :return: an dict with the keys in the order ``major``, ``minor``,
          ``patch``, ``prerelease``, and ``build``.

        >>> semver.Version(3, 2, 1).to_dict()
        {'major': 3, 'minor': 2, 'patch': 1, 'prerelease': None, 'build': None}
        """
        return dict(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            prerelease=self.prerelease,
            build=self.build,
        )

    def __iter__(self) -> VersionIterator:
        """Return iter(self)."""
        yield from self.to_tuple()

    @staticmethod
    def _increment_string(string: str) -> str:
        """
        Look for the last sequence of number(s) in a string and increment.

        :param string: the string to search for.
        :return: the incremented string

        Source:
        http://code.activestate.com/recipes/442460-increment-numbers-in-a-string/#c1
        """
        match = Version._LAST_NUMBER.search(string)
        if match:
            next_ = str(int(match.group(1)) + 1)
            start, end = match.span(1)
            string = string[: max(end - len(next_), start)] + next_ + string[end:]
        return string

    def bump_major(self) -> "Version":
        """
        Raise the major part of the version, return a new object but leave self
        untouched.

        :return: new object with the raised major part

        >>> ver = semver.parse("3.4.5")
        >>> ver.bump_major()
        Version(major=4, minor=0, patch=0, prerelease=None, build=None)
        """
        cls = type(self)
        return cls(self._major + 1)

    def bump_minor(self) -> "Version":
        """
        Raise the minor part of the version, return a new object but leave self
        untouched.

        :return: new object with the raised minor part

        >>> ver = semver.parse("3.4.5")
        >>> ver.bump_minor()
        Version(major=3, minor=5, patch=0, prerelease=None, build=None)
        """
        cls = type(self)
        return cls(self._major, self._minor + 1)

    def bump_patch(self) -> "Version":
        """
        Raise the patch part of the version, return a new object but leave self
        untouched.

        :return: new object with the raised patch part

        >>> ver = semver.parse("3.4.5")
        >>> ver.bump_patch()
        Version(major=3, minor=4, patch=6, prerelease=None, build=None)
        """
        cls = type(self)
        return cls(self._major, self._minor, self._patch + 1)

    def bump_prerelease(self, token: Optional[str] = "rc") -> "Version":
        """
        Raise the prerelease part of the version, return a new object but leave
        self untouched.

        :param token: defaults to ``'rc'``
        :return: new :class:`Version` object with the raised prerelease part.
            The original object is not modified.

        >>> ver = semver.parse("3.4.5")
        >>> ver.bump_prerelease().prerelease
        'rc.2'
        >>> ver.bump_prerelease('').prerelease
        '1'
        >>> ver.bump_prerelease(None).prerelease
        'rc.1'
        """
        cls = type(self)
        if self._prerelease is not None:
            prerelease = self._prerelease
        elif token == "":
            prerelease = "0"
        elif token is None:
            prerelease = "rc.0"
        else:
            prerelease = str(token) + ".0"

        prerelease = cls._increment_string(prerelease)
        return cls(self._major, self._minor, self._patch, prerelease)

    def bump_build(self, token: Optional[str] = "build") -> "Version":
        """
        Raise the build part of the version, return a new object but leave self
        untouched.

        :param token: defaults to ``'build'``
        :return: new :class:`Version` object with the raised build part.
            The original object is not modified.

        >>> ver = semver.parse("3.4.5-rc.1+build.9")
        >>> ver.bump_build()
        Version(major=3, minor=4, patch=5, prerelease='rc.1', \
build='build.10')
        """
        cls = type(self)
        if self._build is not None:
            build = self._build
        elif token == "":
            build = "0"
        elif token is None:
            build = "build.0"
        else:
            build = str(token) + ".0"

        # self._build or (token or "build") + ".0"
        build = cls._increment_string(build)
        if self._build is not None:
            build = self._build
        elif token == "":
            build = "0"
        elif token is None:
            build = "build.0"
        else:
            build = str(token) + ".0"

        # self._build or (token or "build") + ".0"
        build = cls._increment_string(build)
        return cls(self._major, self._minor, self._patch, self._prerelease, build)

    def compare(self, other: Comparable) -> int:
        """
        Compare self with other.

        :param other: the second version
        :return: The return value is negative if ver1 < ver2,
             zero if ver1 == ver2 and strictly positive if ver1 > ver2

        >>> semver.compare("2.0.0")
        -1
        >>> semver.compare("1.0.0")
        1
        >>> semver.compare("2.0.0")
        0
        >>> semver.compare(dict(major=2, minor=0, patch=0))
        0
        """
        cls = type(self)
        if isinstance(other, String.__args__):  # type: ignore
            other = cls.parse(other)
        elif isinstance(other, dict):
            other = cls(**other)
        elif isinstance(other, (tuple, list)):
            other = cls(*other)
        elif not isinstance(other, cls):
            raise TypeError(
                f"Expected str, bytes, dict, tuple, list, or {cls.__name__} instance, "
                f"but got {type(other)}"
            )

        v1 = self.to_tuple()[:3]
        v2 = other.to_tuple()[:3]
        x = _cmp(v1, v2)
        if x:
            return x

        rc1, rc2 = self.prerelease, other.prerelease
        rccmp = self._nat_cmp(rc1, rc2)

        if not rccmp:
            return 0
        if not rc1:
            return 1
        elif not rc2:
            return -1

        return rccmp

    def next_version(self, part: str, prerelease_token: str = "rc") -> "Version":
        """
        Determines next version, preserving natural order.

        .. versionadded:: 2.10.0

        This function is taking prereleases into account.
        The "major", "minor", and "patch" raises the respective parts like
        the ``bump_*`` functions. The real difference is using the
        "prerelease" part. It gives you the next patch version of the
        prerelease, for example:

        >>> str(semver.parse("0.1.4").next_version("prerelease"))
        '0.1.5-rc.1'

        :param part: One of "major", "minor", "patch", or "prerelease"
        :param prerelease_token: prefix string of prerelease, defaults to 'rc'
        :return: new object with the appropriate part raised
        """
        cls = type(self)
        # "build" is currently not used, that's why we use [:-1]
        validparts = cls.NAMES[:-1]
        if part not in validparts:
            raise ValueError(
                f"Invalid part. Expected one of {validparts}, but got {part!r}"
            )
        version = self
        if (version.prerelease or version.build) and (
            part == "patch"
            or (part == "minor" and version.patch == 0)
            or (part == "major" and version.minor == version.patch == 0)
        ):
            return version.replace(prerelease=None, build=None)

        # Only check the main parts:
        if part in cls.NAMES[:3]:
            return getattr(version, "bump_" + part)()

        if not version.prerelease:
            version = version.bump_patch()
        return version.bump_prerelease(prerelease_token)

    @_comparator
    def __eq__(self, other: Comparable) -> bool:  # type: ignore
        return self.compare(other) == 0

    @_comparator
    def __ne__(self, other: Comparable) -> bool:  # type: ignore
        return self.compare(other) != 0

    @_comparator
    def __lt__(self, other: Comparable) -> bool:
        return self.compare(other) < 0

    @_comparator
    def __le__(self, other: Comparable) -> bool:
        return self.compare(other) <= 0

    @_comparator
    def __gt__(self, other: Comparable) -> bool:
        return self.compare(other) > 0

    @_comparator
    def __ge__(self, other: Comparable) -> bool:
        return self.compare(other) >= 0

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[int, Optional[str], Tuple[Union[int, str], ...]]:
        """
        self.__getitem__(index) <==> self[index] Implement getitem.

        If the part  requested is undefined, or a part of the range requested
        is undefined, it will throw an index error.
        Negative indices are not supported.

        :param index: a positive integer indicating the
               offset or a :func:`slice` object
        :raises IndexError: if index is beyond the range or a part is None
        :return: the requested part of the version at position index

        >>> ver = semver.Version.parse("3.4.5")
        >>> ver[0], ver[1], ver[2]
        (3, 4, 5)
        """
        if isinstance(index, int):
            index = slice(index, index + 1)
        index = cast(slice, index)

        if (
            isinstance(index, slice)
            and (index.start is not None and index.start < 0)
            or (index.stop is not None and index.stop < 0)
        ):
            raise IndexError("Version index cannot be negative")

        part = tuple(
            filter(lambda p: p is not None, cast(Iterable, self.to_tuple()[index]))
        )

        if len(part) == 1:
            return part[0]
        elif not part:
            raise IndexError("Version part undefined")
        return part

    def __repr__(self) -> str:
        s = ", ".join("%s=%r" % (key, val) for key, val in self.to_dict().items())
        return "%s(%s)" % (type(self).__name__, s)

    def __str__(self) -> str:
        version = "%d.%d.%d" % (self.major, self.minor, self.patch)
        if self.prerelease:
            version += "-%s" % self.prerelease
        if self.build:
            version += "+%s" % self.build
        return version

    def __hash__(self) -> int:
        return hash(self.to_tuple()[:4])

    def finalize_version(self) -> "Version":
        """
        Remove any prerelease and build metadata from the version.

        :return: a new instance with the finalized version string

        >>> str(semver.Version.parse('1.2.3-rc.5').finalize_version())
        '1.2.3'
        """
        cls = type(self)
        return cls(self.major, self.minor, self.patch)

    def match(self, match_expr: str) -> bool:
        """
        Compare self to match a match expression.

        :param match_expr: optional operator and version; valid operators are
              ``<``   smaller than
              ``>``   greater than
              ``>=``  greator or equal than
              ``<=``  smaller or equal than
              ``==``  equal
              ``!=``  not equal
        :return: True if the expression matches the version, otherwise False

        >>> semver.Version.parse("2.0.0").match(">=1.0.0")
        True
        >>> semver.Version.parse("1.0.0").match(">1.0.0")
        False
        >>> semver.Version.parse("4.0.4").match("4.0.4")
        True
        """
        prefix = match_expr[:2]
        if prefix in (">=", "<=", "==", "!="):
            match_version = match_expr[2:]
        elif prefix and prefix[0] in (">", "<"):
            prefix = prefix[0]
            match_version = match_expr[1:]
        elif match_expr and match_expr[0] in "0123456789":
            prefix = "=="
            match_version = match_expr
        else:
            raise ValueError(
                "match_expr parameter should be in format <op><ver>, "
                "where <op> is one of "
                "['<', '>', '==', '<=', '>=', '!=']. "
                "You provided: %r" % match_expr
            )

        possibilities_dict = {
            ">": (1,),
            "<": (-1,),
            "==": (0,),
            "!=": (-1, 1),
            ">=": (0, 1),
            "<=": (-1, 0),
        }

        possibilities = possibilities_dict[prefix]
        cmp_res = self.compare(match_version)

        return cmp_res in possibilities

    @classmethod
    def parse(
        cls: Type[T], version: String, optional_minor_and_patch: bool = False
    ) -> T:
        """
        Parse version string to a Version instance.

        .. versionchanged:: 2.11.0
           Changed method from static to classmethod to
           allow subclasses.
        .. versionchanged:: 3.0.0
           Added optional parameter ``optional_minor_and_patch`` to allow
           optional minor and patch parts.

        :param version: version string
        :param optional_minor_and_patch: if set to true, the version string to parse \
           can contain optional minor and patch parts. Optional parts are set to zero.
           By default (False), the version string to parse has to follow the semver
           specification.
        :return: a new :class:`Version` instance
        :raises ValueError: if version is invalid
        :raises TypeError: if version contains the wrong type

        >>> semver.Version.parse('3.4.5-pre.2+build.4')
        Version(major=3, minor=4, patch=5, \
prerelease='pre.2', build='build.4')
        """
        if isinstance(version, bytes):
            version = version.decode("UTF-8")
        elif not isinstance(version, String.__args__):  # type: ignore
            raise TypeError("not expecting type '%s'" % type(version))

        if optional_minor_and_patch:
            match = cls._REGEX_OPTIONAL_MINOR_AND_PATCH.match(version)
        else:
            match = cls._REGEX.match(version)
        if match is None:
            raise ValueError(f"{version} is not valid SemVer string")

        matched_version_parts: Dict[str, Any] = match.groupdict()
        if not matched_version_parts["minor"]:
            matched_version_parts["minor"] = 0
        if not matched_version_parts["patch"]:
            matched_version_parts["patch"] = 0

        return cls(**matched_version_parts)

    def replace(self, **parts: Union[int, Optional[str]]) -> "Version":
        """
        Replace one or more parts of a version and return a new :class:`Version`
        object, but leave self untouched.

        .. versionadded:: 2.9.0
           Added :func:`Version.replace`

        :param parts: the parts to be updated. Valid keys are:
          ``major``, ``minor``, ``patch``, ``prerelease``, or ``build``
        :return: the new :class:`~semver.version.Version` object with
          the changed parts
        :raises TypeError: if ``parts`` contain invalid keys
        """
        version = self.to_dict()
        version.update(parts)
        try:
            return type(self)(**version)  # type: ignore
        except TypeError:
            unknownkeys = set(parts) - set(self.to_dict())
            error = "replace() got %d unexpected keyword argument(s): %s" % (
                len(unknownkeys),
                ", ".join(unknownkeys),
            )
            raise TypeError(error)

    @classmethod
    def is_valid(cls, version: str) -> bool:
        """
        Check if the string is a valid semver version.

        .. versionadded:: 2.9.1

        .. versionchanged:: 3.0.0
           Renamed from :meth:`~semver.version.Version.isvalid`

        :param version: the version string to check
        :return: True if the version string is a valid semver version, False
                 otherwise.
        """
        try:
            cls.parse(version)
            return True
        except ValueError:
            return False

    def is_compatible(self, other: "Version") -> bool:
        """
        Check if current version is compatible with other version.

        The result is True, if either of the following is true:

        * both versions are equal, or
        * both majors are equal and higher than 0. Same for both minors.
          Both pre-releases are equal, or
        * both majors are equal and higher than 0. The minor of b's
          minor version is higher then a's. Both pre-releases are equal.

        The algorithm does *not* check patches.

        .. versionadded:: 3.0.0

        :param other: the version to check for compatibility
        :return: True, if ``other`` is compatible with the old version,
                 otherwise False

        >>> Version(1, 1, 0).is_compatible(Version(1, 0, 0))
        False
        >>> Version(1, 0, 0).is_compatible(Version(1, 1, 0))
        True
        """
        if not isinstance(other, Version):
            raise TypeError(f"Expected a Version type but got {type(other)}")

        # All major-0 versions should be incompatible with anything but itself
        if (0 == self.major == other.major) and (self[:4] != other[:4]):
            return False

        return (
            (self.major == other.major)
            and (other.minor >= self.minor)
            and (self.prerelease == other.prerelease)
        )


#: Keep the VersionInfo name for compatibility
VersionInfo = Version
