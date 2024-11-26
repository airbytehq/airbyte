from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from ..exceptions import ExecutionError

if TYPE_CHECKING:
    from .ui import PoeUi


class EnvFileCache:
    _cache: Dict[str, Dict[str, str]] = {}
    _ui: Optional["PoeUi"]
    _project_dir: Path

    def __init__(self, project_dir: Path, ui: Optional["PoeUi"]):
        self._project_dir = project_dir
        self._ui = ui

    def get(self, envfile_path_str: str) -> Dict[str, str]:
        from .parse import parse_env_file

        if envfile_path_str in self._cache:
            return self._cache[envfile_path_str]

        result = {}

        envfile_path = self._project_dir.joinpath(Path(envfile_path_str).expanduser())
        if envfile_path.is_file():
            try:
                with envfile_path.open(encoding="utf-8") as envfile:
                    result = parse_env_file(envfile.readlines())
            except ValueError as error:
                message = error.args[0]
                raise ExecutionError(
                    f"Syntax error in referenced envfile: {envfile_path_str!r};"
                    f" {message}"
                ) from error

        elif self._ui is not None:
            self._ui.print_msg(
                f"Warning: Poe failed to locate envfile at {envfile_path_str!r}",
                verbosity=1,
            )

        self._cache[envfile_path_str] = result
        return result
