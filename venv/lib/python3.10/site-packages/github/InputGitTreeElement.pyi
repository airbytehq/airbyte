from typing import Dict, Union

from github.GithubObject import _NotSetType

class InputGitTreeElement:
    def __init__(
        self,
        path: str,
        mode: str,
        type: str,
        content: Union[str, _NotSetType] = ...,
        sha: Union[str, _NotSetType, None] = ...,
    ) -> None: ...
    @property
    def _identity(self) -> Dict[str, str]: ...
