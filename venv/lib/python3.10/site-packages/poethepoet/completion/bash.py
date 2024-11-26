def get_bash_completion_script() -> str:
    """
    A special task accessible via `poe _bash_completion` that prints a basic bash
    completion script for the presently available poe tasks
    """

    # TODO: see if it's possible to support completion of global options anywhere as
    #       nicely as for zsh

    return "\n".join(
        (
            "_poe_complete() {",
            "    local cur",
            '    cur="${COMP_WORDS[COMP_CWORD]}"',
            '    COMPREPLY=( $(compgen -W "$(poe _list_tasks)" -- ${cur}) )',
            "    return 0",
            "}",
            "complete -o default -F _poe_complete poe",
        )
    )
