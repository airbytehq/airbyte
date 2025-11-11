import argparse
import sys
from pathlib import Path
from typing import Mapping, Optional

from dunamai import check_version, Version, Pattern, Style, Vcs, VERSION_SOURCE_PATTERN


common_sub_args = [
    {
        "triggers": ["--metadata"],
        "action": "store_true",
        "dest": "metadata",
        "default": None,
        "help": "Always include metadata. Ignored when --format is used",
    },
    {
        "triggers": ["--no-metadata"],
        "action": "store_false",
        "dest": "metadata",
        "default": None,
        "help": "Never include metadata. Ignored when --format is used",
    },
    {
        "triggers": ["--dirty"],
        "action": "store_true",
        "dest": "dirty",
        "help": "Include dirty flag if applicable. Ignored when --format is used",
    },
    {
        "vcs": [Vcs.Git],
        "triggers": ["--ignore-untracked"],
        "action": "store_true",
        "dest": "ignore_untracked",
        "help": "Ignore untracked files when determining whether the repository is dirty",
    },
    {
        "triggers": ["--tagged-metadata"],
        "action": "store_true",
        "dest": "tagged_metadata",
        "help": "Include tagged metadata if applicable. Ignored when --format is used",
    },
    {
        "triggers": ["--pattern"],
        "default": VERSION_SOURCE_PATTERN,
        "help": (
            "Regular expression matched against the version source."
            " This must contain one capture group named `base` corresponding to"
            " the release segment of the source."
            " Optionally, it may contain another two groups named `stage` and `revision`"
            " corresponding to a prerelease type (such as 'alpha' or 'rc') and number"
            " (such as in 'alpha-2' or 'rc3')."
            " It may also contain a group named `tagged_metadata` corresponding to extra"
            " metadata after the main part of the version (typically after a plus sign)."
            " There may also be a group named `epoch` for the PEP 440 concept."
            " If the `base` group is not present, then instead this will be interpreted"
            " as a named preset, which may be one of the following: {}"
        ).format(", ".join(["`{}`".format(x.value) for x in Pattern])),
    },
    {
        "triggers": ["--pattern-prefix"],
        "help": "Insert this after the pattern's start anchor (`^`).",
    },
    {
        "triggers": ["--format"],
        "help": (
            "Custom output format. Available substitutions:"
            " {base}, {stage}, {revision}, {distance}, {commit}, {dirty},"
            " {tagged_metadata}, {epoch}, {branch}, {branch_escaped}, {timestamp},"
            " {major}, {minor}, {patch}"
        ),
    },
    {
        "triggers": ["--style"],
        "choices": [x.value for x in Style],
        "help": (
            "Preconfigured output format."
            " Will default to PEP 440 if not set and no custom format given."
            " If you specify both a style and a custom format, then the format"
            " will be validated against the style's rules"
        ),
    },
    {
        "triggers": ["--latest-tag"],
        "action": "store_true",
        "dest": "latest_tag",
        "default": False,
        "help": "Only inspect the latest tag on the latest tagged commit for a pattern match",
    },
    {
        "triggers": ["--strict"],
        "action": "store_true",
        "dest": "strict",
        "default": False,
        "help": ("Elevate warnings to errors. When there are no tags, fail instead of falling back to 0.0.0"),
    },
    {
        "triggers": ["--path"],
        "help": "Directory to inspect, if not the current working directory",
    },
    {
        "triggers": ["--debug"],
        "action": "store_true",
        "dest": "debug",
        "default": False,
        "help": "Display additional information on stderr for troubleshooting",
    },
    {
        "triggers": ["--bump"],
        "action": "store_true",
        "dest": "bump",
        "default": False,
        "help": (
            "Increment the last part of the version `base` by 1,"
            " unless the `stage` is set, in which case increment the `revision`"
            " by 1 or set it to a default of 2 if there was no `revision`"
            " Does nothing when on a commit with a version tag."
        ),
    },
    {
        "vcs": [Vcs.Git, Vcs.Mercurial],
        "triggers": ["--full-commit"],
        "action": "store_true",
        "dest": "full_commit",
        "default": False,
        "help": "Get the full commit hash instead of the short form",
    },
    {
        "triggers": ["--commit-length"],
        "dest": "commit_length",
        "type": int,
        "help": "Use this many characters from the start of the full commit hash",
    },
    {
        "triggers": ["--commit-prefix"],
        "dest": "commit_prefix",
        "type": str,
        "help": "Add this prefix when serializing commit IDs",
    },
    {
        "triggers": ["--escape-with"],
        "dest": "escape_with",
        "type": str,
        "help": "When escaping, replace with this substitution. The default is simply to remove invalid characters.",
    },
    {
        "vcs": [Vcs.Git],
        "triggers": ["--tag-branch"],
        "help": "Branch on which to find tags, if different than the current branch",
    },
    {
        "vcs": [Vcs.Subversion],
        "triggers": ["--tag-dir"],
        "default": "tags",
        "help": "Location of tags relative to the root",
    },
]
cli_spec = {
    "description": "Generate dynamic versions",
    "sub_dest": "command",
    "sub": {
        "from": {
            "description": "Generate version from a particular VCS",
            "sub_dest": "vcs",
            "sub": {
                Vcs.Any.value: {
                    "description": "Generate version from any detected VCS",
                    "args": common_sub_args,
                },
                Vcs.Git.value: {
                    "description": "Generate version from Git",
                    "args": common_sub_args,
                },
                Vcs.Mercurial.value: {
                    "description": "Generate version from Mercurial",
                    "args": common_sub_args,
                },
                Vcs.Darcs.value: {
                    "description": "Generate version from Darcs",
                    "args": common_sub_args,
                },
                Vcs.Subversion.value: {
                    "description": "Generate version from Subversion",
                    "args": common_sub_args,
                },
                Vcs.Bazaar.value: {
                    "description": "Generate version from Bazaar",
                    "args": common_sub_args,
                },
                Vcs.Fossil.value: {
                    "description": "Generate version from Fossil",
                    "args": common_sub_args,
                },
                Vcs.Pijul.value: {
                    "description": "Generate version from Pijul",
                    "args": common_sub_args,
                },
            },
        },
        "check": {
            "description": "Check if a version is valid for a style",
            "args": [
                {
                    "triggers": [],
                    "dest": "version",
                    "help": "Version to check; may be piped in",
                    "nargs": "?",
                },
                {
                    "triggers": ["--style"],
                    "choices": [x.value for x in Style],
                    "default": Style.Pep440.value,
                    "help": "Style against which to check",
                },
            ],
        },
    },
}


def build_parser(
    spec: Mapping, parser: Optional[argparse.ArgumentParser] = None, vcs: Optional[Vcs] = None
) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser(
            description=spec["description"], formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    if "args" in spec:
        for arg in spec["args"]:
            help = arg["help"]
            if "vcs" in arg:
                if vcs not in [*arg["vcs"], Vcs.Any]:
                    continue
                help += " (only: {})".format(", ".join([x.name for x in arg["vcs"]]))
            triggers = arg["triggers"]
            parser.add_argument(
                *triggers,
                help=help,
                **{k: v for k, v in arg.items() if k not in ["triggers", "help", "vcs"]},
            )
    if "sub" in spec:
        subparsers = parser.add_subparsers(dest=spec["sub_dest"])
        subparsers.required = True
        for name, sub_spec in spec["sub"].items():
            subparser = subparsers.add_parser(
                name,
                description=sub_spec.get("description"),
                help=sub_spec.get("description"),
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            build_parser(sub_spec, subparser, Vcs(name) if spec["sub_dest"] == "vcs" else None)

    return parser


def get_parser() -> argparse.ArgumentParser:
    return build_parser(cli_spec)


def parse_args(argv=None) -> argparse.Namespace:
    return get_parser().parse_args(argv)


def from_stdin(value: Optional[str]) -> Optional[str]:
    if value is not None:
        return value

    if not sys.stdin.isatty():
        return sys.stdin.readline().strip()

    return None


def from_vcs(
    vcs: Vcs,
    pattern: str,
    metadata: Optional[bool],
    dirty: bool,
    format: Optional[str],
    style: Optional[Style],
    latest_tag: bool,
    tag_dir: str,
    debug: bool,
    bump: bool,
    tagged_metadata: bool,
    tag_branch: Optional[str],
    full_commit: bool,
    strict: bool,
    path: Optional[Path],
    pattern_prefix: Optional[str],
    ignore_untracked: bool,
    commit_length: Optional[int],
    commit_prefix: Optional[str],
    escape_with: Optional[str],
) -> None:
    version = Version.from_vcs(
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

    for concern in version.concerns:
        print("Warning: {}".format(concern.message()), file=sys.stderr)

    print(version.serialize(metadata, dirty, format, style, bump, tagged_metadata, commit_prefix, escape_with))

    if debug:
        print("# Matched tag: {}".format(version._matched_tag), file=sys.stderr)
        print("# Newer unmatched tags: {}".format(version._newer_unmatched_tags), file=sys.stderr)


def main() -> None:
    args = parse_args()
    try:
        if args.command == "from":
            tag_dir = getattr(args, "tag_dir", "tags")
            tag_branch = getattr(args, "tag_branch", None)
            full_commit = getattr(args, "full_commit", False)
            ignore_untracked = getattr(args, "ignore_untracked", False)
            commit_length = getattr(args, "commit_length", None)
            commit_prefix = getattr(args, "commit_prefix", None)
            escape_with = getattr(args, "escape_with", None)
            from_vcs(
                Vcs(args.vcs),
                args.pattern,
                args.metadata,
                args.dirty,
                args.format,
                Style(args.style) if args.style else None,
                args.latest_tag,
                tag_dir,
                args.debug,
                args.bump,
                args.tagged_metadata,
                tag_branch,
                full_commit,
                args.strict,
                Path(args.path) if args.path is not None else None,
                args.pattern_prefix,
                ignore_untracked,
                commit_length,
                commit_prefix,
                escape_with,
            )
        elif args.command == "check":
            version = from_stdin(args.version)
            if version is None:
                raise ValueError("A version must be specified")
            check_version(version, Style(args.style))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
