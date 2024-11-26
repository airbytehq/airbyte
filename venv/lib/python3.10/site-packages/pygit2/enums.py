from enum import IntEnum, IntFlag

from . import _pygit2


class SubmoduleIgnore(IntEnum):
    UNSPECIFIED = _pygit2.GIT_SUBMODULE_IGNORE_UNSPECIFIED
    "use the submodule's configuration"

    NONE = _pygit2.GIT_SUBMODULE_IGNORE_NONE
    "any change or untracked == dirty"

    UNTRACKED = _pygit2.GIT_SUBMODULE_IGNORE_UNTRACKED
    "dirty if tracked files change"

    DIRTY = _pygit2.GIT_SUBMODULE_IGNORE_DIRTY
    "only dirty if HEAD moved"

    ALL = _pygit2.GIT_SUBMODULE_IGNORE_ALL
    "never dirty"


class SubmoduleStatus(IntFlag):
    IN_HEAD = _pygit2.GIT_SUBMODULE_STATUS_IN_HEAD
    "superproject head contains submodule"

    IN_INDEX = _pygit2.GIT_SUBMODULE_STATUS_IN_INDEX
    "superproject index contains submodule"

    IN_CONFIG = _pygit2.GIT_SUBMODULE_STATUS_IN_CONFIG
    "superproject gitmodules has submodule"

    IN_WD = _pygit2.GIT_SUBMODULE_STATUS_IN_WD
    "superproject workdir has submodule"

    INDEX_ADDED = _pygit2.GIT_SUBMODULE_STATUS_INDEX_ADDED
    "in index, not in head (flag available if ignore is not ALL)"

    INDEX_DELETED = _pygit2.GIT_SUBMODULE_STATUS_INDEX_DELETED
    "in head, not in index (flag available if ignore is not ALL)"

    INDEX_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_INDEX_MODIFIED
    "index and head don't match (flag available if ignore is not ALL)"

    WD_UNINITIALIZED = _pygit2.GIT_SUBMODULE_STATUS_WD_UNINITIALIZED
    "workdir contains empty repository (flag available if ignore is not ALL)"

    WD_ADDED = _pygit2.GIT_SUBMODULE_STATUS_WD_ADDED
    "in workdir, not index (flag available if ignore is not ALL)"

    WD_DELETED = _pygit2.GIT_SUBMODULE_STATUS_WD_DELETED
    "in index, not workdir (flag available if ignore is not ALL)"

    WD_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_WD_MODIFIED
    "index and workdir head don't match (flag available if ignore is not ALL)"

    WD_INDEX_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_WD_INDEX_MODIFIED
    "submodule workdir index is dirty (flag available if ignore is NONE or UNTRACKED)"

    WD_WD_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_WD_WD_MODIFIED
    "submodule workdir has modified files (flag available if ignore is NONE or UNTRACKED)"

    WD_UNTRACKED = _pygit2.GIT_SUBMODULE_STATUS_WD_UNTRACKED
    "submodule workdir contains untracked files (flag available if ignore is NONE)"
