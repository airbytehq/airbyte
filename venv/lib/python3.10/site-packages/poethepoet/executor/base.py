import os
import shutil
import sys
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from ..exceptions import ExecutionError, PoeException

if TYPE_CHECKING:
    from ..context import RunContext
    from ..env.manager import EnvVarsManager


# TODO: maybe invert the control so the executor is given a task to run?


class MetaPoeExecutor(type):
    """
    This metaclass makes all decendents of PoeExecutor (task types) register themselves
    on declaration and validates that they include the expected class attributes.
    """

    def __init__(cls, *args):
        super().__init__(*args)
        if cls.__name__ == "PoeExecutor":
            return
        assert isinstance(getattr(cls, "__key__", None), str)
        assert isinstance(getattr(cls, "__options__", None), dict)
        PoeExecutor._PoeExecutor__executor_types[cls.__key__] = cls


class PoeExecutor(metaclass=MetaPoeExecutor):
    """
    A base class for poe task executors
    """

    working_dir: Optional[Path]

    __executor_types: Dict[str, Type["PoeExecutor"]] = {}
    __key__: Optional[str] = None

    def __init__(
        self,
        invocation: Tuple[str, ...],
        context: "RunContext",
        options: Mapping[str, str],
        env: "EnvVarsManager",
        working_dir: Optional[Path] = None,
        dry: bool = False,
        capture_stdout: Union[str, bool] = False,
    ):
        self.invocation = invocation
        self.context = context
        self.options = options
        self.working_dir = working_dir
        self.env = env
        self.dry = dry
        self.capture_stdout = (
            Path(self.context.config.project_dir).joinpath(
                self.env.fill_template(capture_stdout)
            )
            if isinstance(capture_stdout, str)
            else capture_stdout
        )
        self._is_windows = sys.platform == "win32"

    @classmethod
    def works_with_context(cls, context: "RunContext") -> bool:
        return True

    @classmethod
    def get(
        cls,
        invocation: Tuple[str, ...],
        context: "RunContext",
        env: "EnvVarsManager",
        working_dir: Optional[Path] = None,
        dry: bool = False,
        executor_config: Optional[Mapping[str, str]] = None,
        capture_stdout: Union[str, bool] = False,
    ) -> "PoeExecutor":
        """"""
        # use task specific executor config or fallback to global
        options = executor_config or context.config.executor
        return cls._resolve_implementation(context, executor_config)(
            invocation, context, options, env, working_dir, dry, capture_stdout
        )

    @classmethod
    def _resolve_implementation(
        cls, context: "RunContext", executor_config: Optional[Mapping[str, str]]
    ):
        """
        Resolve to an executor class, either as specified in the available config or
        by making some reasonable assumptions based on visible features of the
        environment
        """

        config_executor_type = context.executor_type
        if executor_config:
            if executor_config["type"] not in cls.__executor_types:
                raise PoeException(
                    f"Cannot instantiate unknown executor {executor_config['type']!r}"
                )
            return cls.__executor_types[executor_config["type"]]
        elif config_executor_type == "auto":
            for impl in [
                cls.__executor_types["poetry"],
                cls.__executor_types["virtualenv"],
            ]:
                if impl.works_with_context(context):
                    return impl

            # Fallback to not using any particular environment
            return cls.__executor_types["simple"]
        else:
            if config_executor_type not in cls.__executor_types:
                raise PoeException(
                    "Cannot instantiate unknown executor" + repr(config_executor_type)
                )
            return cls.__executor_types[config_executor_type]

    def execute(
        self, cmd: Sequence[str], input: Optional[bytes] = None, use_exec: bool = False
    ) -> int:
        """
        Execute the given cmd.
        """

        # Attempt to explicitly resolve the target executable, because we can't count
        # on the OS to do this consistently.
        resolved_executable = shutil.which(cmd[0])
        if resolved_executable:
            cmd = (resolved_executable, *cmd[1:])

        return self._execute_cmd(cmd, input=input, use_exec=use_exec)

    def _execute_cmd(
        self,
        cmd: Sequence[str],
        *,
        input: Optional[bytes] = None,
        env: Optional[Mapping[str, str]] = None,
        shell: bool = False,
        use_exec: bool = False,
    ) -> int:
        """
        Execute the given cmd either as a subprocess or use exec to replace the current
        process. Using exec supports fewer options, and doesn't work on windows.
        """

        try:
            if self.working_dir and not self.working_dir.is_dir():
                raise PoeException(
                    f"Working directory {self.working_dir} could not be found."
                )
            if use_exec:
                if input:
                    raise ExecutionError("Cannot exec task that requires input!")
                if shell:
                    raise ExecutionError("Cannot exec task that requires shell!")
                if not self._is_windows:
                    # execvpe doesn't work properly on windows so we just don't go there
                    return self._exec(cmd, env=env)

            return self._exec_via_subproc(cmd, input=input, env=env, shell=shell)
        except FileNotFoundError as error:
            if error.filename == cmd[0]:
                return self._handle_file_not_found(cmd, error)
            if error.filename == self.working_dir:
                raise PoeException(
                    "The specified working directory does not exists "
                    f"'{self.working_dir}'"
                )
            raise

    def _handle_file_not_found(
        self, cmd: Sequence[str], error: FileNotFoundError
    ) -> int:
        raise PoeException(f"executable {cmd[0]!r} could not be found") from error

    def _exec(
        self,
        cmd: Sequence[str],
        *,
        env: Optional[Mapping[str, str]] = None,
    ):
        if self.dry:
            return 0

        # Beware: this is the point of no return!

        exec_env = dict(
            (self.env.to_dict() if env is None else env), POE_ACTIVE=self.__key__
        )
        if self.working_dir:
            os.chdir(self.working_dir)
        sys.stdout.flush()

        # if running tests then wrap up coverage instrumentation while we still can
        _stop_coverage()

        os.execvpe(cmd[0], tuple(cmd), exec_env)

    def _exec_via_subproc(
        self,
        cmd: Sequence[str],
        *,
        input: Optional[bytes] = None,
        env: Optional[Mapping[str, str]] = None,
        shell: bool = False,
    ) -> int:
        import signal
        from subprocess import PIPE, Popen

        if self.dry:
            return 0
        popen_kwargs: MutableMapping[str, Any] = {"shell": shell}
        popen_kwargs["env"] = dict(
            (self.env.to_dict() if env is None else env), POE_ACTIVE=self.__key__
        )
        if input is not None:
            popen_kwargs["stdin"] = PIPE
        if self.capture_stdout:
            if isinstance(self.capture_stdout, Path):
                # ruff: noqa: SIM115
                popen_kwargs["stdout"] = open(self.capture_stdout, "wb")
            else:
                popen_kwargs["stdout"] = PIPE

            if "PYTHONIOENCODING" not in popen_kwargs["env"]:
                popen_kwargs["env"]["PYTHONIOENCODING"] = "utf-8"

        if self.working_dir is not None:
            popen_kwargs["cwd"] = self.working_dir

        # TODO: exclude the subprocess from coverage more gracefully
        _stop_coverage()

        proc = Popen(cmd, **popen_kwargs)

        # signal pass through
        def handle_sigint(signum, _frame):
            # sigint is not handled on windows
            signum = signal.CTRL_C_EVENT if self._is_windows else signum
            proc.send_signal(signum)

        old_sigint_handler = signal.signal(signal.SIGINT, handle_sigint)

        # send data to the subprocess and wait for it to finish
        (captured_stdout, _) = proc.communicate(input)

        if self.capture_stdout is True:
            self.context.save_task_output(self.invocation, captured_stdout)

        # restore signal handler
        signal.signal(signal.SIGINT, old_sigint_handler)

        return proc.returncode

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Optional[str]:
        executor_type = config["type"]
        if executor_type == "auto":
            extra_options = set(config.keys()) - {"type"}
            if extra_options:
                return f"Unexpected keys for executor config: {extra_options!r}"
        elif executor_type not in cls.__executor_types:
            return f"Unknown executor type: {executor_type!r}"
        else:
            return cls.__executor_types[executor_type].validate_executor_config(config)
        return None

    @classmethod
    def validate_executor_config(cls, config: Dict[str, Any]) -> Optional[str]:
        """To be overridden by subclasses if they accept options"""
        extra_options = set(config.keys()) - {"type"}
        if extra_options:
            return f"Unexpected keys for executor config: {extra_options!r}"
        return None


def _stop_coverage():
    """
    Running coverage around subprocesses seems to be problematic, esp. on windows.
    There's probably a more elegant solution that this.
    """
    if "coverage" in sys.modules:
        # If Coverage is running then it ends here
        from coverage import Coverage

        cov = Coverage.current()
        if cov:
            cov.stop()
            cov.save()
