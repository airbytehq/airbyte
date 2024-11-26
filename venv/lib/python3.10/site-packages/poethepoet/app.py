import os
import sys
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from .exceptions import ExecutionError, PoeException

if TYPE_CHECKING:
    from .config import PoeConfig
    from .context import RunContext
    from .task import PoeTask
    from .ui import PoeUi


class PoeThePoet:
    """
    :param cwd:
        The directory that poe should take as the current working directory,
        this determines where to look for a pyproject.toml file, defaults to
        ``Path(".").resolve()``
    :type cwd: Path, optional
    :param config:
        Either a dictionary with the same schema as a pyproject.toml file, or a
        `PoeConfig <https://github.com/nat-n/poethepoet/blob/main/poethepoet/config.py>`_
        object to use as an alternative to loading config from a file.
    :type config: dict | PoeConfig, optional
    :param output:
        A stream for the application to write its own output to, defaults to sys.stdout
    :type output: IO, optional
    :param poetry_env_path:
        The path to the poetry virtualenv. If provided then it is used by the
        `PoetryExecutor <https://github.com/nat-n/poethepoet/blob/main/poethepoet/executor/poetry.py>`_,
        instead of having to execute poetry in a subprocess to determine this.
    :type poetry_env_path: str, optional
    :param config_name:
        The name of the file to load tasks and configuration from, defaults to
        "pyproject.toml"
    :type config_name: str, optional
    :param program_name:
        The name of the program that is being run. This is used primarily when
        outputting help messages, defaults to "poe"
    :type program_name: str, optional
    """

    cwd: Path
    ui: "PoeUi"
    config: "PoeConfig"

    def __init__(
        self,
        cwd: Optional[Union[Path, str]] = None,
        config: Optional[Union[Mapping[str, Any], "PoeConfig"]] = None,
        output: IO = sys.stdout,
        poetry_env_path: Optional[str] = None,
        config_name: str = "pyproject.toml",
        program_name: str = "poe",
    ):
        from .config import PoeConfig
        from .ui import PoeUi

        self.cwd = Path(cwd) if cwd else Path().resolve()

        if self.cwd and self.cwd.is_file():
            config_name = self.cwd.name
            self.cwd = self.cwd.parent

        self.config = (
            config
            if isinstance(config, PoeConfig)
            else PoeConfig(cwd=self.cwd, table=config, config_name=config_name)
        )
        self.ui = PoeUi(output=output, program_name=program_name)
        self._poetry_env_path = poetry_env_path

    def __call__(self, cli_args: Sequence[str], internal: bool = False) -> int:
        """
        :param cli_args:
            A sequence of command line arguments to pass to poe (i.e. sys.argv[1:])
        :param internal:
            Indicates that this is an internal call to run poe, e.g. from a
            plugin hook.
        """

        self.ui.parse_args(cli_args)

        if self.ui["version"]:
            self.ui.print_version()
            return 0

        try:
            self.config.load(self.ui["project_root"])
            self.config.validate()
        except PoeException as error:
            if self.ui["help"]:
                self.print_help()
                return 0
            self.print_help(error=error)
            return 1

        self.ui.set_default_verbosity(self.config.verbosity)

        if self.ui["help"]:
            self.print_help()
            return 0

        task = self.resolve_task(internal)
        if not task:
            return 1

        if task.has_deps():
            return self.run_task_graph(task) or 0
        else:
            return self.run_task(task) or 0

    def resolve_task(self, allow_hidden: bool = False) -> Optional["PoeTask"]:
        from .task import PoeTask

        task = tuple(self.ui["task"])
        if not task:
            self.print_help(info="No task specified.")
            return None

        task_name = task[0]
        if task_name not in self.config.tasks:
            self.print_help(error=PoeException(f"Unrecognised task {task_name!r}"))
            return None

        if task_name.startswith("_") and not allow_hidden:
            self.print_help(
                error=PoeException(
                    "Tasks prefixed with `_` cannot be executed directly"
                ),
            )
            return None

        return PoeTask.from_config(
            task_name, config=self.config, ui=self.ui, invocation=task
        )

    def run_task(
        self, task: "PoeTask", context: Optional["RunContext"] = None
    ) -> Optional[int]:
        if context is None:
            context = self.get_run_context()
        try:
            return task.run(context=context, extra_args=task.invocation[1:])
        except PoeException as error:
            self.print_help(error=error)
            return 1
        except ExecutionError as error:
            self.ui.print_error(error=error)
            return 1

    def run_task_graph(self, task: "PoeTask") -> Optional[int]:
        from .task.graph import TaskExecutionGraph

        context = self.get_run_context(multistage=True)
        graph = TaskExecutionGraph(task, context)
        plan = graph.get_execution_plan()

        for stage in plan:
            for stage_task in stage:
                if stage_task == task:
                    # The final sink task gets special treatment
                    return self.run_task(stage_task, context)

                try:
                    task_result = stage_task.run(
                        context=context, extra_args=stage_task.invocation[1:]
                    )
                    if task_result:
                        raise ExecutionError(
                            f"Task graph aborted after failed task {stage_task.name!r}"
                        )
                except PoeException as error:
                    self.print_help(error=error)
                    return 1
                except ExecutionError as error:
                    self.ui.print_error(error=error)
                    return 1
        return 0

    def get_run_context(self, multistage: bool = False) -> "RunContext":
        from .context import RunContext

        result = RunContext(
            config=self.config,
            ui=self.ui,
            env=os.environ,
            dry=self.ui["dry_run"],
            poe_active=os.environ.get("POE_ACTIVE"),
            multistage=multistage,
            cwd=self.cwd,
        )
        if self._poetry_env_path:
            # This allows the PoetryExecutor to use the venv from poetry directly
            result.exec_cache["poetry_virtualenv"] = self._poetry_env_path
        return result

    def print_help(
        self,
        info: Optional[str] = None,
        error: Optional[Union[str, PoeException]] = None,
    ):
        from .task.args import PoeTaskArgs

        if isinstance(error, str):
            error = PoeException(error)

        tasks_help: Dict[
            str, Tuple[str, Sequence[Tuple[Tuple[str, ...], str, str]]]
        ] = {
            task_name: (
                (
                    content.get("help", ""),
                    PoeTaskArgs.get_help_content(content.get("args")),
                )
                if isinstance(content, dict)
                else ("", tuple())
            )
            for task_name, content in self.config.tasks.items()
        }

        self.ui.print_help(tasks=tasks_help, info=info, error=error)
