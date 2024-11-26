"""
Contains all deprecated functions.

.. autofunction: deprecated
"""
import inspect
import warnings
from functools import partial, wraps
from types import FrameType
from typing import Type, Callable, Optional, cast

from . import cli
from .version import Version
from ._types import Decorator, F


def deprecated(
    func: Optional[F] = None,
    *,
    replace: Optional[str] = None,
    version: Optional[str] = None,
    remove: Optional[str] = None,
    category: Type[Warning] = DeprecationWarning,
) -> Decorator:
    """
    Decorates a function to output a deprecation warning.

    :param func: the function to decorate
    :param replace: the function to replace (use the full qualified
        name like ``semver.version.Version.bump_major``.
    :param version: the first version when this function was deprecated.
    :param category: allow you to specify the deprecation warning class
        of your choice. By default, it's  :class:`DeprecationWarning`, but
        you can choose :class:`PendingDeprecationWarning` or a custom class.
    :return: decorated function which is marked as deprecated
    """

    if func is None:
        return partial(
            deprecated,
            replace=replace,
            version=version,
            remove=remove,
            category=category,
        )

    @wraps(func)
    def wrapper(*args, **kwargs) -> Callable[..., F]:
        msg_list = ["Function 'semver.{f}' is deprecated."]

        if version:
            msg_list.append("Deprecated since version {v}. ")

        if not remove:
            msg_list.append("This function will be removed in semver 3.")
        else:
            msg_list.append(str(remove))

        if replace:
            msg_list.append("Use {r!r} instead.")
        else:
            msg_list.append("Use the respective 'semver.Version.{r}' instead.")

        f = cast(F, func).__qualname__
        r = replace or f

        frame = cast(FrameType, cast(FrameType, inspect.currentframe()).f_back)

        msg = " ".join(msg_list)
        warnings.warn_explicit(
            msg.format(f=f, r=r, v=version),
            category=category,
            filename=inspect.getfile(frame.f_code),
            lineno=frame.f_lineno,
        )
        # As recommended in the Python documentation
        # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
        # better remove the interpreter stack:
        del frame
        return func(*args, **kwargs)  # type: ignore

    return wrapper


@deprecated(
    version="3.0.0",
    remove="Still under investigation, see #258.",
    category=PendingDeprecationWarning,
)
def compare(ver1: str, ver2: str) -> int:
    """
    Compare two versions strings.

    .. deprecated:: 3.0.0
       The situation of this function is unclear and it might
       disappear in the future.
       If possible, use :meth:`semver.version.Version.compare`.
       See :gh:`258` for details.

    :param ver1: first version string
    :param ver2: second version string
    :return: The return value is negative if ver1 < ver2,
             zero if ver1 == ver2 and strictly positive if ver1 > ver2

    >>> semver.compare("1.0.0", "2.0.0")
    -1
    >>> semver.compare("2.0.0", "1.0.0")
    1
    >>> semver.compare("2.0.0", "2.0.0")
    0
    """
    return Version.parse(ver1).compare(ver2)


@deprecated(version="2.10.0")
def parse(version):
    """
    Parse version to major, minor, patch, pre-release, build parts.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.parse` instead.

    :param version: version string
    :return: dictionary with the keys 'build', 'major', 'minor', 'patch',
             and 'prerelease'. The prerelease or build keys can be None
             if not provided
    :rtype: dict

    >>> ver = semver.parse('3.4.5-pre.2+build.4')
    >>> ver['major']
    3
    >>> ver['minor']
    4
    >>> ver['patch']
    5
    >>> ver['prerelease']
    'pre.2'
    >>> ver['build']
    'build.4'
    """
    return Version.parse(version).to_dict()


@deprecated(replace="semver.version.Version.parse", version="2.10.0")
def parse_version_info(version):
    """
    Parse version string to a Version instance.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.parse` instead.
    .. versionadded:: 2.7.2
       Added :func:`semver.parse_version_info`

    :param version: version string
    :return: a :class:`VersionInfo` instance

    >>> version_info = semver.Version.parse("3.4.5-pre.2+build.4")
    >>> version_info.major
    3
    >>> version_info.minor
    4
    >>> version_info.patch
    5
    >>> version_info.prerelease
    'pre.2'
    >>> version_info.build
    'build.4'
    """
    return Version.parse(version)


@deprecated(version="2.10.0")
def match(version, match_expr):
    """
    Compare two versions strings through a comparison.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.match` instead.

    :param str version: a version string
    :param str match_expr: operator and version; valid operators are
          <   smaller than
          >   greater than
          >=  greator or equal than
          <=  smaller or equal than
          ==  equal
          !=  not equal
    :return: True if the expression matches the version, otherwise False
    :rtype: bool

    >>> semver.match("2.0.0", ">=1.0.0")
    True
    >>> semver.match("1.0.0", ">1.0.0")
    False
    """
    ver = Version.parse(version)
    return ver.match(match_expr)


@deprecated(replace="max", version="2.10.2")
def max_ver(ver1, ver2):
    """
    Returns the greater version of two versions strings.

    .. deprecated:: 2.10.2
       Use :func:`max` instead.

    :param ver1: version string 1
    :param ver2: version string 2
    :return: the greater version of the two
    :rtype: :class:`Version`

    >>> semver.max_ver("1.0.0", "2.0.0")
    '2.0.0'
    """
    return str(max(ver1, ver2, key=Version.parse))


@deprecated(replace="min", version="2.10.2")
def min_ver(ver1, ver2):
    """
    Returns the smaller version of two versions strings.

    .. deprecated:: 2.10.2
       Use Use :func:`min` instead.

    :param ver1: version string 1
    :param ver2: version string 2
    :return: the smaller version of the two
    :rtype: :class:`Version`

    >>> semver.min_ver("1.0.0", "2.0.0")
    '1.0.0'
    """
    return str(min(ver1, ver2, key=Version.parse))


@deprecated(replace="str(versionobject)", version="2.10.0")
def format_version(major, minor, patch, prerelease=None, build=None):
    """
    Format a version string according to the Semantic Versioning specification.

    .. deprecated:: 2.10.0
       Use ``str(Version(VERSION)`` instead.

    :param int major: the required major part of a version
    :param int minor: the required minor part of a version
    :param int patch: the required patch part of a version
    :param str prerelease: the optional prerelease part of a version
    :param str build: the optional build part of a version
    :return: the formatted string
    :rtype: str

    >>> semver.format_version(3, 4, 5, 'pre.2', 'build.4')
    '3.4.5-pre.2+build.4'
    """
    return str(Version(major, minor, patch, prerelease, build))


@deprecated(version="2.10.0")
def bump_major(version):
    """
    Raise the major part of the version string.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.bump_major` instead.

    :param: version string
    :return: the raised version string
    :rtype: str

    >>> semver.bump_major("3.4.5")
    '4.0.0'
    """
    return str(Version.parse(version).bump_major())


@deprecated(version="2.10.0")
def bump_minor(version):
    """
    Raise the minor part of the version string.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.bump_minor` instead.

    :param: version string
    :return: the raised version string
    :rtype: str

    >>> semver.bump_minor("3.4.5")
    '3.5.0'
    """
    return str(Version.parse(version).bump_minor())


@deprecated(version="2.10.0")
def bump_patch(version):
    """
    Raise the patch part of the version string.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.bump_patch` instead.

    :param: version string
    :return: the raised version string
    :rtype: str

    >>> semver.bump_patch("3.4.5")
    '3.4.6'
    """
    return str(Version.parse(version).bump_patch())


@deprecated(version="2.10.0")
def bump_prerelease(version, token="rc"):
    """
    Raise the prerelease part of the version string.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.bump_prerelease` instead.

    :param version: version string
    :param token: defaults to 'rc'
    :return: the raised version string
    :rtype: str

    >>> semver.bump_prerelease('3.4.5', 'dev')
    '3.4.5-dev.1'
    """
    return str(Version.parse(version).bump_prerelease(token))


@deprecated(version="2.10.0")
def bump_build(version, token="build"):
    """
    Raise the build part of the version string.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.bump_build` instead.

    :param version: version string
    :param token: defaults to 'build'
    :return: the raised version string
    :rtype: str

    >>> semver.bump_build('3.4.5-rc.1+build.9')
    '3.4.5-rc.1+build.10'
    """
    return str(Version.parse(version).bump_build(token))


@deprecated(version="2.10.0")
def finalize_version(version):
    """
    Remove any prerelease and build metadata from the version string.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.finalize_version` instead.

    .. versionadded:: 2.7.9
       Added :func:`finalize_version`

    :param version: version string
    :return: the finalized version string
    :rtype: str

    >>> semver.finalize_version('1.2.3-rc.5')
    '1.2.3'
    """
    verinfo = Version.parse(version)
    return str(verinfo.finalize_version())


@deprecated(version="2.10.0")
def replace(version, **parts):
    """
    Replace one or more parts of a version and return the new string.

    .. deprecated:: 2.10.0
       Use :meth:`~semver.version.Version.replace` instead.
    .. versionadded:: 2.9.0
       Added :func:`replace`

    :param version: the version string to replace
    :param parts: the parts to be updated. Valid keys are:
      ``major``, ``minor``, ``patch``, ``prerelease``, or ``build``
    :return: the replaced version string
    :raises TypeError: if ``parts`` contains invalid keys

    >>> import semver
    >>> semver.replace("1.2.3", major=2, patch=10)
    '2.2.10'
    """
    return str(Version.parse(version).replace(**parts))


# CLI
cmd_bump = deprecated(cli.cmd_bump, replace="semver.cli.cmd_bump", version="3.0.0")
cmd_check = deprecated(cli.cmd_check, replace="semver.cli.cmd_check", version="3.0.0")
cmd_compare = deprecated(
    cli.cmd_compare, replace="semver.cli.cmd_compare", version="3.0.0"
)
cmd_nextver = deprecated(
    cli.cmd_nextver, replace="semver.cli.cmd_nextver", version="3.0.0"
)
createparser = deprecated(
    cli.createparser, replace="semver.cli.createparser", version="3.0.0"
)
process = deprecated(cli.process, replace="semver.cli.process", version="3.0.0")
main = deprecated(cli.main, replace="semver.cli.main", version="3.0.0")
