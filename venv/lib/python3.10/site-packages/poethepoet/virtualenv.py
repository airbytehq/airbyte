import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Mapping


class Virtualenv:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self._is_windows = sys.platform == "win32"

    def exists(self) -> bool:
        """
        Check if the configured path points to a directory
        """
        return self.path.is_dir()

    def bin_dir(self) -> Path:
        """
        Path to where the directory for installed executables should be
        """
        if self._is_windows:
            return self.path.joinpath("Scripts")
        return self.path.joinpath("bin")

    def resolve_executable(self, executable: str) -> str:
        """
        If the given executable can be found in the bin_dir then return its absolute
        path. Otherwise return the input.
        """
        bin_dir = self.bin_dir()
        if bin_dir.joinpath(executable).is_file():
            return str(bin_dir.joinpath(executable))
        if self._is_windows:
            if bin_dir.joinpath(f"{executable}.com").is_file():
                return str(bin_dir.joinpath(f"{executable}.com"))
            if bin_dir.joinpath(f"{executable}.exe").is_file():
                return str(bin_dir.joinpath(f"{executable}.exe"))
            if bin_dir.joinpath(f"{executable}.bat").is_file():
                return str(bin_dir.joinpath(f"{executable}.bat"))
            return shutil.which(executable) or executable
        return executable

    @staticmethod
    def detect(parent_dir: Path) -> bool:
        """
        Check whether there seems to be a valid virtualenv within the given directory at
        either ./venv, or ./.venv
        """
        return (
            Virtualenv(parent_dir.joinpath("venv")).valid()
            or Virtualenv(parent_dir.joinpath(".venv")).valid()
        )

    def valid(self) -> bool:
        """
        Check that the path points to a dir that really is a virtualenv with reasonable
        certainty
        """
        if not self.path:
            return False
        bin_dir = self.bin_dir()
        if self._is_windows:
            return (
                bin_dir.joinpath("activate").is_file()
                and bin_dir.joinpath("python.exe").is_file()
                and self.path.joinpath("Lib", "site-packages").is_dir()
            )
        return (
            bin_dir.joinpath("activate").is_file()
            and bin_dir.joinpath("python").is_file()
            and bool(
                next(
                    self.path.glob(
                        os.path.sep.join(("lib", "python3*", "site-packages"))
                    ),
                    False,
                )
            )
        )

    def get_env_vars(self, base_env: Mapping[str, str]) -> Dict[str, str]:
        bin_dir = str(self.bin_dir())
        # Revert path update from existing virtualenv if applicable
        path_var = os.environ.get("_OLD_VIRTUAL_PATH", "") or os.environ.get("PATH", "")
        old_path_var = path_var

        if not path_var.startswith(bin_dir):
            path_delim = ";" if self._is_windows else ":"
            path_var = bin_dir + path_delim + path_var

        result = dict(
            base_env,
            VIRTUAL_ENV=str(self.path),
            _OLD_VIRTUAL_PATH=old_path_var,
            PATH=path_var,
        )

        if "PYTHONHOME" in result:
            result["_OLD_VIRTUAL_PYTHONHOME"] = result["PYTHONHOME"]
            result.pop("PYTHONHOME")

        return result
