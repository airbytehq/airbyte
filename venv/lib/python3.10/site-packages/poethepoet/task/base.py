import re
import sys
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Collection,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from ..exceptions import PoeException

if TYPE_CHECKING:
    from ..config import PoeConfig
    from ..context import RunContext
    from ..env.manager import EnvVarsManager
    from ..ui import PoeUi


TaskDef = Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]

_TASK_NAME_PATTERN = re.compile(r"^\w[\w\d\-\_\+\:]*$")


class MetaPoeTask(type):
    """
    This metaclass makes all decendents of PoeTask (task types) register themselves on
    declaration and validates that they include the expected class attributes.
    """

    def __init__(cls, *args):
        super().__init__(*args)
        if cls.__name__ == "PoeTask":
            return
        assert isinstance(getattr(cls, "__key__", None), str)
        assert isinstance(getattr(cls, "__options__", None), dict)
        PoeTask._PoeTask__task_types[cls.__key__] = cls


TaskContent = Union[str, List[Union[str, Dict[str, Any]]]]


class TaskInheritance(NamedTuple):
    """
    Collection of inheritanced config from a parent task to a child task
    """

    cwd: str

    @classmethod
    def from_task(cls, parent_task: "PoeTask"):
        return cls(cwd=str(parent_task.options.get("cwd", parent_task.inheritance.cwd)))


class PoeTask(metaclass=MetaPoeTask):
    name: str
    content: TaskContent
    options: Dict[str, Any]
    inheritance: TaskInheritance
    named_args: Optional[Dict[str, str]] = None

    __options__: Dict[str, Union[Type, Tuple[Type, ...]]] = {}
    __content_type__: Type = str
    __base_options: Dict[str, Union[Type, Tuple[Type, ...]]] = {
        "args": (dict, list),
        "capture_stdout": str,
        "cwd": str,
        "deps": list,
        "env": dict,
        "envfile": (str, list),
        "executor": dict,
        "help": str,
        "uses": dict,
    }
    __task_types: Dict[str, Type["PoeTask"]] = {}

    __upstream_invocations: Optional[
        Dict[str, Union[List[Tuple[str, ...]], Dict[str, Tuple[str, ...]]]]
    ] = None

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
        self.name = name
        self.content = content
        self.options = dict(options, capture_stdout=True) if capture_stdout else options
        self._ui = ui
        self._config = config
        self._is_windows = sys.platform == "win32"
        self.invocation = invocation
        self.inheritance = inheritance or TaskInheritance(cwd=str(config.project_dir))

    @classmethod
    def from_config(
        cls,
        task_name: str,
        config: "PoeConfig",
        ui: "PoeUi",
        invocation: Tuple[str, ...],
        capture_stdout: Optional[bool] = None,
        inheritance: Optional[TaskInheritance] = None,
    ) -> "PoeTask":
        task_def = config.tasks.get(task_name)
        if not task_def:
            raise PoeException(f"Cannot instantiate unknown task {task_name!r}")
        return cls.from_def(
            task_def,
            task_name,
            config,
            ui,
            invocation=invocation,
            capture_stdout=capture_stdout,
            inheritance=inheritance,
        )

    @classmethod
    def from_def(
        cls,
        task_def: TaskDef,
        task_name: str,
        config: "PoeConfig",
        ui: "PoeUi",
        invocation: Tuple[str, ...],
        array_item: Union[bool, str] = False,
        capture_stdout: Optional[bool] = None,
        inheritance: Optional[TaskInheritance] = None,
    ) -> "PoeTask":
        task_type = cls.resolve_task_type(task_def, config, array_item)
        if task_type is None:
            # Something is wrong with this task_def
            raise cls.Error(cls.validate_def(task_name, task_def, config))

        options: Dict[str, Any] = {}
        if capture_stdout is not None:
            # Override config because we want to specifically capture the stdout of this
            # task for internal use
            options["capture_stdout"] = capture_stdout

        if isinstance(task_def, (str, list)):
            task_def = cls.normalize_task_def(
                task_def, config, task_type=cls.__task_types[task_type]
            )

        assert isinstance(task_def, dict)
        options = dict(task_def, **options)
        content = options.pop(task_type)
        return cls.__task_types[task_type](
            name=task_name,
            content=content,
            options=options,
            ui=ui,
            config=config,
            invocation=invocation,
            inheritance=inheritance,
        )

    @classmethod
    def normalize_task_def(
        cls,
        task_def: TaskDef,
        config: "PoeConfig",
        *,
        task_type: Optional[Type["PoeTask"]] = None,
        array_item: Union[bool, str] = False,
    ):
        if isinstance(task_def, dict):
            return task_def

        if not task_type:
            task_type_key = cls.resolve_task_type(task_def, config, array_item)
            assert task_type_key
            task_type = cls.__task_types[task_type_key]

        return {getattr(task_type, "__key__", "__key_unknown__"): task_def}

    @classmethod
    def resolve_task_type(
        cls,
        task_def: TaskDef,
        config: "PoeConfig",
        array_item: Union[bool, str] = False,
    ) -> Optional[str]:
        if isinstance(task_def, str):
            if array_item:
                return (
                    array_item
                    if isinstance(array_item, str)
                    else config.default_array_item_task_type
                )
            else:
                return config.default_task_type

        elif isinstance(task_def, dict):
            task_type_keys = set(task_def.keys()).intersection(cls.__task_types)
            if len(task_type_keys) == 1:
                return next(iter(task_type_keys))

        elif isinstance(task_def, list):
            return config.default_array_task_type

        return None

    def get_named_arg_values(self, env: "EnvVarsManager") -> Dict[str, str]:
        try:
            split_index = self.invocation.index("--")
            parse_args = self.invocation[1:split_index]
        except ValueError:
            parse_args = self.invocation[1:]

        if self.named_args is None:
            self.named_args = self._parse_named_args(parse_args, env)

        if not self.named_args:
            return {}

        return self.named_args

    def _parse_named_args(
        self, extra_args: Sequence[str], env: "EnvVarsManager"
    ) -> Optional[Dict[str, str]]:
        if args_def := self.options.get("args"):
            from .args import PoeTaskArgs

            return PoeTaskArgs(args_def, self.name, self._ui.program_name, env).parse(
                extra_args
            )

        return None

    def run(
        self,
        context: "RunContext",
        extra_args: Sequence[str] = tuple(),
        parent_env: Optional["EnvVarsManager"] = None,
    ) -> int:
        """
        Run this task
        """
        upstream_invocations = self._get_upstream_invocations(context)

        if context.dry and upstream_invocations.get("uses", {}):
            self._print_action(
                (
                    "unresolved dependency task results via uses option for task "
                    f"{self.name!r}"
                ),
                dry=True,
                unresolved=True,
            )
            return 0

        return self._handle_run(
            context,
            extra_args,
            context.get_task_env(
                parent_env,
                self.options.get("envfile"),
                self.options.get("env"),
                upstream_invocations["uses"],
            ),
        )

    def _handle_run(
        self,
        context: "RunContext",
        extra_args: Sequence[str],
        env: "EnvVarsManager",
    ) -> int:
        """
        This method must be implemented by a subclass and return a single executor
        result.
        """
        raise NotImplementedError

    def _get_executor(
        self,
        context: "RunContext",
        env: "EnvVarsManager",
    ):
        return context.get_executor(
            self.invocation,
            env,
            working_dir=self.get_working_dir(env),
            executor_config=self.options.get("executor"),
            capture_stdout=self.options.get("capture_stdout", False),
        )

    def get_working_dir(
        self,
        env: "EnvVarsManager",
    ) -> Path:
        cwd_option = env.fill_template(self.options.get("cwd", self.inheritance.cwd))
        working_dir = Path(cwd_option)

        if not working_dir.is_absolute():
            working_dir = self._config.project_dir / working_dir

        return working_dir

    def iter_upstream_tasks(
        self, context: "RunContext"
    ) -> Iterator[Tuple[str, "PoeTask"]]:
        invocations = self._get_upstream_invocations(context)
        for invocation in invocations["deps"]:
            yield ("", self._instantiate_dep(invocation, capture_stdout=False))
        for key, invocation in invocations["uses"].items():
            yield (key, self._instantiate_dep(invocation, capture_stdout=True))

    def _get_upstream_invocations(self, context: "RunContext"):
        """
        NB. this memoization assumes the context (and contained env vars) will be the
        same in all instances for the lifetime of this object. Whilst this should be OK
        for all current usecases is it strictly speaking something that this object
        should not know enough to safely assume. So we probably want to revisit this.
        """
        import shlex

        if self.__upstream_invocations is None:
            env = context.get_task_env(
                None, self.options.get("envfile"), self.options.get("env")
            )
            env.update(self.get_named_arg_values(env))

            self.__upstream_invocations = {
                "deps": [
                    tuple(shlex.split(env.fill_template(task_ref)))
                    for task_ref in self.options.get("deps", tuple())
                ],
                "uses": {
                    key: tuple(shlex.split(env.fill_template(task_ref)))
                    for key, task_ref in self.options.get("uses", {}).items()
                },
            }

        return self.__upstream_invocations

    def _instantiate_dep(
        self, invocation: Tuple[str, ...], capture_stdout: bool
    ) -> "PoeTask":
        return self.from_config(
            invocation[0],
            config=self._config,
            ui=self._ui,
            invocation=invocation,
            capture_stdout=capture_stdout,
        )

    def has_deps(self) -> bool:
        return bool(self.options.get("deps", False) or self.options.get("uses", False))

    @classmethod
    def validate_def(
        cls,
        task_name: str,
        task_def: TaskDef,
        config: "PoeConfig",
        *,
        anonymous: bool = False,
        extra_options: Collection[str] = tuple(),
    ) -> Optional[str]:
        """
        Check the given task name and definition for validity and return a message
        describing the first encountered issue if any.
        If anonymous is set to True then task_name is not validated.
        """
        if not anonymous and (not (task_name[0].isalpha() or task_name[0] == "_")):
            return (
                f"Invalid task name: {task_name!r}. Task names must start with a letter"
                " or underscore."
            )

        if not anonymous and not _TASK_NAME_PATTERN.match(task_name):
            return (
                f"Invalid task name: {task_name!r}. Task names characters must be "
                "alphanumeric, colon, underscore or dash."
            )

        if isinstance(task_def, dict):
            task_type_keys = set(task_def.keys()).intersection(cls.__task_types)
            if len(task_type_keys) != 1:
                return (
                    f"Invalid task: {task_name!r}. Task definition must include exactly"
                    f" one task key from {set(cls.__task_types)!r}"
                )
            task_type_key = next(iter(task_type_keys))
            task_content = task_def[task_type_key]
            task_type = cls.__task_types[task_type_key]
            if not isinstance(task_content, task_type.__content_type__):
                return (
                    f"Invalid task: {task_name!r}. Content for {task_type.__name__} "
                    f"must be a {task_type.__content_type__.__name__}"
                )

            for key in set(task_def) - {task_type_key}:
                expected_type = cls.__base_options.get(
                    key, task_type.__options__.get(key)
                )
                if expected_type is None:
                    if key not in extra_options:
                        return (
                            f"Invalid task: {task_name!r}. Unrecognised option "
                            f"{key!r} for task of type: {task_type_key}."
                        )
                elif not isinstance(task_def[key], expected_type):
                    return (
                        f"Invalid task: {task_name!r}. Option {key!r} should "
                        f"have a value of type {expected_type!r}"
                    )
            else:
                if hasattr(task_type, "_validate_task_def"):
                    task_type_issue = task_type._validate_task_def(
                        task_name, task_def, config
                    )
                    if task_type_issue:
                        return task_type_issue

            if "args" in task_def:
                from .args import PoeTaskArgs

                return PoeTaskArgs.validate_def(task_name, task_def["args"])

            if "cwd" in task_def:
                path = Path(config.project_dir).joinpath(task_def["cwd"]).resolve()
                if not str(path).startswith(config.project_dir):
                    return (
                        f"Invalid task: {task_name!r}. cwd option may not specify a "
                        "directory outside of the project."
                    )

            if "\n" in task_def.get("help", ""):
                return (
                    f"Invalid task: {task_name!r}. Help messages cannot contain "
                    "line breaks"
                )

            if task_def.get("use_exec") and task_def.get("capture_stdout"):
                return (
                    f"Invalid task: {task_name!r}, 'use_exec' and 'capture_stdout'"
                    " options cannot be both provided on the same task."
                )

            all_task_names = set(config.tasks.keys())

            if "deps" in task_def:
                for dep in task_def["deps"]:
                    dep_task_name = dep.split(" ", 1)[0]
                    if dep_task_name not in all_task_names:
                        return (
                            f"Invalid task: {task_name!r}. deps options contains "
                            f"reference to unknown task: {dep_task_name!r}"
                        )

                    referenced_task = config.tasks[dep_task_name]
                    if isinstance(referenced_task, dict) and referenced_task.get(
                        "use_exec"
                    ):
                        return (
                            f"Invalid task: {task_name!r}. deps options contains "
                            "reference to task with use_exec set to true: "
                            f"{dep_task_name!r}"
                        )

            if "uses" in task_def:
                from ..helpers import is_valid_env_var

                for key, dep in task_def["uses"].items():
                    if not is_valid_env_var(key):
                        return (
                            f"Invalid task: {task_name!r} uses options contains invalid"
                            f" key: {key!r}"
                        )

                    dep_task_name = dep.split(" ", 1)[0]
                    if dep_task_name not in all_task_names:
                        return (
                            f"Invalid task: {task_name!r}. uses options contains "
                            f"reference to unknown task: {dep_task_name!r}"
                        )

                    referenced_task = config.tasks[dep_task_name]
                    if isinstance(referenced_task, dict):
                        if referenced_task.get("use_exec"):
                            return (
                                f"Invalid task: {task_name!r}, 'uses' option references"
                                " task with 'use_exec' set to true: "
                                f"{dep_task_name!r}"
                            )
                        if referenced_task.get("capture_stdout"):
                            return (
                                f"Invalid task: {task_name!r}, 'uses' option references"
                                " task with 'capture_stdout' option set: "
                                f"{dep_task_name!r}"
                            )

        elif isinstance(task_def, list):
            task_type_key = config.default_array_task_type
            task_type = cls.__task_types[task_type_key]
            normalized_task_def = cls.normalize_task_def(
                task_def, config, task_type=task_type
            )
            if hasattr(task_type, "_validate_task_def"):
                task_type_issue = task_type._validate_task_def(
                    task_name, normalized_task_def, config
                )
                if task_type_issue:
                    return task_type_issue

        return None

    @classmethod
    def is_task_type(
        cls, task_def_key: str, content_type: Optional[Type] = None
    ) -> bool:
        """
        Checks whether the given key identifies a known task type.
        Optionally also check whether the given content_type matches the type of content
        for this tasks type.
        """
        return task_def_key in cls.__task_types and (
            content_type is None
            or cls.__task_types[task_def_key].__content_type__ is content_type
        )

    @classmethod
    def get_task_types(cls, content_type: Optional[Type] = None) -> Tuple[str, ...]:
        if content_type:
            return tuple(
                task_type
                for task_type, task_cls in cls.__task_types.items()
                if task_cls.__content_type__ is content_type
            )
        return tuple(task_type for task_type in cls.__task_types.keys())

    @classmethod
    def _validate_task_def(
        cls, task_name: str, task_def: Dict[str, Any], config: "PoeConfig"
    ) -> Optional[str]:
        """
        To be overriden by subclasses to check the given task definition for validity
        specific to that task type and return a message describing the first encountered
        issue if any.
        """
        issue = None
        return issue

    def _print_action(self, action: str, dry: bool, unresolved: bool = False):
        """
        Print the action taken by a task just before executing it.
        """
        min_verbosity = -1 if dry else 0
        arrow = (
            "??" if unresolved else "<=" if self.options.get("capture_stdout") else "=>"
        )
        self._ui.print_msg(
            f"<hl>Poe {arrow}</hl> <action>{action}</action>", min_verbosity
        )

    class Error(Exception):
        pass
