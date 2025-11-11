__all__ = [
    "bump_version",
    "check_version",
    "get_version",
    "serialize_pep440",
    "serialize_pvp",
    "serialize_semver",
    "Style",
    "Vcs",
    "Version",
]

import copy
import datetime as dt
import inspect
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections import OrderedDict
from enum import Enum
from functools import total_ordering
from pathlib import Path
from typing import (
    Any,
    Callable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from xml.etree import ElementTree

VERSION_SOURCE_PATTERN = r"""
    (?x)                                                        (?# ignore whitespace)
    ^v((?P<epoch>\d+)!)?(?P<base>\d+(\.\d+)*)                   (?# v1.2.3 or v1!2000.1.2)
    ([-._]?((?P<stage>[a-zA-Z]+)[-._]?(?P<revision>\d+)?))?     (?# b0)
    (\+(?P<tagged_metadata>.+))?$                               (?# +linux)
""".strip()

# Preserve old/private name for now in case it exists in the wild
_VERSION_PATTERN = VERSION_SOURCE_PATTERN

_VALID_PEP440 = r"""
    (?x)
    ^(\d+!)?
    \d+(\.\d+)*
    ((a|b|rc)\d+)?
    (\.post\d+)?
    (\.dev\d+)?
    (\+([a-zA-Z0-9]|[a-zA-Z0-9]{2}|[a-zA-Z0-9][a-zA-Z0-9.]+[a-zA-Z0-9]))?$
""".strip()
_VALID_SEMVER = r"""
    (?x)
    ^\d+\.\d+\.\d+
    (\-[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*)?
    (\+[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*)?$
""".strip()
_VALID_PVP = r"^\d+(\.\d+)*(-[a-zA-Z0-9]+)*$"

_TIMESTAMP_GENERIC = "%Y-%m-%dT%H:%M:%S.%f%z"
_TIMESTAMP_GENERIC_SPACE = "%Y-%m-%d %H:%M:%S.%f%z"
_TIMESTAMP_GIT_ISO_STRICT = "%Y-%m-%dT%H:%M:%S%z"
_TIMESTAMP_GIT_ISO = "%Y-%m-%d %H:%M:%S %z"

_T = TypeVar("_T")


class Style(Enum):
    """
    Standard styles for serializing a version.
    """

    Pep440 = "pep440"
    """PEP 440"""
    SemVer = "semver"
    """Semantic Versioning"""
    Pvp = "pvp"
    """Haskell Package Versioning Policy"""


class Vcs(Enum):
    """
    Version control systems.
    """

    Any = "any"
    """Automatically determine the VCS."""
    Git = "git"
    """Git"""
    Mercurial = "mercurial"
    """Mercurial"""
    Darcs = "darcs"
    """Darcs"""
    Subversion = "subversion"
    """Subversion"""
    Bazaar = "bazaar"
    """Bazaar"""
    Fossil = "fossil"
    """Fossil"""
    Pijul = "pijul"
    """Pijul"""


class Pattern(Enum):
    """
    Regular expressions used to parse tags as versions.
    """

    Default = "default"
    """Default pattern, including `v` prefix."""
    DefaultUnprefixed = "default-unprefixed"
    """Default pattern, but without `v` prefix."""

    def regex(self, prefix: Optional[str] = None) -> str:
        """
        Get the regular expression for this preset pattern.

        :param prefix: Insert this after the pattern's start anchor (`^`).
        :returns: Regular expression.
        """
        variants = {
            Pattern.Default: VERSION_SOURCE_PATTERN,
            Pattern.DefaultUnprefixed: VERSION_SOURCE_PATTERN.replace("^v", "^v?", 1),
        }

        out = variants[self]
        if prefix:
            out = out.replace("^", "^{}".format(prefix), 1)

        return out

    @staticmethod
    def parse(pattern: Union[str, "Pattern"], prefix: Optional[str] = None) -> str:
        """
        Parse a pattern string into a regular expression.

        If the pattern contains the capture group `?P<base>`, then it is
        returned as-is. Otherwise, it is interpreted as a variant of the
        `Pattern` enum.

        :param pattern: Pattern to parse.
        :param prefix: Insert this after the pattern's start anchor (`^`).
        :returns: Regular expression.
        """
        if isinstance(pattern, str) and "?P<base>" in pattern:
            if prefix:
                return pattern.replace("^", "^{}".format(prefix), 1)
            else:
                return pattern

        try:
            pattern = Pattern(pattern)
        except ValueError:
            raise ValueError(
                _pattern_error(
                    (
                        "The pattern does not contain the capture group '?P<base>'"
                        " and is not a known preset like '{}'".format(Pattern.Default.value)
                    ),
                    pattern,
                )
            )
        return pattern.regex(prefix)


class Concern(Enum):
    """
    A concern/warning discovered while producing the version.
    """

    ShallowRepository = "shallow-repository"
    """Repository does not contain full history"""

    def message(self) -> str:
        """
        Produce a human-readable description of the concern.

        :returns: Concern description.
        """

        if self == Concern.ShallowRepository:
            return "This is a shallow repository, so Dunamai may not produce the correct version."
        else:
            return ""


def _pattern_error(primary: str, pattern: Union[str, Pattern], tags: Optional[Sequence[str]] = None) -> str:
    parts = [primary, "Pattern:\n{}".format(pattern)]

    if tags is not None:
        parts.append("Tags:\n{}".format(tags))

    return "\n\n".join(parts)


def _run_cmd(
    command: str,
    where: Optional[Path],
    codes: Sequence[int] = (0,),
    shell: bool = False,
    env: Optional[dict] = None,
) -> Tuple[int, str]:
    result = subprocess.run(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(where) if where is not None else None,
        shell=shell,
        env=env,
    )
    output = result.stdout.decode().strip()
    if codes and result.returncode not in codes:
        raise RuntimeError("The command '{}' returned code {}. Output:\n{}".format(command, result.returncode, output))
    return (result.returncode, output)


_MatchedVersionPattern = NamedTuple(
    "_MatchedVersionPattern",
    [
        ("matched_tag", str),
        ("base", str),
        ("stage_revision", Optional[Tuple[str, Optional[int]]]),
        ("newer_tags", Sequence[str]),
        ("tagged_metadata", Optional[str]),
        ("epoch", Optional[int]),
    ],
)


def _match_version_pattern(
    pattern: Union[str, Pattern],
    sources: Sequence[str],
    latest_source: bool,
    strict: bool,
    pattern_prefix: Optional[str],
) -> Optional[_MatchedVersionPattern]:
    """
    :returns: Tuple of:
        * matched tag
        * base segment
        * tuple of:
          * stage
          * revision
        * any newer unmatched tags
        * tagged_metadata matched section
    """
    pattern_match = None
    base = None
    stage_revision = None
    newer_unmatched_tags = []
    tagged_metadata = None
    epoch = None  # type: Optional[Union[str, int]]

    pattern = Pattern.parse(pattern, pattern_prefix)

    for source in sources[:1] if latest_source else sources:
        try:
            pattern_match = re.search(pattern, source)
        except re.error as e:
            raise re.error(
                _pattern_error(
                    "The pattern is an invalid regular expression: {}".format(e.msg),  # type: ignore
                    pattern,
                ),
                e.pattern,  # type: ignore
                e.pos,  # type: ignore
            )
        if pattern_match is None:
            newer_unmatched_tags.append(source)
            continue
        try:
            base = pattern_match.group("base")
            if base is not None:
                break
        except IndexError:
            raise ValueError(_pattern_error("The pattern did not include required capture group 'base'", pattern))
    if pattern_match is None or base is None:
        if latest_source:
            raise ValueError(
                _pattern_error(
                    "The pattern did not match the latest tag '{}'".format(sources[0]),
                    pattern,
                    sources,
                )
            )
        elif strict:
            raise ValueError(_pattern_error("The pattern did not match any tags", pattern, sources))
        else:
            return None

    stage = pattern_match.groupdict().get("stage")
    revision = pattern_match.groupdict().get("revision")
    tagged_metadata = pattern_match.groupdict().get("tagged_metadata")
    epoch = pattern_match.groupdict().get("epoch")
    if stage is not None:
        try:
            stage_revision = (stage, None if revision is None else int(revision))
        except ValueError:
            raise ValueError("Revision '{}' is not a valid number".format(revision))
    if epoch is not None:
        try:
            epoch = int(epoch)
        except ValueError:
            raise ValueError("Epoch '{}' is not a valid number".format(epoch))

    return _MatchedVersionPattern(source, base, stage_revision, newer_unmatched_tags, tagged_metadata, epoch)


def _blank(value: Optional[_T], default: _T) -> _T:
    return value if value is not None else default


def _escape_branch(value: str, replacement: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", replacement, value)


def _equal_if_set(x: _T, y: Optional[_T], unset: Sequence[Any] = (None,)) -> bool:
    if y in unset:
        return True
    return x == y


def _get_git_version() -> List[int]:
    _, msg = _run_cmd("git version", where=None)
    result = re.search(r"git version (\d+(\.\d+)*)", msg.strip())
    if result is not None:
        parts = result.group(1).split(".")
        return [int(x) for x in parts]
    return []


def _git_log(git_version: List[int]) -> str:
    if git_version < [2, 10]:
        return "git log"
    else:
        return "git -c log.showsignature=false log"


def _detect_vcs(expected_vcs: Optional[Vcs], path: Optional[Path]) -> Vcs:
    checks = OrderedDict(
        [
            (Vcs.Git, "git status"),
            (Vcs.Mercurial, "hg status"),
            (Vcs.Darcs, "darcs log"),
            (Vcs.Subversion, "svn log"),
            (Vcs.Bazaar, "bzr status"),
            (Vcs.Fossil, "fossil status"),
            (Vcs.Pijul, "pijul log"),
        ]
    )

    dubious_ownership_flag = "detected dubious ownership"
    dubious_ownership_error = "Detected Git repository, but failed because of dubious ownership"

    if expected_vcs:
        command = checks[expected_vcs]
        program = command.split()[0]
        if not shutil.which(program):
            raise RuntimeError("Unable to find '{}' program".format(program))
        code, msg = _run_cmd(command, path, codes=[])
        if code != 0:
            if expected_vcs == Vcs.Git and dubious_ownership_flag in msg:
                raise RuntimeError(dubious_ownership_error)
            raise RuntimeError("This does not appear to be a {} project".format(expected_vcs.value.title()))
        return expected_vcs
    else:
        disproven = []
        unavailable = []
        for vcs, command in checks.items():
            if shutil.which(command.split()[0]):
                code, msg = _run_cmd(command, path, codes=[])
                if code == 0:
                    return vcs
                elif vcs == Vcs.Git and dubious_ownership_flag in msg:
                    raise RuntimeError(dubious_ownership_error)
                disproven.append(vcs.name)
            else:
                unavailable.append(vcs.name)

        error_parts = ["Unable to detect version control system."]
        if disproven:
            error_parts.append("Checked: {}.".format(", ".join(disproven)))
        if unavailable:
            error_parts.append("Not installed: {}.".format(", ".join(unavailable)))
        raise RuntimeError(" ".join(error_parts))


def _detect_vcs_from_archival(path: Optional[Path]) -> Optional[Vcs]:
    archival = _find_higher_file(".git_archival.json", path, ".git")
    if archival is not None:
        content = archival.read_text("utf8")
        if "$Format:" not in content:
            return Vcs.Git

    archival = _find_higher_file(".hg_archival.txt", path, ".hg")
    if archival is not None:
        return Vcs.Mercurial

    return None


def _find_higher_file(name: str, start: Optional[Path], limit: Optional[str] = None) -> Optional[Path]:
    """
    :param name: Bare name of a file we'd like to find.
    :param limit: Give up if we find a file/folder with this name.
    :param start: Begin recursing from this folder (default: `.`).
    """

    if start is None:
        start = Path.cwd()
    for level in [start, *start.parents]:
        if (level / name).is_file():
            return level / name
        if limit is not None and (level / limit).exists():
            return None
    return None


class _GitRefInfo:
    """
    This assumes Git 2.7+.
    """

    def __init__(self, ref: str, commit: str, creatordate: str, committerdate: str, taggerdate: str):
        self.fullref = ref
        self.commit = commit
        self.creatordate = self.normalize_git_dt(creatordate)
        self.committerdate = self.normalize_git_dt(committerdate)
        self.taggerdate = self.normalize_git_dt(taggerdate)
        self.tag_topo_lookup = {}  # type: Mapping[str, int]

    def with_tag_topo_lookup(self, lookup: Mapping[str, int]) -> "_GitRefInfo":
        self.tag_topo_lookup = lookup
        return self

    @staticmethod
    def normalize_git_dt(timestamp: str) -> Optional[dt.datetime]:
        if timestamp == "":
            return None
        else:
            return _parse_git_timestamp_iso_strict(timestamp)

    def __repr__(self):
        return ("_GitRefInfo(ref={!r}, commit={!r}, creatordate={!r}, committerdate={!r}, taggerdate={!r})").format(
            self.fullref, self.commit_offset, self.creatordate, self.committerdate, self.taggerdate
        )

    def best_date(self) -> Optional[dt.datetime]:
        if self.taggerdate is not None:
            return self.taggerdate
        elif self.committerdate is not None:
            return self.committerdate
        else:
            return self.creatordate

    def commit_offset(self) -> int:
        try:
            return self.tag_topo_lookup[self.fullref]
        except KeyError:
            # This can happen when the initial commit is both tagged and empty.
            return sys.maxsize

    def sort_key(self) -> Tuple[int, Optional[dt.datetime]]:
        return (-self.commit_offset(), self.best_date())

    def ref(self) -> str:
        return self.fullref.replace("refs/tags/", "")

    @staticmethod
    def normalize_tag_ref(ref: str) -> str:
        if ref.startswith("refs/tags/"):
            return ref
        else:
            return "refs/tags/{}".format(ref)

    @staticmethod
    def from_git_tag_topo_order(tag_branch: str, git_version: List[int], path: Optional[Path]) -> Mapping[str, int]:
        cmd = ('{} --simplify-by-decoration --topo-order --decorate=full {} "--format=%H%d"').format(
            _git_log(git_version), tag_branch
        )
        if git_version >= [2, 16]:
            cmd += " --decorate-refs=refs/tags/"
        code, logmsg = _run_cmd(cmd, path)

        filtered_lines = [x for x in logmsg.strip().splitlines(keepends=False) if " (" not in x or "tag: " in x]

        tag_lookup = {}
        for tag_offset, line in enumerate(filtered_lines):
            # lines have the pattern
            # <gitsha1>  (tag: refs/tags/v1.2.0b1, tag: refs/tags/v1.2.0)
            commit, _, tags = line.partition("(")
            commit = commit.strip()
            if tags:
                # remove trailing ')'
                tags = tags[:-1]
                taglist = [tag.strip() for tag in tags.split(", ") if tag.strip().startswith("tag: ")]
                taglist = [tag.split()[-1] for tag in taglist]
                taglist = [_GitRefInfo.normalize_tag_ref(tag) for tag in taglist]
                for tag in taglist:
                    tag_lookup[tag] = tag_offset
        return tag_lookup


@total_ordering
class Version:
    """
    A dynamic version.

    :ivar base: Release segment.
    :vartype base: str
    :ivar stage: Alphabetical part of prerelease segment.
    :vartype stage: Optional[str]
    :ivar revision: Numerical part of prerelease segment.
    :vartype revision: Optional[int]
    :ivar distance: Number of commits since the last tag.
    :vartype distance: int
    :ivar commit: Commit ID.
    :vartype commit: Optional[str]
    :ivar dirty: Whether there are uncommitted changes.
    :vartype dirty: Optional[bool]
    :ivar tagged_metadata: Any metadata segment from the tag itself.
    :vartype tagged_metadata: Optional[str]
    :ivar epoch: Optional PEP 440 epoch.
    :vartype epoch: Optional[int]
    :ivar branch: Name of the current branch.
    :vartype branch: Optional[str]
    :ivar timestamp: Timestamp of the current commit.
    :vartype timestamp: Optional[dt.datetime]
    :ivar concerns: Any concerns regarding the version.
    :vartype concerns: Optional[Set[Concern]]
    :ivar vcs: Version control system from which the version was detected.
    :vartype vcs: Vcs
    """

    def __init__(
        self,
        base: str,
        *,
        stage: Optional[Tuple[str, Optional[int]]] = None,
        distance: int = 0,
        commit: Optional[str] = None,
        dirty: Optional[bool] = None,
        tagged_metadata: Optional[str] = None,
        epoch: Optional[int] = None,
        branch: Optional[str] = None,
        timestamp: Optional[dt.datetime] = None,
        concerns: Optional[Set[Concern]] = None,
        # fmt: off
        vcs: Vcs = Vcs.Any
        # fmt: on
    ) -> None:
        """
        :param base: Release segment, such as 0.1.0.
        :param stage: Pair of release stage (e.g., "a", "alpha", "b", "rc")
            and an optional revision number.
        :param distance: Number of commits since the last tag.
        :param commit: Commit hash/identifier.
        :param dirty: True if the working directory does not match the commit.
        :param epoch: Optional PEP 440 epoch.
        :param branch: Name of the current branch.
        :param timestamp: Timestamp of the current commit.
        :param concerns: Any concerns regarding the version.
        """
        self.base = base
        self.stage = None
        self.revision = None
        if stage is not None:
            self.stage, self.revision = stage
        self.distance = distance
        self.commit = commit
        self.dirty = dirty
        self.tagged_metadata = tagged_metadata
        self.epoch = epoch
        self.branch = branch
        try:
            self.timestamp = timestamp.astimezone(dt.timezone.utc) if timestamp else None
        except ValueError:
            # Will fail for naive timestamps before Python 3.6.
            self.timestamp = timestamp
        self.concerns = concerns or set()
        self.vcs = vcs

        self._matched_tag = None  # type: Optional[str]
        self._newer_unmatched_tags = None  # type: Optional[Sequence[str]]
        self._smart_bumped = False

    def __str__(self) -> str:
        return self.serialize()

    def __repr__(self) -> str:
        return (
            "Version(base={!r}, stage={!r}, revision={!r}, distance={!r}, commit={!r},"
            " dirty={!r}, tagged_metadata={!r}, epoch={!r}, branch={!r}, timestamp={!r})"
        ).format(
            self.base,
            self.stage,
            self.revision,
            self.distance,
            self.commit,
            self.dirty,
            self.tagged_metadata,
            self.epoch,
            self.branch,
            self.timestamp,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise TypeError("Cannot compare Version with type {}".format(other.__class__.__qualname__))
        return (
            self.base == other.base
            and self.stage == other.stage
            and self.revision == other.revision
            and self.distance == other.distance
            and self.commit == other.commit
            and self.dirty == other.dirty
            and self.tagged_metadata == other.tagged_metadata
            and self.epoch == other.epoch
            and self.branch == other.branch
            and self.timestamp == other.timestamp
        )

    def _matches_partial(self, other: "Version") -> bool:
        """
        Compare this version to another version, but ignore None values in the other version.
        Distance is also ignored when `other.distance == 0`.

        :param other: The version to compare to.
        :returns: True if this version equals the other version.
        """
        return (
            _equal_if_set(self.base, other.base)
            and _equal_if_set(self.stage, other.stage)
            and _equal_if_set(self.revision, other.revision)
            and _equal_if_set(self.distance, other.distance, unset=[None, 0])
            and _equal_if_set(self.commit, other.commit)
            and _equal_if_set(self.dirty, other.dirty)
            and _equal_if_set(self.tagged_metadata, other.tagged_metadata)
            and _equal_if_set(self.epoch, other.epoch)
            and _equal_if_set(self.branch, other.branch)
            and _equal_if_set(self.timestamp, other.timestamp)
        )

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise TypeError("Cannot compare Version with type {}".format(other.__class__.__qualname__))

        import packaging.version as pv

        parsable = True
        try:
            us = pv.Version(self.serialize(metadata=False))
            them = pv.Version(other.serialize(metadata=False))
            if us < them:
                return True
            elif us > them:
                return False
        except Exception:
            parsable = False

        common_pairs = [
            (_blank(self.distance, 0), _blank(other.distance, 0)),
            (_blank(self.commit, ""), _blank(other.commit, "")),
            (bool(self.dirty), bool(other.dirty)),
            (_blank(self.tagged_metadata, ""), _blank(other.tagged_metadata, "")),
            (_blank(self.branch, ""), _blank(other.branch, "")),
            (
                _blank(self.timestamp, dt.datetime(1, 1, 1, 0, 0, 0)),
                _blank(other.timestamp, dt.datetime(1, 1, 1, 0, 0, 0)),
            ),
        ]

        if parsable:
            pairs = common_pairs
        else:
            pairs = [
                (_blank(self.epoch, 0), _blank(other.epoch, 0)),
                (pv.Version(self.base), pv.Version(other.base)),
                (_blank(self.stage, ""), _blank(other.stage, "")),
                (_blank(self.revision, 0), _blank(other.revision, 0)),
                *common_pairs,
            ]

        for (a, b) in pairs:
            if a < b:  # type: ignore
                return True
            elif a > b:  # type: ignore
                return False

        return False

    def serialize(
        self,
        metadata: Optional[bool] = None,
        dirty: bool = False,
        format: Optional[Union[str, Callable[["Version"], str]]] = None,
        style: Optional[Style] = None,
        bump: bool = False,
        tagged_metadata: bool = False,
        commit_prefix: Optional[str] = None,
        escape_with: Optional[str] = None,
    ) -> str:
        """
        Create a string from the version info.

        :param metadata: Metadata (commit ID, dirty flag) is normally included
            in the metadata/local version part only if the distance is nonzero.
            Set this to True to always include metadata even with no distance,
            or set it to False to always exclude it.
            This is ignored when `format` is used.
        :param dirty: Set this to True to include a dirty flag in the
            metadata if applicable. Inert when metadata=False.
            This is ignored when `format` is used.
        :param format: Custom output format. It is either a formatted string or a
            callback. In the string you can use substitutions, such as "v{base}"
            to get "v0.1.0". Available substitutions:

            * {base}
            * {stage}
            * {revision}
            * {distance}
            * {commit}
            * {dirty} which expands to either "dirty" or "clean"
            * {tagged_metadata}
            * {epoch}
            * {branch}
            * {branch_escaped} which omits any non-letter/number characters (or replaces via `escape_with`)
            * {timestamp} which expands to YYYYmmddHHMMSS as UTC
            * {major} (first part of `base` split on `.`, or 0)
            * {minor} (second part of `base` split on `.`, or 0)
            * {patch} (third part of `base` split on `.`, or 0)
        :param style: Built-in output formats. Will default to PEP 440 if not
            set and no custom format given. If you specify both a style and a
            custom format, then the format will be validated against the
            style's rules.
        :param bump: If true, increment the last part of the `base` by 1,
            unless `stage` is set, in which case either increment `revision`
            by 1 or set it to a default of 2 if there was no revision.
            Does nothing when on a commit with a version tag.
        :param tagged_metadata: If true, insert the `tagged_metadata` in the
            version as the first part of the metadata segment.
            This is ignored when `format` is used.
        :param commit_prefix: Add this prefix to the commit ID.
            This can be helpful when an all-numeric commit would be misinterpreted.
            For example, "g" is a common prefix for Git commits.
        :param escape_with: When escaping, replace with this substitution.
            The default is simply to remove invalid characters.
        :returns: Serialized version.
        """
        base = self.base
        revision = self.revision
        if bump:
            bumped = self.bump(smart=True)
            base = bumped.base
            revision = bumped.revision

        commit = self.commit
        if commit is not None and commit_prefix is not None:
            commit = "{}{}".format(commit_prefix, commit)

        if format is not None:
            if callable(format):
                new_version = copy.deepcopy(self)
                new_version.base = base
                new_version.revision = revision
                out = format(new_version)
            else:
                try:
                    base_parts = base.split(".")

                    out = format.format(
                        base=base,
                        stage=_blank(self.stage, ""),
                        revision=_blank(revision, ""),
                        distance=_blank(self.distance, ""),
                        commit=_blank(commit, ""),
                        tagged_metadata=_blank(self.tagged_metadata, ""),
                        dirty="dirty" if self.dirty else "clean",
                        epoch=_blank(self.epoch, ""),
                        branch=_blank(self.branch, ""),
                        branch_escaped=_escape_branch(_blank(self.branch, ""), escape_with or ""),
                        timestamp=self.timestamp.strftime("%Y%m%d%H%M%S") if self.timestamp else "",
                        major=base_parts[0] if len(base_parts) > 0 else "0",
                        minor=base_parts[1] if len(base_parts) > 1 else "0",
                        patch=base_parts[2] if len(base_parts) > 2 else "0",
                    )
                except KeyError as e:
                    raise KeyError("Format contains invalid placeholder: {}".format(e))
                except ValueError as e:
                    raise ValueError("Format is invalid: {}".format(e))
            if style is not None:
                check_version(out, style)
            return out

        if style is None:
            style = Style.Pep440
        out = ""

        meta_parts = []
        if metadata is not False:
            if tagged_metadata and self.tagged_metadata:
                meta_parts.append(self.tagged_metadata)
            if (metadata or self.distance > 0) and commit is not None:
                meta_parts.append(commit)
            if dirty and self.dirty:
                meta_parts.append("dirty")

        pre_parts = []
        if self.stage is not None:
            pre_parts.append(self.stage)
            if revision is not None:
                pre_parts.append(str(revision))
        if self.distance > 0:
            pre_parts.append("pre" if bump or self._smart_bumped else "post")
            pre_parts.append(str(self.distance))

        if style == Style.Pep440:
            stage = self.stage
            post = None
            dev = None
            if stage == "post":
                stage = None
                post = revision
            elif stage == "dev":
                stage = None
                dev = revision
            if self.distance > 0:
                if bump or self._smart_bumped:
                    if dev is None:
                        dev = self.distance
                    else:
                        dev += self.distance
                else:
                    if post is None and dev is None:
                        post = self.distance
                        dev = 0
                    elif dev is None:
                        dev = self.distance
                    else:
                        dev += self.distance

            out = serialize_pep440(
                base,
                stage=stage,
                revision=revision,
                post=post,
                dev=dev,
                metadata=meta_parts,
                epoch=self.epoch,
            )
        elif style == Style.SemVer:
            out = serialize_semver(base, pre=pre_parts, metadata=meta_parts)
        elif style == Style.Pvp:
            out = serialize_pvp(base, metadata=[*pre_parts, *meta_parts])

        check_version(out, style)
        return out

    @classmethod
    def parse(cls, version: str, pattern: Union[str, Pattern] = Pattern.Default) -> "Version":
        """
        Attempt to parse a string into a Version instance.

        This uses inexact heuristics, so its output may vary slightly between
        releases. Consider this a "best effort" conversion.

        :param version: Full version, such as 0.3.0a3+d7.gb6a9020.dirty.
        :param pattern: Regular expression matched against the version.
            Refer to `from_any_vcs` for more info.
        :returns: Parsed version.
        """
        normalized = version
        if not version.startswith("v") and pattern in [VERSION_SOURCE_PATTERN, Pattern.Default]:
            normalized = "v{}".format(version)

        failed = False
        try:
            matched_pattern = _match_version_pattern(pattern, [normalized], True, strict=True, pattern_prefix=None)
        except ValueError:
            failed = True

        if failed or matched_pattern is None:
            replaced = re.sub(r"(\.post(\d+)\.dev\d+)", r".dev\2", version, count=1)
            if replaced != version:
                alt = Version.parse(replaced, pattern)
                if alt.base != replaced:
                    return alt

            return cls(version)

        base = matched_pattern.base
        stage = matched_pattern.stage_revision
        distance = None
        commit = None
        dirty = None
        tagged_metadata = matched_pattern.tagged_metadata
        epoch = matched_pattern.epoch

        if tagged_metadata:
            pop = []  # type: list
            parts = tagged_metadata.split(".")

            for i, value in enumerate(parts):
                if dirty is None:
                    if value == "dirty":
                        dirty = True
                        pop.append(i)
                        continue
                    elif value == "clean":
                        dirty = False
                        pop.append(i)
                        continue
                if distance is None:
                    match = re.match(r"d?(\d+)", value)
                    if match:
                        distance = int(match.group(1))
                        pop.append(i)
                        continue
                if commit is None:
                    match = re.match(r"g?([\da-z]+)", value)
                    if match:
                        commit = match.group(1)
                        pop.append(i)
                        continue

            for i in reversed(sorted(pop)):
                parts.pop(i)

            tagged_metadata = ".".join(parts)

        if distance is None:
            distance = 0
        if tagged_metadata is not None and tagged_metadata.strip() == "":
            tagged_metadata = None

        if stage is not None and stage[0] == "dev" and stage[1] is not None:
            distance += stage[1]
            stage = None

        return cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
        )

    def bump(self, index: int = -1, increment: int = 1, smart: bool = False) -> "Version":
        """
        Increment the version.

        The base is bumped unless there is a stage defined, in which case,
        the revision is bumped instead.

        :param index: Numerical position to increment in the base.
            This follows Python indexing rules, so positive numbers start from
            the left side and count up from 0, while negative numbers start from
            the right side and count down from -1.
            Only has an effect when the base is bumped.
        :param increment: By how much to increment the relevant position.
        :param smart: If true, only bump when distance is not 0.
            This will also make `Version.serialize()` use pre-release formatting automatically,
            like calling `Version.serialize(bump=True)`.
        :returns: Bumped version.
        """
        bumped = copy.deepcopy(self)

        if smart:
            if bumped.distance == 0:
                return bumped
            bumped._smart_bumped = True

        if bumped.stage is None:
            bumped.base = bump_version(bumped.base, index, increment)
        else:
            if bumped.revision is None:
                bumped.revision = 2
            else:
                bumped.revision += increment
        return bumped

    @classmethod
    def _fallback(
        cls,
        strict: bool,
        *,
        stage: Optional[Tuple[str, Optional[int]]] = None,
        distance: int = 0,
        commit: Optional[str] = None,
        dirty: Optional[bool] = None,
        tagged_metadata: Optional[str] = None,
        epoch: Optional[int] = None,
        branch: Optional[str] = None,
        timestamp: Optional[dt.datetime] = None,
        concerns: Optional[Set[Concern]] = None,
        # fmt: off
        vcs: Vcs = Vcs.Any
        # fmt: on
    ):
        if strict:
            raise RuntimeError("No tags available and fallbacks disabled by strict mode")
        return cls(
            "0.0.0",
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            branch=branch,
            timestamp=timestamp,
            concerns=concerns,
            vcs=vcs,
        )

    @classmethod
    def from_git(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        tag_branch: Optional[str] = None,
        full_commit: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        ignore_untracked: bool = False,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on Git tags.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param tag_branch: Branch on which to find tags, if different than the
            current branch.
        :param full_commit: Get the full commit hash instead of the short form.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param ignore_untracked:
            Ignore untracked files when determining whether the repository is dirty.
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = Vcs.Git
        full_commit = full_commit or commit_length is not None
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_TRACE")}

        archival = _find_higher_file(".git_archival.json", path, ".git")
        if archival is not None:
            content = archival.read_text("utf8")
            if "$Format:" not in content:
                data = json.loads(content)

                if full_commit:
                    commit = data.get("hash-full")
                else:
                    commit = data.get("hash-short")

                if commit is not None:
                    commit = commit[:commit_length]

                timestamp = None
                raw_timestamp = data.get("timestamp")
                if raw_timestamp:
                    timestamp = _parse_git_timestamp_iso_strict(raw_timestamp)

                branch = None
                refs = data.get("refs")
                if refs:
                    parts = refs.split(" -> ")
                    if len(parts) == 2:
                        branch = parts[1].split(", ")[0]

                tag = None
                distance = 0
                dirty = None
                describe = data.get("describe")
                if describe:
                    if describe.endswith("-dirty"):
                        dirty = True
                        describe = describe[:-6]
                    else:
                        dirty = False
                    parts = describe.rsplit("-", 2)
                    tag = parts[0]
                    if len(parts) > 1:
                        distance = int(parts[1])

                if tag is None:
                    return cls._fallback(
                        strict,
                        distance=distance,
                        commit=commit,
                        dirty=dirty,
                        branch=branch,
                        timestamp=timestamp,
                        vcs=vcs,
                    )

                matched_pattern = _match_version_pattern(pattern, [tag], latest_tag, strict, pattern_prefix)
                if matched_pattern is None:
                    return cls._fallback(
                        strict,
                        distance=distance,
                        commit=commit,
                        dirty=dirty,
                        branch=branch,
                        timestamp=timestamp,
                        vcs=vcs,
                    )
                tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

                version = cls(
                    base,
                    stage=stage,
                    distance=distance,
                    commit=commit,
                    dirty=dirty,
                    tagged_metadata=tagged_metadata,
                    epoch=epoch,
                    branch=branch,
                    timestamp=timestamp,
                    vcs=vcs,
                )
                version._matched_tag = tag
                version._newer_unmatched_tags = unmatched
                return version

        _detect_vcs(vcs, path)
        concerns = set()  # type: Set[Concern]
        if tag_branch is None:
            tag_branch = "HEAD"

        git_version = _get_git_version()

        if git_version < [2, 15]:
            flag_file = _find_higher_file(".git/shallow", path)
            if flag_file:
                concerns.add(Concern.ShallowRepository)
        else:
            code, msg = _run_cmd("git rev-parse --is-shallow-repository", path, env=env)
            if msg.strip() == "true":
                concerns.add(Concern.ShallowRepository)

        if strict and concerns:
            raise RuntimeError("\n".join(x.message() for x in concerns))

        code, msg = _run_cmd("git symbolic-ref --short HEAD", path, codes=[0, 128], env=env)
        if code == 128:
            branch = None
        else:
            branch = msg

        code, msg = _run_cmd(
            '{} -n 1 --format="format:{}"'.format(_git_log(git_version), "%H" if full_commit else "%h"),
            path,
            codes=[0, 128],
            env=env,
        )
        if code == 128:
            return cls._fallback(strict, distance=0, dirty=True, branch=branch, concerns=concerns, vcs=vcs)
        commit = msg[:commit_length]

        timestamp = None
        if git_version < [2, 2]:
            code, msg = _run_cmd('{} -n 1 --pretty=format:"%ci"'.format(_git_log(git_version)), path, env=env)
            timestamp = _parse_git_timestamp_iso(msg)
        else:
            code, msg = _run_cmd('{} -n 1 --pretty=format:"%cI"'.format(_git_log(git_version)), path, env=env)
            timestamp = _parse_git_timestamp_iso_strict(msg)

        code, msg = _run_cmd("git describe --always --dirty", path, env=env)
        dirty = msg.endswith("-dirty")

        if not dirty and not ignore_untracked:
            code, msg = _run_cmd("git status --porcelain", path, env=env)
            if msg.strip() != "":
                dirty = True

        if git_version < [2, 7]:
            code, msg = _run_cmd(
                'git for-each-ref "refs/tags/**" --format "%(refname)" --sort -creatordate', path, env=env
            )
            if not msg:
                try:
                    code, msg = _run_cmd("git rev-list --count HEAD", path, env=env)
                    distance = int(msg)
                except Exception:
                    distance = 0
                return cls._fallback(
                    strict,
                    distance=distance,
                    commit=commit,
                    dirty=dirty,
                    branch=branch,
                    timestamp=timestamp,
                    concerns=concerns,
                    vcs=vcs,
                )
            tags = [line.replace("refs/tags/", "") for line in msg.splitlines()]
            matched_pattern = _match_version_pattern(pattern, tags, latest_tag, strict, pattern_prefix)
        else:
            code, msg = _run_cmd(
                'git for-each-ref "refs/tags/**" --merged {}'.format(tag_branch) + ' --format "%(refname)'
                "@{%(objectname)"
                "@{%(creatordate:iso-strict)"
                "@{%(*committerdate:iso-strict)"
                "@{%(taggerdate:iso-strict)"
                '"',
                path,
                env=env,
            )
            if not msg:
                try:
                    code, msg = _run_cmd("git rev-list --count HEAD", path, env=env)
                    distance = int(msg)
                except Exception:
                    distance = 0
                return cls._fallback(
                    strict,
                    distance=distance,
                    commit=commit,
                    dirty=dirty,
                    branch=branch,
                    timestamp=timestamp,
                    concerns=concerns,
                    vcs=vcs,
                )

            detailed_tags = []  # type: List[_GitRefInfo]
            tag_topo_lookup = _GitRefInfo.from_git_tag_topo_order(tag_branch, git_version, path)

            for line in msg.strip().splitlines():
                parts = line.split("@{")
                if len(parts) != 5:
                    continue
                detailed_tags.append(_GitRefInfo(*parts).with_tag_topo_lookup(tag_topo_lookup))

            tags = [t.ref() for t in sorted(detailed_tags, key=lambda x: x.sort_key(), reverse=True)]
            matched_pattern = _match_version_pattern(pattern, tags, latest_tag, strict, pattern_prefix)

        if matched_pattern is None:
            try:
                code, msg = _run_cmd("git rev-list --count HEAD", path, env=env)
                distance = int(msg)
            except Exception:
                distance = 0

            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                concerns=concerns,
                vcs=vcs,
            )
        tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

        code, msg = _run_cmd("git rev-list --count refs/tags/{}..HEAD".format(tag), path, env=env)
        distance = int(msg)

        version = cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            branch=branch,
            timestamp=timestamp,
            concerns=concerns,
            vcs=vcs,
        )
        version._matched_tag = tag
        version._newer_unmatched_tags = unmatched
        return version

    @classmethod
    def from_mercurial(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        full_commit: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on Mercurial tags.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param full_commit: Get the full commit hash instead of the short form.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = Vcs.Mercurial
        full_commit = full_commit or commit_length is not None

        archival = _find_higher_file(".hg_archival.txt", path, ".hg")
        if archival is not None:
            content = archival.read_text("utf8")
            data = {}
            for line in content.splitlines():
                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue
                data[parts[0].strip()] = parts[1].strip()

            tag = data.get("latesttag")
            # The distance is 1 on a new repo or on a tagged commit.
            distance = int(data.get("latesttagdistance", 1)) - 1
            commit = data.get("node")
            if commit is not None:
                commit = commit[:commit_length]
            branch = data.get("branch")

            if tag is None or tag == "null":
                return cls._fallback(strict, distance=distance, commit=commit, branch=branch, vcs=vcs)

            all_tags_file = _find_higher_file(".hgtags", path, ".hg")
            if all_tags_file is None:
                all_tags = [tag]
            else:
                all_tags = []
                all_tags_content = all_tags_file.read_text("utf8")
                for line in reversed(all_tags_content.splitlines()):
                    parts = line.split(" ", 1)
                    if len(parts) != 2:
                        continue
                    all_tags.append(parts[1])

            matched_pattern = _match_version_pattern(pattern, all_tags, latest_tag, strict, pattern_prefix)
            if matched_pattern is None:
                return cls._fallback(
                    strict,
                    distance=distance,
                    commit=commit,
                    branch=branch,
                    vcs=vcs,
                )
            tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

            version = cls(
                base,
                stage=stage,
                distance=distance,
                commit=commit,
                tagged_metadata=tagged_metadata,
                epoch=epoch,
                branch=branch,
                vcs=vcs,
            )
            version._matched_tag = tag
            version._newer_unmatched_tags = unmatched
            return version

        _detect_vcs(vcs, path)

        code, msg = _run_cmd("hg summary", path)
        dirty = "commit: (clean)" not in msg.splitlines()

        code, msg = _run_cmd("hg branch", path)
        branch = msg

        code, msg = _run_cmd('hg id --template "{}"'.format("{id}" if full_commit else "{id|short}"), path)
        commit = msg[:commit_length] if set(msg) != {"0"} else None

        code, msg = _run_cmd('hg log --limit 1 --template "{date|rfc3339date}"', path)
        timestamp = _parse_git_timestamp_iso_strict(msg) if msg != "" else None

        code, msg = _run_cmd(
            'hg log -r "sort(tag(){}, -rev)" --template "{{join(tags, \':\')}}\\n"'.format(
                " and ancestors({})".format(commit) if commit is not None else ""
            ),
            path,
        )
        if not msg:
            try:
                code, msg = _run_cmd("hg id --num --rev tip", path)
                distance = int(msg) + 1
            except Exception:
                distance = 0
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )
        tags = [tag for tags in [line.split(":") for line in msg.splitlines()] for tag in tags]

        matched_pattern = _match_version_pattern(pattern, tags, latest_tag, strict, pattern_prefix)
        if matched_pattern is None:
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )
        tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

        code, msg = _run_cmd('hg log -r "{0}::{1} - {0}" --template "."'.format(tag, commit), path)
        # The tag itself is in the list, so offset by 1.
        distance = max(len(msg) - 1, 0)

        version = cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            branch=branch,
            timestamp=timestamp,
            vcs=vcs,
        )
        version._matched_tag = tag
        version._newer_unmatched_tags = unmatched
        return version

    @classmethod
    def from_darcs(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on Darcs tags.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = Vcs.Darcs
        _detect_vcs(vcs, path)

        code, msg = _run_cmd("darcs status", path, codes=[0, 1])
        dirty = msg != "No changes!"

        code, msg = _run_cmd("darcs log --last 1 --xml-output", path)
        root = ElementTree.fromstring(msg)
        if len(root) == 0:
            commit = None
            timestamp = None
        else:
            commit = root[0].attrib["hash"]
            if commit is not None:
                commit = commit[:commit_length]
            timestamp = dt.datetime.strptime(root[0].attrib["date"] + "+0000", "%Y%m%d%H%M%S%z")

        code, msg = _run_cmd("darcs show tags", path)
        if not msg:
            try:
                code, msg = _run_cmd("darcs log --count", path)
                distance = int(msg)
            except Exception:
                distance = 0
            return cls._fallback(strict, distance=distance, commit=commit, dirty=dirty, timestamp=timestamp, vcs=vcs)
        tags = msg.splitlines()

        matched_pattern = _match_version_pattern(pattern, tags, latest_tag, strict, pattern_prefix)
        if matched_pattern is None:
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                timestamp=timestamp,
                vcs=vcs,
            )
        tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

        code, msg = _run_cmd("darcs log --from-tag {} --count".format(tag), path)
        # The tag itself is in the list, so offset by 1.
        distance = int(msg) - 1

        version = cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            timestamp=timestamp,
            vcs=vcs,
        )
        version._matched_tag = tag
        version._newer_unmatched_tags = unmatched
        return version

    @classmethod
    def from_subversion(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        tag_dir: str = "tags",
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on Subversion tags.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param tag_dir: Location of tags relative to the root.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = Vcs.Subversion
        _detect_vcs(vcs, path)

        tag_dir = tag_dir.strip("/")

        code, msg = _run_cmd("svn status", path)
        dirty = bool(msg)

        code, msg = _run_cmd("svn info --show-item repos-root-url", path)
        url = msg.strip("/")

        code, msg = _run_cmd("svn info --show-item revision", path)
        if not msg or msg == "0":
            commit = None
        else:
            commit = msg[:commit_length]

        timestamp = None
        if commit:
            code, msg = _run_cmd("svn info --show-item last-changed-date", path)
            timestamp = _parse_timestamp(msg)

        if not commit:
            return cls._fallback(strict, distance=0, commit=commit, dirty=dirty, timestamp=timestamp, vcs=vcs)
        code, msg = _run_cmd('svn ls -v -r {} "{}/{}"'.format(commit, url, tag_dir), path)
        lines = [line.split(maxsplit=5) for line in msg.splitlines()[1:]]
        tags_to_revs = {line[-1].strip("/"): int(line[0]) for line in lines}
        if not tags_to_revs:
            try:
                distance = int(commit)
            except Exception:
                distance = 0
            return cls._fallback(strict, distance=distance, commit=commit, dirty=dirty, timestamp=timestamp, vcs=vcs)
        tags_to_sources_revs = {}
        for tag, rev in tags_to_revs.items():
            code, msg = _run_cmd('svn log -v "{}/{}/{}" --stop-on-copy'.format(url, tag_dir, tag), path)
            for line in msg.splitlines():
                match = re.search(r"A /{}/{} \(from .+?:(\d+)\)".format(tag_dir, tag), line)
                if match:
                    source = int(match.group(1))
                    tags_to_sources_revs[tag] = (source, rev)
        tags = sorted(tags_to_sources_revs, key=lambda x: tags_to_sources_revs[x], reverse=True)

        matched_pattern = _match_version_pattern(pattern, tags, latest_tag, strict, pattern_prefix)
        if matched_pattern is None:
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                timestamp=timestamp,
                vcs=vcs,
            )
        tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

        source, rev = tags_to_sources_revs[tag]
        # The tag itself is in the list, so offset by 1.
        distance = int(commit) - 1 - source

        version = cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            timestamp=timestamp,
            vcs=vcs,
        )
        version._matched_tag = tag
        version._newer_unmatched_tags = unmatched
        return version

    @classmethod
    def from_bazaar(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on Bazaar tags.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = Vcs.Bazaar
        _detect_vcs(vcs, path)

        code, msg = _run_cmd("bzr status", path)
        dirty = msg != ""

        code, msg = _run_cmd("bzr log --limit 1", path)
        commit = None
        branch = None
        timestamp = None
        for line in msg.splitlines():
            info = line.split("revno: ", maxsplit=1)
            if len(info) == 2:
                commit = info[1][:commit_length]

            info = line.split("branch nick: ", maxsplit=1)
            if len(info) == 2:
                branch = info[1]

            info = line.split("timestamp: ", maxsplit=1)
            if len(info) == 2:
                timestamp = dt.datetime.strptime(info[1], "%a %Y-%m-%d %H:%M:%S %z")

        code, msg = _run_cmd("bzr tags", path)
        if not msg or not commit:
            try:
                distance = int(commit) if commit is not None else 0
            except Exception:
                distance = 0
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )
        tags_to_revs = {line.split()[0]: int(line.split()[1]) for line in msg.splitlines() if line.split()[1] != "?"}
        tags = [x[1] for x in sorted([(v, k) for k, v in tags_to_revs.items()], reverse=True)]

        matched_pattern = _match_version_pattern(pattern, tags, latest_tag, strict, pattern_prefix)
        if matched_pattern is None:
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )
        tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

        distance = int(commit) - tags_to_revs[tag]

        version = cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            branch=branch,
            timestamp=timestamp,
            vcs=vcs,
        )
        version._matched_tag = tag
        version._newer_unmatched_tags = unmatched
        return version

    @classmethod
    def from_fossil(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on Fossil tags.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag for a pattern
            match. If false, keep looking at tags until there is a match.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = Vcs.Fossil
        _detect_vcs(vcs, path)

        code, msg = _run_cmd("fossil changes --differ", path)
        dirty = bool(msg)

        code, msg = _run_cmd("fossil branch current", path)
        branch = msg

        code, msg = _run_cmd("fossil sql \"SELECT value FROM vvar WHERE name = 'checkout-hash' LIMIT 1\"", path)
        commit = msg.strip("'")[:commit_length]

        code, msg = _run_cmd(
            'fossil sql "'
            "SELECT DATETIME(mtime) FROM event JOIN blob ON event.objid=blob.rid WHERE type = 'ci'"
            " AND uuid = (SELECT value FROM vvar WHERE name = 'checkout-hash' LIMIT 1) LIMIT 1\"",
            path,
        )
        timestamp = dt.datetime.strptime(msg.strip("'") + "+0000", "%Y-%m-%d %H:%M:%S%z")

        code, msg = _run_cmd("fossil sql \"SELECT count() FROM event WHERE type = 'ci'\"", path)
        # The repository creation itself counts as a commit.
        total_commits = int(msg) - 1
        if total_commits <= 0:
            return cls._fallback(
                strict,
                distance=0,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )

        # Based on `compute_direct_ancestors` from descendants.c in the
        # Fossil source code:
        query = """
            CREATE TEMP TABLE IF NOT EXISTS
                dunamai_ancestor(
                    rid INTEGER UNIQUE NOT NULL,
                    generation INTEGER PRIMARY KEY
                );
            DELETE FROM dunamai_ancestor;
            WITH RECURSIVE g(x, i)
                AS (
                    VALUES((SELECT value FROM vvar WHERE name = 'checkout' LIMIT 1), 1)
                    UNION ALL
                    SELECT plink.pid, g.i + 1 FROM plink, g
                    WHERE plink.cid = g.x AND plink.isprim
                )
                INSERT INTO dunamai_ancestor(rid, generation) SELECT x, i FROM g;
            SELECT tag.tagname, dunamai_ancestor.generation
                FROM tag
                JOIN tagxref ON tag.tagid = tagxref.tagid
                JOIN event ON tagxref.origid = event.objid
                JOIN dunamai_ancestor ON tagxref.origid = dunamai_ancestor.rid
                WHERE tagxref.tagtype = 1
                ORDER BY event.mtime DESC, tagxref.mtime DESC;
        """
        code, msg = _run_cmd('fossil sql "{}"'.format(" ".join(query.splitlines())), path)
        if not msg:
            try:
                distance = int(total_commits)
            except Exception:
                distance = 0
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )

        tags_to_distance = [
            (line.rsplit(",", 1)[0][5:-1], int(line.rsplit(",", 1)[1]) - 1) for line in msg.splitlines()
        ]

        matched_pattern = _match_version_pattern(
            pattern, [t for t, d in tags_to_distance], latest_tag, strict, pattern_prefix
        )
        if matched_pattern is None:
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )
        tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

        distance = dict(tags_to_distance)[tag]

        version = cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            branch=branch,
            timestamp=timestamp,
            vcs=vcs,
        )
        version._matched_tag = tag
        version._newer_unmatched_tags = unmatched
        return version

    @classmethod
    def from_pijul(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on Pijul tags.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = Vcs.Pijul
        _detect_vcs(vcs, path)

        code, msg = _run_cmd("pijul diff --short", path)
        dirty = msg.strip() != ""

        code, msg = _run_cmd("pijul channel", path)
        branch = "main"
        for line in msg.splitlines():
            if line.startswith("* "):
                branch = line.split("* ", 1)[1]
                break

        code, msg = _run_cmd("pijul log --limit 1 --output-format json", path)
        limited_commits = json.loads(msg)
        if len(limited_commits) == 0:
            return cls._fallback(strict, dirty=dirty, branch=branch, vcs=vcs)

        commit = limited_commits[0]["hash"][:commit_length]
        timestamp = _parse_timestamp(limited_commits[0]["timestamp"])

        code, msg = _run_cmd("pijul log --output-format json", path)
        channel_commits = json.loads(msg)

        code, msg = _run_cmd("pijul tag", path)
        if not msg:
            # The channel creation is in the list, so offset by 1.
            distance = len(channel_commits) - 1
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )

        tag_meta = []  # type: List[dict]
        tag_state = ""
        tag_timestamp = dt.datetime.now()
        tag_message = ""
        tag_after_header = False
        for line in msg.splitlines():
            if not tag_after_header:
                if line.startswith("State "):
                    tag_state = line.split("State ", 1)[1]
                elif line.startswith("Date:"):
                    tag_timestamp = _parse_timestamp(
                        line.split("Date: ", 1)[1].replace(" UTC", "Z"), format=_TIMESTAMP_GENERIC_SPACE
                    )
                elif line.startswith("    "):
                    tag_message += line[4:]
                    tag_after_header = True
            else:
                if line.startswith("State "):
                    tag_meta.append(
                        {
                            "state": tag_state,
                            "timestamp": tag_timestamp,
                            "message": tag_message.strip(),
                        }
                    )

                    tag_state = line.split("State ", 1)[1]
                    tag_timestamp = dt.datetime.now()
                    tag_message = ""
                    tag_after_header = False
                else:
                    tag_message += line
        if tag_after_header:
            tag_meta.append({"state": tag_state, "timestamp": tag_timestamp, "message": tag_message.strip()})

        tag_meta_by_msg = {}  # type: dict
        for meta in tag_meta:
            if (
                meta["message"] not in tag_meta_by_msg
                or meta["timestamp"] > tag_meta_by_msg[meta["message"]]["timestamp"]
            ):
                tag_meta_by_msg[meta["message"]] = meta

        tags = [t["message"] for t in sorted(tag_meta_by_msg.values(), key=lambda x: x["timestamp"], reverse=True)]

        matched_pattern = _match_version_pattern(pattern, tags, latest_tag, strict, pattern_prefix)
        if matched_pattern is None:
            return cls._fallback(
                strict,
                distance=distance,
                commit=commit,
                dirty=dirty,
                branch=branch,
                timestamp=timestamp,
                vcs=vcs,
            )
        tag, base, stage, unmatched, tagged_metadata, epoch = matched_pattern

        tag_id = tag_meta_by_msg[tag]["state"]
        _run_cmd("pijul tag checkout {}".format(tag_id), path, codes=[0, 1])
        code, msg = _run_cmd("pijul log --output-format json --channel {}".format(tag_id), path)
        if msg.strip() == "":
            tag_commits = []  # type: list
        else:
            tag_commits = json.loads(msg)

        distance = len(channel_commits) - len(tag_commits)

        version = cls(
            base,
            stage=stage,
            distance=distance,
            commit=commit,
            dirty=dirty,
            tagged_metadata=tagged_metadata,
            epoch=epoch,
            branch=branch,
            timestamp=timestamp,
            vcs=vcs,
        )
        version._matched_tag = tag
        version._newer_unmatched_tags = unmatched
        return version

    @classmethod
    def from_any_vcs(
        cls,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        tag_dir: str = "tags",
        tag_branch: Optional[str] = None,
        full_commit: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        ignore_untracked: bool = False,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on a detected version control system.

        :param pattern: Regular expression matched against the version source.
            This must contain one capture group named `base` corresponding to
            the release segment of the source. Optionally, it may contain another
            two groups named `stage` and `revision` corresponding to a prerelease
            type (such as 'alpha' or 'rc') and number (such as in 'alpha-2' or 'rc3').
            It may also contain a group named `tagged_metadata` corresponding to extra
            metadata after the main part of the version (typically after a plus sign).
            There may also be a group named `epoch` for the PEP 440 concept.

            If the `base` group is not included, then this will be interpreted
            as the name of a variant of the `Pattern` enum. For example, passing
            `"default"` is the same as passing `Pattern.Default`.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param tag_dir: Location of tags relative to the root.
            This is only used for Subversion.
        :param tag_branch: Branch on which to find tags, if different than the
            current branch. This is only used for Git currently.
        :param full_commit: Get the full commit hash instead of the short form.
            This is only used for Git and Mercurial.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param ignore_untracked:
            Ignore untracked files when determining whether the repository is dirty.
            This is only used for Git currently.
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        vcs = _detect_vcs_from_archival(path)
        if vcs is None:
            vcs = _detect_vcs(None, path)
        return cls._do_vcs_callback(
            vcs,
            pattern,
            latest_tag,
            tag_dir,
            tag_branch,
            full_commit,
            strict,
            path,
            pattern_prefix,
            ignore_untracked,
            commit_length,
        )

    @classmethod
    def from_vcs(
        cls,
        vcs: Vcs,
        pattern: Union[str, Pattern] = Pattern.Default,
        latest_tag: bool = False,
        tag_dir: str = "tags",
        tag_branch: Optional[str] = None,
        full_commit: bool = False,
        strict: bool = False,
        path: Optional[Path] = None,
        pattern_prefix: Optional[str] = None,
        ignore_untracked: bool = False,
        commit_length: Optional[int] = None,
    ) -> "Version":
        r"""
        Determine a version based on a specific VCS setting.

        This is primarily intended for other tools that want to generically
        use some VCS setting based on user configuration, without having to
        maintain a mapping from the VCS name to the appropriate function.

        :param pattern: Regular expression matched against the version source.
            Refer to `from_any_vcs` for more info.
        :param latest_tag: If true, only inspect the latest tag on the latest
            tagged commit for a pattern match. If false, keep looking at tags
            until there is a match.
        :param tag_dir: Location of tags relative to the root.
            This is only used for Subversion.
        :param tag_branch: Branch on which to find tags, if different than the
            current branch. This is only used for Git currently.
        :param full_commit: Get the full commit hash instead of the short form.
            This is only used for Git and Mercurial.
        :param strict: Elevate warnings to errors.
            When there are no tags, fail instead of falling back to 0.0.0.
        :param path: Directory to inspect, if not the current working directory.
        :param pattern_prefix: Insert this after the pattern's start anchor (`^`).
        :param ignore_untracked:
            Ignore untracked files when determining whether the repository is dirty.
            This is only used for Git currently.
        :param commit_length:
            Use this many characters from the start of the full commit hash.
        :returns: Detected version.
        """
        return cls._do_vcs_callback(
            vcs,
            pattern,
            latest_tag,
            tag_dir,
            tag_branch,
            full_commit,
            strict,
            path,
            pattern_prefix,
            ignore_untracked,
            commit_length,
        )

    @classmethod
    def _do_vcs_callback(
        cls,
        vcs: Vcs,
        pattern: Union[str, Pattern],
        latest_tag: bool,
        tag_dir: str,
        tag_branch: Optional[str],
        full_commit: bool,
        strict: bool,
        path: Optional[Path],
        pattern_prefix: Optional[str] = None,
        ignore_untracked: bool = False,
        commit_length: Optional[int] = None,
    ) -> "Version":
        mapping = {
            Vcs.Any: cls.from_any_vcs,
            Vcs.Git: cls.from_git,
            Vcs.Mercurial: cls.from_mercurial,
            Vcs.Darcs: cls.from_darcs,
            Vcs.Subversion: cls.from_subversion,
            Vcs.Bazaar: cls.from_bazaar,
            Vcs.Fossil: cls.from_fossil,
            Vcs.Pijul: cls.from_pijul,
        }  # type: Mapping[Vcs, Callable[..., "Version"]]
        kwargs = {}
        callback = mapping[vcs]
        for kwarg, value in [
            ("pattern", pattern),
            ("latest_tag", latest_tag),
            ("tag_dir", tag_dir),
            ("tag_branch", tag_branch),
            ("full_commit", full_commit),
            ("strict", strict),
            ("path", path),
            ("pattern_prefix", pattern_prefix),
            ("ignore_untracked", ignore_untracked),
            ("commit_length", commit_length),
        ]:
            if kwarg in inspect.getfullargspec(callback).args:
                kwargs[kwarg] = value
        return callback(**kwargs)


def check_version(version: str, style: Style = Style.Pep440) -> None:
    """
    Check if a version is valid for a style.

    :param version: Version to check.
    :param style: Style against which to check.
    :raises ValueError: If the version is invalid.
    """
    name, pattern = {
        Style.Pep440: ("PEP 440", _VALID_PEP440),
        Style.SemVer: ("Semantic Versioning", _VALID_SEMVER),
        Style.Pvp: ("PVP", _VALID_PVP),
    }[style]
    failure_message = "Version '{}' does not conform to the {} style".format(version, name)
    if not re.search(pattern, version):
        raise ValueError(failure_message)
    if style == Style.SemVer:
        parts = re.split(r"[.-]", version.split("+", 1)[0])
        if any(re.search(r"^0[0-9]+$", x) for x in parts):
            raise ValueError(failure_message)


def get_version(
    name: str,
    first_choice: Optional[Callable[[], Optional[Version]]] = None,
    third_choice: Optional[Callable[[], Optional[Version]]] = None,
    fallback: Version = Version("0.0.0"),
    ignore: Optional[Sequence[Version]] = None,
    parser: Callable[[str], Version] = Version,
) -> Version:
    """
    Check importlib-metadata info or a fallback function to determine the version.
    This is intended as a convenient default for setting your `__version__` if
    you do not want to include a generated version statically during packaging.

    :param name: Installed package name.
    :param first_choice: Callback to determine a version before checking
        to see if the named package is installed.
    :param third_choice: Callback to determine a version if the installed
        package cannot be found by name.
    :param fallback: If no other matches found, use this version.
    :param ignore: Ignore a found version if it is part of this list. When
        comparing the found version to an ignored one, fields with None in the ignored
        version are not taken into account. If the ignored version has distance=0,
        then that field is also ignored.
    :param parser: Callback to convert a string into a Version instance.
        This will be used for the second choice.
        For example, you can pass `Version.parse` here.
    :returns: First available version.
    """
    if ignore is None:
        ignore = []

    if first_choice:
        first_ver = first_choice()
        if first_ver and not any(first_ver._matches_partial(v) for v in ignore):
            return first_ver

    try:
        import importlib.metadata as ilm
    except ImportError:
        import importlib_metadata as ilm  # type: ignore
    try:
        ilm_version = parser(ilm.version(name))
        if not any(ilm_version._matches_partial(v) for v in ignore):
            return ilm_version
    except ilm.PackageNotFoundError:
        pass

    if third_choice:
        third_ver = third_choice()
        if third_ver and not any(third_ver._matches_partial(v) for v in ignore):
            return third_ver

    return fallback


def serialize_pep440(
    base: str,
    stage: Optional[str] = None,
    revision: Optional[int] = None,
    post: Optional[int] = None,
    dev: Optional[int] = None,
    epoch: Optional[int] = None,
    metadata: Optional[Sequence[Union[str, int]]] = None,
) -> str:
    """
    Serialize a version based on PEP 440.
    Use this instead of `Version.serialize()` if you want more control
    over how the version is mapped.

    :param base: Release segment, such as 0.1.0.
    :param stage: Pre-release stage ("a", "b", or "rc").
    :param revision: Pre-release revision (e.g., 1 as in "rc1").
        This is ignored when `stage` is None.
    :param post: Post-release number.
    :param dev: Developmental release number.
    :param epoch: Epoch number.
    :param metadata: Any local version label segments.
    :returns: Serialized version.
    """
    out = []  # type: list

    if epoch is not None:
        out.extend([epoch, "!"])

    out.append(base)

    if stage is not None:
        alternative_stages = {"alpha": "a", "beta": "b", "c": "rc", "pre": "rc", "preview": "rc"}
        out.append(alternative_stages.get(stage.lower(), stage.lower()))
        if revision is None:
            # PEP 440 does not allow omitting the revision, so assume 0.
            out.append(0)
        else:
            out.append(revision)

    if post is not None:
        out.extend([".post", post])

    if dev is not None:
        out.extend([".dev", dev])

    if metadata is not None and len(metadata) > 0:
        out.extend(["+", ".".join(map(str, metadata))])

    serialized = "".join(map(str, out))
    check_version(serialized, Style.Pep440)
    return serialized


def serialize_semver(
    base: str,
    pre: Optional[Sequence[Union[str, int]]] = None,
    metadata: Optional[Sequence[Union[str, int]]] = None,
) -> str:
    """
    Serialize a version based on Semantic Versioning.
    Use this instead of `Version.serialize()` if you want more control
    over how the version is mapped.

    :param base: Version core, such as 0.1.0.
    :param pre: Pre-release identifiers.
    :param metadata: Build metadata identifiers.
    :returns: Serialized version.
    """
    out = [base]

    if pre is not None and len(pre) > 0:
        out.extend(["-", ".".join(map(str, pre))])

    if metadata is not None and len(metadata) > 0:
        out.extend(["+", ".".join(map(str, metadata))])

    serialized = "".join(str(x) for x in out)
    check_version(serialized, Style.SemVer)
    return serialized


def serialize_pvp(base: str, metadata: Optional[Sequence[Union[str, int]]] = None) -> str:
    """
    Serialize a version based on the Haskell Package Versioning Policy.
    Use this instead of `Version.serialize()` if you want more control
    over how the version is mapped.

    :param base: Version core, such as 0.1.0.
    :param metadata: Version tag metadata.
    :returns: Serialized version.
    """
    out = [base]

    if metadata is not None and len(metadata) > 0:
        out.extend(["-", "-".join(map(str, metadata))])

    serialized = "".join(map(str, out))
    check_version(serialized, Style.Pvp)
    return serialized


def bump_version(base: str, index: int = -1, increment: int = 1) -> str:
    """
    Increment one of the numerical positions of a version.

    :param base: Version core, such as 0.1.0.
        Do not include pre-release identifiers.
    :param index: Numerical position to increment.
        This follows Python indexing rules, so positive numbers start from
        the left side and count up from 0, while negative numbers start from
        the right side and count down from -1.
    :param increment: By how much the `index` needs to increment.
    :returns: Bumped version.
    """
    bases = [int(x) for x in base.split(".")]
    bases[index] += increment

    limit = 0 if index < 0 else len(bases)
    i = index + 1
    while i < limit:
        bases[i] = 0
        i += 1

    return ".".join(str(x) for x in bases)


def _parse_git_timestamp_iso_strict(raw: str) -> dt.datetime:
    # Remove colon from timezone offset for pre-3.7 Python:
    compat = re.sub(r"(.*T.*[-+]\d+):(\d+)", r"\1\2", raw)
    return _parse_timestamp(compat, _TIMESTAMP_GIT_ISO_STRICT)


def _parse_git_timestamp_iso(raw: str) -> dt.datetime:
    # Remove colon from timezone offset for pre-3.7 Python:
    compat = re.sub(r"(.* .* [-+]\d+):(\d+)", r"\1\2", raw)
    return _parse_timestamp(compat, _TIMESTAMP_GIT_ISO)


def _parse_timestamp(raw: str, format: str = _TIMESTAMP_GENERIC) -> dt.datetime:
    # Normalize "Z" for pre-3.7 compatibility:
    normalized = re.sub(r"Z$", "+0000", raw)
    # Truncate %f to six digits:
    normalized = re.sub(r"\.(\d{6})\d+\+0000", r".\g<1>+0000", normalized)

    return dt.datetime.strptime(normalized, format)


__version__ = get_version("dunamai").serialize()
