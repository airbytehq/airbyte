import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Tuple, Union

if TYPE_CHECKING:
    from .config import PoeConfig
    from .env.manager import EnvVarsManager
    from .executor import PoeExecutor
    from .ui import PoeUi


class RunContext:
    config: "PoeConfig"
    ui: "PoeUi"
    env: "EnvVarsManager"
    dry: bool
    poe_active: Optional[str]
    project_dir: Path
    multistage: bool = False
    exec_cache: Dict[str, Any]
    captured_stdout: Dict[Tuple[str, ...], str]

    def __init__(
        self,
        config: "PoeConfig",
        ui: "PoeUi",
        env: Mapping[str, str],
        dry: bool,
        poe_active: Optional[str],
        multistage: bool = False,
        cwd: Optional[Union[Path, str]] = None,
    ):
        from .env.manager import EnvVarsManager

        self.config = config
        self.ui = ui
        self.project_dir = Path(config.project_dir)
        self.dry = dry
        self.poe_active = poe_active
        self.multistage = multistage
        self.exec_cache = {}
        self.captured_stdout = {}
        self.env = EnvVarsManager(self.config, self.ui, base_env=env, cwd=cwd)

    @property
    def executor_type(self) -> Optional[str]:
        return self.config.executor["type"]

    def get_task_env(
        self,
        parent_env: Optional["EnvVarsManager"],
        task_envfile: Optional[str],
        task_env: Optional[Mapping[str, str]],
        task_uses: Optional[Mapping[str, Tuple[str, ...]]] = None,
    ) -> "EnvVarsManager":
        if parent_env is None:
            parent_env = self.env

        result = parent_env.for_task(task_envfile, task_env)

        # Include env vars from dependencies
        if task_uses is not None:
            result.update(self._get_dep_values(task_uses))

        return result

    def _get_dep_values(
        self, used_task_invocations: Mapping[str, Tuple[str, ...]]
    ) -> Dict[str, str]:
        """
        Get env vars from upstream tasks declared via the uses option.
        """
        return {
            var_name: self.get_task_output(invocation)
            for var_name, invocation in used_task_invocations.items()
        }

    def save_task_output(self, invocation: Tuple[str, ...], captured_stdout: bytes):
        """
        Store the stdout data from a task so that it can be reused by other tasks
        """
        try:
            self.captured_stdout[invocation] = captured_stdout.decode()
        except UnicodeDecodeError:
            # Attempt to recover in case a specific encoding is configured
            io_encoding = self.env.get("PYTHONIOENCODING")
            if io_encoding:
                self.captured_stdout[invocation] = captured_stdout.decode(io_encoding)
            else:
                raise

    def get_task_output(self, invocation: Tuple[str, ...]):
        """
        Get the stored stdout data from a task so that it can be reused by other tasks

        New lines are replaced with whitespace similar to how unquoted command
        interpolation works in bash.
        """
        return re.sub(r"\s+", " ", self.captured_stdout[invocation].strip("\r\n"))

    def get_executor(
        self,
        invocation: Tuple[str, ...],
        env: "EnvVarsManager",
        working_dir: Path,
        executor_config: Optional[Mapping[str, str]] = None,
        capture_stdout: bool = False,
    ) -> "PoeExecutor":
        from .executor import PoeExecutor

        return PoeExecutor.get(
            invocation=invocation,
            context=self,
            env=env,
            working_dir=working_dir,
            dry=self.dry,
            executor_config=executor_config,
            capture_stdout=capture_stdout,
        )
