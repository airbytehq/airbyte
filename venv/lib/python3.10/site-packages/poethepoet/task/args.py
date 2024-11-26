from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

if TYPE_CHECKING:
    from argparse import ArgumentParser

    from ..env.manager import EnvVarsManager

ArgParams = Dict[str, Any]
ArgsDef = Union[List[str], List[ArgParams], Dict[str, ArgParams]]

arg_param_schema: Dict[str, Union[Type, Tuple[Type, ...]]] = {
    "default": (str, int, float, bool),
    "help": str,
    "name": str,
    "options": (list, tuple),
    "positional": (bool, str),
    "required": bool,
    "type": str,
    "multiple": (bool, int),
}
arg_types: Dict[str, Type] = {
    "string": str,
    "float": float,
    "integer": int,
    "boolean": bool,
}


class PoeTaskArgs:
    _args: Tuple[ArgParams, ...]

    def __init__(
        self,
        args_def: ArgsDef,
        task_name: str,
        program_name: str,
        env: "EnvVarsManager",
    ):
        self._args = self._normalize_args_def(args_def)
        self._program_name = program_name
        self._task_name = task_name
        self._env = env

    @classmethod
    def _normalize_args_def(cls, args_def: ArgsDef) -> Tuple[ArgParams, ...]:
        """
        args_def can be defined as a dictionary of ArgParams, or a list of strings, or
        ArgParams. Here we normalize it to a list of ArgParams, assuming that it has
        already been validated.
        """
        result = []
        if isinstance(args_def, list):
            for item in args_def:
                if isinstance(item, str):
                    result.append({"name": item, "options": (f"--{item}",)})
                else:
                    result.append(
                        dict(
                            item,
                            options=cls._get_arg_options_list(item),
                        )
                    )
        else:
            for name, params in args_def.items():
                result.append(
                    dict(
                        params,
                        name=name,
                        options=cls._get_arg_options_list(params, name),
                    )
                )
        return tuple(result)

    @staticmethod
    def _get_arg_options_list(arg: ArgParams, name: Optional[str] = None):
        position = arg.get("positional", False)
        name = name or arg["name"]
        if position:
            if isinstance(position, str):
                return [position]
            return [name]
        return tuple(arg.get("options", (f"--{name}",)))

    @classmethod
    def get_help_content(
        cls, args_def: Optional[ArgsDef]
    ) -> List[Tuple[Tuple[str, ...], str, str]]:
        if args_def is None:
            return []

        def format_default(arg) -> str:
            default = arg.get("default")
            if default:
                return f"[default: {default}]"
            return ""

        return [
            (arg["options"], arg.get("help", ""), format_default(arg))
            for arg in cls._normalize_args_def(args_def)
        ]

    @classmethod
    def validate_def(cls, task_name: str, args_def: ArgsDef) -> Optional[str]:
        arg_names: Set[str] = set()
        arg_params = []

        if isinstance(args_def, list):
            for item in args_def:
                # can be a list of strings (just arg name) or ArgConfig dictionaries
                if isinstance(item, str):
                    arg_name = item
                elif isinstance(item, dict):
                    arg_name = item.get("name", "")
                    arg_params.append((item, arg_name, task_name))
                else:
                    return f"Arg {item!r} of task {task_name!r} has invlaid type"
                error = cls._validate_name(arg_name, task_name, arg_names)
                if error:
                    return error

        elif isinstance(args_def, dict):
            for arg_name, params in args_def.items():
                error = cls._validate_name(arg_name, task_name, arg_names)
                if error:
                    return error
                if "name" in params:
                    return (
                        f"Unexpected 'name' option for arg {arg_name!r} of task "
                        f"{task_name!r}"
                    )
                arg_params.append((params, arg_name, task_name))

        positional_multiple = None
        for params, arg_name, task_name in arg_params:
            error = cls._validate_type(params, arg_name, task_name)
            if error:
                return error

            error = cls._validate_params(params, arg_name, task_name)
            if error:
                return error

            if params.get("positional", False):
                if positional_multiple:
                    return (
                        f"Only the last positional arg of task {task_name!r} may accept"
                        f" multiple values ({positional_multiple!r})."
                    )
                if params.get("multiple", False):
                    positional_multiple = arg_name

        return None

    @classmethod
    def _validate_name(
        cls, name: Any, task_name: str, arg_names: Set[str]
    ) -> Optional[str]:
        if not isinstance(name, str):
            return f"Arg name {name!r} of task {task_name!r} should be a string"
        if not name.replace("-", "_").isidentifier():
            return (
                f"Arg name {name!r} of task {task_name!r} is not a valid  'identifier'"
                f"see the following documentation for details"
                f"https://docs.python.org/3/reference/lexical_analysis.html#identifiers"
            )
        if name in arg_names:
            return f"Duplicate arg name {name!r} for task {task_name!r}"
        arg_names.add(name)
        return None

    @classmethod
    def _validate_params(
        cls, params: ArgParams, arg_name: str, task_name: str
    ) -> Optional[str]:
        for param, value in params.items():
            if param not in arg_param_schema:
                return (
                    f"Invalid option {param!r} for arg {arg_name!r} of task "
                    f"{task_name!r}"
                )
            if not isinstance(value, arg_param_schema[param]):
                return (
                    f"Invalid value for option {param!r} of arg {arg_name!r} of"
                    f" task {task_name!r}"
                )

        positional = params.get("positional", False)
        if positional:
            if params.get("type") == "boolean":
                return (
                    f"Positional argument {arg_name!r} of task {task_name!r} may not"
                    "have type 'boolean'"
                )
            if params.get("options") is not None:
                return (
                    f"Positional argument {arg_name!r} of task {task_name!r} may not"
                    "have options defined"
                )
            if isinstance(positional, str) and not positional.isidentifier():
                return (
                    f"positional name  {positional!r} for arg {arg_name!r} of task "
                    f"{task_name!r} is not a valid  'identifier' see the following "
                    "documentation for details"
                    "https://docs.python.org/3/reference/lexical_analysis.html#identifiers"
                )

        multiple = params.get("multiple", False)
        if (
            not isinstance(multiple, bool)
            and isinstance(multiple, int)
            and multiple < 2
        ):
            return (
                f"The multiple option for arg {arg_name!r} of {task_name!r}"
                " must be given a boolean or integer >= 2"
            )
        if multiple is not False and params.get("type") == "boolean":
            return (
                "Incompatible param 'multiple' for arg {arg_name!r} of {task_name!r} "
                "with type: 'boolean'"
            )

        return None

    @classmethod
    def _validate_type(
        cls, params: ArgParams, arg_name: str, task_name: str
    ) -> Optional[str]:
        if "type" in params and params["type"] not in arg_types:
            return (
                f"{params['type']!r} is not a valid type for arg {arg_name!r} of task "
                f"{task_name!r}. Choose one of "
                "{"
                f'{" ".join(sorted(str_type for str_type in arg_types.keys()))}'
                "}"
            )
        return None

    def build_parser(self) -> "ArgumentParser":
        import argparse

        parser = argparse.ArgumentParser(
            prog=f"{self._program_name} {self._task_name}",
            add_help=False,
            allow_abbrev=False,
        )
        for arg in self._args:
            parser.add_argument(
                *arg["options"],
                **self._get_argument_params(arg),
            )
        return parser

    def _get_argument_params(self, arg: ArgParams):
        default = arg.get("default")
        if isinstance(default, str):
            default = self._env.fill_template(default)

        result = {
            "default": default,
            "help": arg.get("help", ""),
        }

        required = arg.get("required", False)
        multiple = arg.get("multiple", False)
        arg_type = str(arg.get("type"))

        if multiple is True:
            if required:
                result["nargs"] = "+"
            else:
                result["nargs"] = "*"
        elif multiple and isinstance(multiple, int):
            result["nargs"] = multiple

        if arg.get("positional", False):
            if not multiple and not required:
                result["nargs"] = "?"
        else:
            result["dest"] = arg["name"]
            result["required"] = required

        if arg_type == "boolean":
            result["action"] = "store_false" if default else "store_true"
        else:
            result["type"] = arg_types.get(arg_type, str)

        return result

    def parse(self, extra_args: Sequence[str]):
        parsed_args = vars(self.build_parser().parse_args(extra_args))
        # Ensure positional args are still exposed by name even if they were parsed with
        # alternate identifiers
        for arg in self._args:
            if isinstance(arg.get("positional"), str):
                parsed_args[arg["name"]] = parsed_args[arg["positional"]]
                del parsed_args[arg["positional"]]
        # args named with dash case are converted to snake case before being exposed
        return {name.replace("-", "_"): value for name, value in parsed_args.items()}
