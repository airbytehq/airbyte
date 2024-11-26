from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)

from ..exceptions import ExecutionError, PoeException
from .base import PoeTask, TaskContent, TaskInheritance

if TYPE_CHECKING:
    from ..config import PoeConfig
    from ..context import RunContext
    from ..env.manager import EnvVarsManager
    from ..ui import PoeUi


DEFAULT_CASE = "__default__"


class SwitchTask(PoeTask):
    """
    A task that runs one of several `case` subtasks depending on the output of a
    `switch` subtask.
    """

    content: List[Union[str, Dict[str, Any]]]

    __key__ = "switch"
    __content_type__: Type = list
    __options__: Dict[str, Union[Type, Tuple[Type, ...]]] = {
        "control": (str, dict),
        "default": str,
    }

    def __init__(
        self,
        name: str,
        content: TaskContent,
        options: Dict[str, Any],
        ui: "PoeUi",
        config: "PoeConfig",
        invocation: Tuple[str, ...],
        capture_stdout: bool = False,
        inheritance: Optional[TaskInheritance] = None,
    ):
        super().__init__(
            name, content, options, ui, config, invocation, False, inheritance
        )

        control_task_name = f"{name}[control]"
        control_invocation: Tuple[str, ...] = (control_task_name,)
        if self.options.get("args"):
            self.options["control"]["args"] = self.options["args"]
            control_invocation = (*control_invocation, *invocation[1:])

        self.control_task = self.from_def(
            task_def=self.options.get("control", ""),
            task_name=control_task_name,
            config=config,
            invocation=control_invocation,
            ui=ui,
            capture_stdout=True,
            inheritance=TaskInheritance.from_task(self),
        )

        self.switch_tasks = {}
        for item in cast(List[Dict[str, Any]], content):
            task_def = {key: value for key, value in item.items() if key != "case"}

            task_invocation: Tuple[str, ...] = (name,)
            if self.options.get("args"):
                task_def["args"] = self.options["args"]
                task_invocation = (*task_invocation, *invocation[1:])

            for case_key in self._get_case_keys(item):
                self.switch_tasks[case_key] = self.from_def(
                    task_def=task_def,
                    task_name=f"{name}__{case_key}",
                    config=config,
                    invocation=task_invocation,
                    ui=ui,
                    capture_stdout=self.options.get("capture_stdout", capture_stdout),
                    inheritance=TaskInheritance.from_task(self),
                )

    def _handle_run(
        self,
        context: "RunContext",
        extra_args: Sequence[str],
        env: "EnvVarsManager",
    ) -> int:
        named_arg_values = self.get_named_arg_values(env)
        env.update(named_arg_values)

        if not named_arg_values and any(arg.strip() for arg in extra_args):
            raise PoeException(f"Switch task {self.name!r} does not accept arguments")

        # Indicate on the global context that there are multiple stages to this task
        context.multistage = True

        task_result = self.control_task.run(
            context=context,
            extra_args=extra_args if self.options.get("args") else tuple(),
            parent_env=env,
        )
        if task_result:
            raise ExecutionError(
                f"Switch task {self.name!r} aborted after failed control task"
            )

        if context.dry:
            self._print_action(
                "unresolved case for switch task", dry=True, unresolved=True
            )
            return 0

        control_task_output = context.get_task_output(self.control_task.invocation)
        case_task = self.switch_tasks.get(
            control_task_output, self.switch_tasks.get(DEFAULT_CASE)
        )

        if case_task is None:
            if self.options.get("default", "fail") == "pass":
                return 0
            raise ExecutionError(
                f"Control value {control_task_output!r} did not match any cases in "
                f"switch task {self.name!r}."
            )

        return case_task.run(context=context, extra_args=extra_args, parent_env=env)

    @classmethod
    def _get_case_keys(cls, task_def: Dict[str, Any]) -> List[Any]:
        case_value = task_def.get("case", DEFAULT_CASE)
        if isinstance(case_value, list):
            return case_value
        return [case_value]

    @classmethod
    def _validate_task_def(
        cls, task_name: str, task_def: Dict[str, Any], config: "PoeConfig"
    ) -> Optional[str]:
        from collections import defaultdict

        control_task_def = task_def.get("control")
        if not control_task_def:
            return f"Switch task {task_name!r} has no control task."

        allowed_control_task_types = ("expr", "cmd", "script")
        if isinstance(control_task_def, dict) and not any(
            key in control_task_def for key in allowed_control_task_types
        ):
            return (
                f"Control task for {task_name!r} must have a type that is one of "
                f"{allowed_control_task_types!r}"
            )

        control_task_issue = PoeTask.validate_def(
            f"{task_name}[control]", control_task_def, config, anonymous=True
        )
        if control_task_issue:
            return control_task_issue

        cases: MutableMapping[Any, int] = defaultdict(int)
        for switch_task in task_def["switch"]:
            for case_key in cls._get_case_keys(switch_task):
                cases[case_key] += 1

            case_key = switch_task.get("case", DEFAULT_CASE)
            for invalid_option in ("args", "deps"):
                if invalid_option in switch_task:
                    if case_key is DEFAULT_CASE:
                        return (
                            f"Default case of switch task {task_name!r} includes "
                            f"invalid option {invalid_option!r}"
                        )
                    return (
                        f"Case {case_key!r} switch task {task_name!r} include invalid "
                        f"option {invalid_option!r}"
                    )

            switch_task_issue = PoeTask.validate_def(
                f"{task_name}[{case_key}]",
                switch_task,
                config,
                anonymous=True,
                extra_options=("case",),
            )
            if switch_task_issue:
                return switch_task_issue

        for case, count in cases.items():
            if count > 1:
                if case is DEFAULT_CASE:
                    return (
                        f"Switch task {task_name!r} includes more than one default case"
                    )
                return (
                    f"Switch task {task_name!r} includes more than one case for "
                    f"{case!r}"
                )

        if "default" in task_def:
            if task_def["default"] not in ("pass", "fail"):
                return (
                    f"The 'default' option for switch task {task_name!r} should be one "
                    "of ('pass', 'fail')"
                )
            if DEFAULT_CASE in cases:
                return (
                    f"Switch task {task_name!r} should not have both a default case "
                    f"and the 'default' option."
                )

        return None
