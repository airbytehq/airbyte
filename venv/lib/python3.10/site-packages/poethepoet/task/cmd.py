import shlex
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, Tuple, Type, Union

from ..exceptions import PoeException
from .base import PoeTask

if TYPE_CHECKING:
    from ..config import PoeConfig
    from ..context import RunContext
    from ..env.manager import EnvVarsManager


class CmdTask(PoeTask):
    """
    A task consisting of a reference to a shell command
    """

    content: str

    __key__ = "cmd"
    __options__: Dict[str, Union[Type, Tuple[Type, ...]]] = {
        "use_exec": bool,
    }

    def _handle_run(
        self,
        context: "RunContext",
        extra_args: Sequence[str],
        env: "EnvVarsManager",
    ) -> int:
        named_arg_values = self.get_named_arg_values(env)
        env.update(named_arg_values)

        if named_arg_values:
            # If named arguments are defined then pass only arguments following a double
            # dash token: `--`
            try:
                split_index = extra_args.index("--")
                extra_args = extra_args[split_index + 1 :]
            except ValueError:
                extra_args = tuple()

        cmd = (*self._resolve_args(context, env), *extra_args)

        self._print_action(shlex.join(cmd), context.dry)

        return self._get_executor(context, env).execute(
            cmd, use_exec=self.options.get("use_exec", False)
        )

    def _resolve_args(self, context: "RunContext", env: "EnvVarsManager"):
        from ..helpers.command import parse_poe_cmd, resolve_command_tokens
        from ..helpers.command.ast_core import ParseError

        try:
            command_lines = parse_poe_cmd(self.content).command_lines
        except ParseError as error:
            raise PoeException(
                f"Couldn't parse command line for task {self.name!r}: {error.args[0]}"
            ) from error

        if not command_lines:
            raise PoeException(
                f"Invalid cmd task {self.name!r} does not include any command lines"
            )
        if len(command_lines) > 1:
            raise PoeException(
                f"Invalid cmd task {self.name!r} includes multiple command lines"
            )

        working_dir = self.get_working_dir(env)

        result = []
        for cmd_token, has_glob in resolve_command_tokens(
            command_lines[0], env.to_dict()
        ):
            if has_glob:
                # Resolve glob pattern from the working directory
                result.extend([str(match) for match in working_dir.glob(cmd_token)])
            else:
                result.append(cmd_token)

        return result

    @classmethod
    def _validate_task_def(
        cls, task_name: str, task_def: Dict[str, Any], config: "PoeConfig"
    ) -> Optional[str]:
        if not task_def["cmd"].strip():
            return f"Task {task_name!r} has no content"

        return None
