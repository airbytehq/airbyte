import json
from pathlib import Path

try:
    import tomllib as tomli
except ImportError:
    import tomli  # type: ignore[no-redef]

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from .exceptions import PoeException


class PoeConfig:
    KNOWN_SHELL_INTERPRETERS = (
        "posix",
        "sh",
        "bash",
        "zsh",
        "fish",
        "pwsh",  # powershell >= 6
        "powershell",  # any version of powershell
        "python",
    )

    """
    Options allowed directly under tool.poe in pyproject.toml
    """
    __options__ = {
        "default_task_type": str,
        "default_array_task_type": str,
        "default_array_item_task_type": str,
        "env": dict,
        "envfile": (str, list),
        "executor": dict,
        "include": (str, list, dict),
        "poetry_command": str,
        "poetry_hooks": dict,
        "shell_interpreter": (str, list),
        "verbosity": int,
    }

    """
    This can be overridden, for example to align with poetry
    """
    _baseline_verbosity: int = 0

    def __init__(
        self,
        cwd: Optional[Union[Path, str]] = None,
        table: Optional[Mapping[str, Any]] = None,
        config_name: str = "pyproject.toml",
    ):
        self.cwd = Path().resolve() if cwd is None else Path(cwd)
        self._poe = {} if table is None else dict(table)
        self._config_name = config_name
        self._project_dir: Optional[Path] = None

    @property
    def executor(self) -> Mapping[str, Any]:
        return self._poe.get("executor", {"type": "auto"})

    @property
    def tasks(self) -> Mapping[str, Any]:
        return self._poe.get("tasks", {})

    @property
    def default_task_type(self) -> str:
        return self._poe.get("default_task_type", "cmd")

    @property
    def default_array_task_type(self) -> str:
        return self._poe.get("default_array_task_type", "sequence")

    @property
    def default_array_item_task_type(self) -> str:
        return self._poe.get("default_array_item_task_type", "ref")

    @property
    def global_env(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return self._poe.get("env", {})

    @property
    def global_envfile(self) -> Optional[str]:
        return self._poe.get("envfile")

    @property
    def shell_interpreter(self) -> Tuple[str, ...]:
        raw_value = self._poe.get("shell_interpreter", "posix")
        if isinstance(raw_value, list):
            return tuple(raw_value)
        return (raw_value,)

    @property
    def verbosity(self) -> int:
        return self._poe.get("verbosity", self._baseline_verbosity)

    @property
    def project(self) -> Any:
        return self._project

    @property
    def project_dir(self) -> str:
        return str(self._project_dir or self.cwd)

    def load(self, target_dir: Optional[str] = None):
        if self._poe:
            return

        config_path = self.find_config_file(target_dir)
        try:
            self._project = self._read_config_file(config_path)
            self._poe = self._project["tool"]["poe"]
        except KeyError:
            raise PoeException(
                f"No poe configuration found in file at {self._config_name}"
            )
        self._project_dir = config_path.parent
        self._load_includes(self._project_dir)

    def validate(self):
        from .executor import PoeExecutor
        from .task import PoeTask

        # Validate keys
        supported_keys = {"tasks", *self.__options__}
        unsupported_keys = set(self._poe) - supported_keys
        if unsupported_keys:
            raise PoeException(f"Unsupported keys in poe config: {unsupported_keys!r}")

        # Validate types of option values
        for key, option_type in self.__options__.items():
            if key in self._poe and not isinstance(self._poe[key], option_type):
                raise PoeException(
                    f"Unsupported value for option {key!r}, expected type to be "
                    f"{option_type.__name__}."
                )

        # Validate executor config
        error = PoeExecutor.validate_config(self.executor)
        if error:
            raise PoeException(error)

        # Validate default_task_type value
        if not PoeTask.is_task_type(self.default_task_type, content_type=str):
            raise PoeException(
                "Unsupported value for option `default_task_type` "
                f"{self.default_task_type!r}"
            )

        # Validate default_array_task_type value
        if not PoeTask.is_task_type(self.default_array_task_type, content_type=list):
            raise PoeException(
                "Unsupported value for option `default_array_task_type` "
                f"{self.default_array_task_type!r}"
            )

        # Validate default_array_item_task_type value
        if not PoeTask.is_task_type(self.default_array_item_task_type):
            raise PoeException(
                "Unsupported value for option `default_array_item_task_type` "
                f"{self.default_array_item_task_type!r}"
            )

        # Validate env value
        for key, value in self.global_env.items():
            if isinstance(value, dict):
                if tuple(value.keys()) != ("default",) or not isinstance(
                    value["default"], str
                ):
                    raise PoeException(
                        f"Invalid declaration at {key!r} in option `env`: {value!r}"
                    )
            elif not isinstance(value, str):
                raise PoeException(
                    f"Value of {key!r} in option `env` should be a string, but found "
                    f"{type(value)!r}"
                )

        # Validate tasks
        for task_name, task_def in self.tasks.items():
            error = PoeTask.validate_def(task_name, task_def, self)
            if error is None:
                continue
            raise PoeException(error)

        # Validate shell_interpreter type
        for interpreter in self.shell_interpreter:
            if interpreter not in self.KNOWN_SHELL_INTERPRETERS:
                raise PoeException(
                    f"Unsupported value {interpreter!r} for option `shell_interpreter`."
                )

        # Validate default verbosity.
        if self.verbosity < -1 or self.verbosity > 2:
            raise PoeException(
                f"Invalid value for option `verbosity`: {self.verbosity!r}. "
                "Should be between -1 and 2."
            )

    def find_config_file(self, target_dir: Optional[str] = None) -> Path:
        """
        Resolve a path to a self._config_name using one of two strategies:
          1. If target_dir is provided then only look there, (accept path to config file
             or to a directory).
          2. Otherwise look for the self._config_name in the current working directory,
             following by all parent directories in ascending order.

        Both strategies result in an Exception on failure.
        """
        if target_dir:
            target_path = Path(target_dir).resolve()
            if not (
                target_path.name.endswith(".toml") or target_path.name.endswith(".json")
            ):
                target_path = target_path.joinpath(self._config_name)
            if not target_path.exists():
                raise PoeException(
                    f"Poe could not find a {self._config_name} file at the given "
                    f"location: {target_dir}"
                )
            return target_path

        maybe_result = self.cwd.joinpath(self._config_name)
        while not maybe_result.exists():
            if len(maybe_result.parents) == 1:
                raise PoeException(
                    f"Poe could not find a {self._config_name} file in {self.cwd} or"
                    " its parents"
                )
            maybe_result = maybe_result.parents[1].joinpath(self._config_name).resolve()
        return maybe_result

    def _load_includes(self, project_dir: Path):
        include_option: Union[str, Sequence[str]] = self._poe.get("include", tuple())
        includes: List[Dict[str, str]] = []

        if isinstance(include_option, str):
            includes.append({"path": include_option})
        elif isinstance(include_option, dict):
            includes.append(include_option)
        elif isinstance(include_option, list):
            valid_keys = {"path", "cwd"}
            for include in include_option:
                if isinstance(include, str):
                    includes.append({"path": include})
                elif (
                    isinstance(include, dict)
                    and include.get("path")
                    and set(include.keys()) <= valid_keys
                ):
                    includes.append(include)
                else:
                    raise PoeException(
                        f"Invalid item for the include option {include!r}"
                    )

        for include in includes:
            include_path = project_dir.joinpath(include["path"]).resolve()

            if not include_path.exists():
                # TODO: print warning in verbose mode, requires access to ui somehow
                continue

            try:
                include_config = PoeConfig(
                    cwd=include.get("cwd", self.project_dir),
                    table=self._read_config_file(include_path)["tool"]["poe"],
                )
                include_config._project_dir = self._project_dir
            except (PoeException, KeyError) as error:
                raise PoeException(
                    f"Invalid content in included file from {include_path}", error
                ) from error

            self._merge_config(include_config)

    def _merge_config(self, include_config: "PoeConfig"):
        from .task import PoeTask

        # Env is special because it can be extended rather than just overwritten
        if include_config.global_env:
            self._poe["env"] = {**include_config.global_env, **self._poe.get("env", {})}

        if include_config.global_envfile and "envfile" not in self._poe:
            self._poe["envfile"] = include_config.global_envfile

        # Includes additional tasks with preserved ordering
        self._poe["tasks"] = own_tasks = self._poe.get("tasks", {})
        for task_name, task_def in include_config.tasks.items():
            if task_name in own_tasks:
                # don't override tasks from the base config
                continue

            task_def = PoeTask.normalize_task_def(task_def, include_config)
            if include_config.cwd:
                # Override the config of each task to use the include level cwd as a
                # base for the task level cwd
                if "cwd" in task_def:
                    # rebase the configured cwd onto the include level cwd
                    task_def["cwd"] = str(
                        Path(include_config.cwd)
                        .resolve()
                        .joinpath(task_def["cwd"])
                        .relative_to(self.project_dir)
                    )
                else:
                    task_def["cwd"] = str(include_config.cwd)

            own_tasks[task_name] = task_def

    @staticmethod
    def _read_config_file(path: Path) -> Mapping[str, Any]:
        try:
            with path.open("rb") as file:
                if path.suffix.endswith(".json"):
                    return json.load(file)
                else:
                    return tomli.load(file)

        except tomli.TOMLDecodeError as error:
            raise PoeException(f"Couldn't parse toml file at {path}", error) from error

        except json.decoder.JSONDecodeError as error:
            raise PoeException(
                f"Couldn't parse json file from {path}", error
            ) from error

        except Exception as error:
            raise PoeException(f"Couldn't open file at {path}") from error
