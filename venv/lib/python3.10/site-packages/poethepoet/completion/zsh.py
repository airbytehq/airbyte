from typing import Any, Iterable, Set


def get_zsh_completion_script() -> str:
    """
    A special task accessible via `poe _zsh_completion` that prints a zsh completion
    script for poe generated from the argparses config
    """
    from pathlib import Path

    from ..app import PoeThePoet

    # build and interogate the argument parser as the normal cli would
    app = PoeThePoet(cwd=Path().resolve())
    parser = app.ui.build_parser()
    global_options = parser._action_groups[1]._group_actions
    excl_groups = [
        set(excl_group._group_actions)
        for excl_group in parser._mutually_exclusive_groups
    ]

    def format_exclusions(excl_option_strings):
        return f"($ALL_EXLC {' '.join(sorted(excl_option_strings))})"

    # format the zsh completion script
    args_lines = ["    _arguments -C"]
    for option in global_options:
        # help and version are special cases that dont go with other args
        if option.dest in ["help", "version"]:
            options_part = (
                option.option_strings[0]
                if len(option.option_strings) == 1
                else '"{' + ",".join(sorted(option.option_strings)) + '}"'
            )
            args_lines.append(f'"(- *){options_part}[{option.help}]"')
            continue

        # collect other options that are exclusive to this one
        excl_options: Iterable[Any] = next(
            (
                excl_group - {option}
                for excl_group in excl_groups
                if option in excl_group
            ),
            tuple(),
        )
        # collect all option strings that are exclusive with this one
        excl_option_strings: Set[str] = {
            option_string
            for excl_option in excl_options
            for option_string in excl_option.option_strings
        } | set(option.option_strings)

        if len(excl_option_strings) == 1:
            options_part = option.option_strings[0]
        elif len(option.option_strings) == 1:
            options_part = (
                format_exclusions(excl_option_strings) + option.option_strings[0]
            )
        else:
            options_part = (
                format_exclusions(excl_option_strings)
                + '"{'
                + ",".join(sorted(option.option_strings))
                + '}"'
            )

        args_lines.append(f'"{options_part}[{option.help}]"')

    args_lines.append('"1: :($TASKS)"')
    args_lines.append('"*::arg:->args"')

    return "\n".join(
        [
            "#compdef _poe poe\n",
            "function _poe {",
            '    local ALL_EXLC=("-h" "--help" "--version")',
            "    local TASKS=($(poe _list_tasks))",
            "",
            " \\\n        ".join(args_lines),
            "",
            # Only offer filesystem based autocompletions after a task is specified
            "    if (($TASKS[(Ie)$line[1]])); then",
            "        _files",
            "    fi",
            "}",
        ]
    )
