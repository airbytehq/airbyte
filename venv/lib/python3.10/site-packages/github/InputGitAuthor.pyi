from typing import Dict, Union

from github.GithubObject import _NotSetType

class InputGitAuthor:
    def __init__(
        self, name: str, email: str, date: Union[str, _NotSetType] = ...
    ) -> None: ...
    @property
    def _identity(self) -> Dict[str, str]: ...
