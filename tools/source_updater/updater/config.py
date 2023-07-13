from typing import Any, Dict


class Config:
    def __init__(self, name: str, content: Dict[str, Any]):
        self._name = name
        self._content = content

    @property
    def name(self) -> str:
        return self._name

    @property
    def content(self) -> Dict[str, Any]:
        return self._content

