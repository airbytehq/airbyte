def get_fish_completion_script() -> str:
    """
    A special task accessible via `poe _fish_completion` that prints a basic fish
    completion script for the presently available poe tasks
    """

    # TODO: work out how to:
    # - support completion of global options (with help) only if no task provided
    #   without having to call poe for every option which would be too slow
    # - include task help in (dynamic) task completions
    # - maybe just use python for the whole of the __list_poe_tasks logic?

    return "\n".join(
        (
            "function __list_poe_tasks",
            "    set prev_args (commandline -pco)",
            '    set tasks (poe _list_tasks | string split " ")',
            "    set arg (commandline -ct)",
            "    for task in $tasks",
            '        if test "$task" != poe && contains $task $prev_args',
            # TODO: offer $task specific options
            '            complete -C "ls $arg"',
            "            return 0",
            "        end",
            "    end",
            "    for task in $tasks",
            "        echo $task",
            "    end",
            "end",
            "complete -c poe --no-files -a '(__list_poe_tasks)'",
        )
    )
