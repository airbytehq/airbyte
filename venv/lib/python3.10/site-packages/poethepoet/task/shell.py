import re
from os import environ
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from ..exceptions import PoeException
from .base import PoeTask

if TYPE_CHECKING:
    from ..config import PoeConfig
    from ..context import RunContext
    from ..env.manager import EnvVarsManager


class ShellTask(PoeTask):
    """
    A task consisting of a reference to a shell command
    """

    content: str

    __key__ = "shell"
    __options__: Dict[str, Union[Type, Tuple[Type, ...]]] = {"interpreter": (str, list)}

    def _handle_run(
        self,
        context: "RunContext",
        extra_args: Sequence[str],
        env: "EnvVarsManager",
    ) -> int:
        named_arg_values = self.get_named_arg_values(env)
        env.update(named_arg_values)

        if not named_arg_values and any(arg.strip() for arg in extra_args):
            raise PoeException(f"Shell task {self.name!r} does not accept arguments")

        interpreter_cmd = self.resolve_interpreter_cmd()
        if not interpreter_cmd:
            config_value = self._get_interpreter_config()
            message = (
                f"Couldn't locate interpreter executable for {config_value!r} to run "
                "shell task. "
            )
            if self._is_windows and config_value in ("posix", "bash"):
                message += "Installing Git Bash or using WSL should fix this."
            else:
                message += "Some dependencies may be missing from your system."
            raise PoeException(message)

        content = _unindent_code(self.content).rstrip()

        self._print_action(content, context.dry)

        return self._get_executor(context, env).execute(
            interpreter_cmd, input=content.encode()
        )

    def _get_interpreter_config(self) -> Tuple[str, ...]:
        result: Union[str, Tuple[str, ...]] = self.options.get(
            "interpreter", self._config.shell_interpreter
        )
        if isinstance(result, str):
            return (result,)
        return tuple(result)

    def resolve_interpreter_cmd(self) -> Optional[List[str]]:
        """
        Return a formatted command for the first specified interpreter that can be
        located.
        """
        for item in self._get_interpreter_config():
            executable = self._locate_interpreter(item)
            if executable is None:
                continue

            if item in ("pwsh", "powershell"):
                return [executable, "-NoLogo", "-Command", "-"]

            return [executable]

        return None

    def _locate_interpreter(self, interpreter: str) -> Optional[str]:
        from shutil import which

        result = None
        prog_files = environ.get("PROGRAMFILES", "C:\\Program Files")

        # Try use $SHELL from the environment as a hint
        shell_var = environ.get("SHELL", "")
        if shell_var.endswith(f"/{interpreter}") and which(shell_var) == shell_var:
            result = shell_var

        elif interpreter == "posix":
            # look for any known posix shell
            result = (
                self._locate_interpreter("sh")
                or self._locate_interpreter("bash")
                or self._locate_interpreter("zsh")
            )

        elif interpreter == "sh":
            result = which("sh") or which("/bin/sh")

            # Specifically look for git sh on windows
            if result is None and self._is_windows:
                result = which(f"{prog_files}\\Git\\bin\\sh.exe")

        elif interpreter == "bash":
            if self._is_windows:
                # Specifically look for git bash on windows as the preferred option
                # Don't trust bash from the path becuase it might be a useless decoy
                result = (
                    which(f"{prog_files}\\Git\\bin\\bash.exe")
                    or which("/bin/bash")
                    or which("bash")
                )
            else:
                result = which("bash") or which("/bin/bash")

        elif interpreter == "zsh":
            result = which("zsh") or which("/bin/zsh")

        elif interpreter == "fish":
            result = which("fish") or which("/bin/fish")

        elif interpreter in ("pwsh", "powershell"):
            # Look for the pwsh executable and verify the version matches
            result = (
                which("pwsh")
                or which(f"{prog_files}\\PowerShell\\7\\pwsh.exe")
                or which(f"{prog_files}\\PowerShell\\6\\pwsh.exe")
            )

            if result is None and interpreter == "powershell" and self._is_windows:
                # Look for older versions of powershell
                result = which("powershell") or which(
                    environ.get("WINDIR", "C:\\Windows")
                    + "\\System32\\WindowsPowerShell\\v1.0\\powershell.EXE"
                )

        elif interpreter == "python":
            # Exactly which python executable to use is usually resolved by the executor
            result = "python"

        return result

    @classmethod
    def _validate_task_def(
        cls, task_name: str, task_def: Dict[str, Any], config: "PoeConfig"
    ) -> Optional[str]:
        interpreter = task_def.get("interpreter")
        valid_interpreters = config.KNOWN_SHELL_INTERPRETERS

        if isinstance(interpreter, str) and interpreter not in valid_interpreters:
            return (
                "Unsupported value for option `interpreter` for task "
                f"{task_name!r}. Expected one of {valid_interpreters}"
            )

        if isinstance(interpreter, list):
            if len(interpreter) == 0:
                return (
                    "Unsupported value for option `interpreter` for task "
                    f"{task_name!r}. Expected at least one item in list."
                )
            for item in interpreter:
                if item not in valid_interpreters:
                    return (
                        "Unsupported item {item!r} in option `interpreter` for task "
                        f"{task_name!r}. Expected one of {valid_interpreters}"
                    )

        return None


def _unindent_code(python_code: str):
    """
    Unindent all lines by the indent level of the first line.
    This is rather naive, but should usually work as one would naively expect for a
    multiline script in a multiline string value in toml.

    It will not always work correctly if the multiline string itself contains a triple
    quoted multiline python string or similar. Let's say that's OK for now.
    """

    if not python_code.startswith(" "):
        return python_code

    indent = 0
    while python_code[indent] == " ":
        indent += 1

    prefix = " " * indent
    return "\n".join(
        _remove_prefix(line, prefix)
        for line in re.split(r"(?:\r\n|\r|\n)", python_code)
    )


def _remove_prefix(text: str, prefix: str):
    """
    When we drop support for python <3.9 then str.removeprefix can be used
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text
