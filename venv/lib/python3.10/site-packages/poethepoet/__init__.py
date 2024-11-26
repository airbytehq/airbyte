from .__version__ import __version__

__all__ = ["__version__", "main"]


def main():
    import sys

    if len(sys.argv) == 2 and sys.argv[1].startswith("_"):
        first_arg = sys.argv[1]
        if first_arg in ("_list_tasks", "_describe_tasks"):
            _list_tasks()
            return
        if first_arg == "_zsh_completion":
            from .completion.zsh import get_zsh_completion_script

            print(get_zsh_completion_script())
            return
        if first_arg == "_bash_completion":
            from .completion.bash import get_bash_completion_script

            print(get_bash_completion_script())
            return
        if first_arg == "_fish_completion":
            from .completion.fish import get_fish_completion_script

            print(get_fish_completion_script())
            return

    from pathlib import Path

    from .app import PoeThePoet

    app = PoeThePoet(cwd=Path().resolve(), output=sys.stdout)
    result = app(cli_args=sys.argv[1:])
    if result:
        raise SystemExit(result)


def _list_tasks():
    """
    A special task accessible via `poe _list_tasks` for use in shell completion

    Note this code path should include minimal imports to avoid slowing down the shell
    """

    try:
        from .config import PoeConfig

        config = PoeConfig()
        config.load()
        task_names = (task for task in config.tasks.keys() if task and task[0] != "_")
        print(" ".join(task_names))
    except Exception:  # pylint: disable=broad-except
        # this happens if there's no pyproject.toml present
        pass
