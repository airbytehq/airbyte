"""
This module core a framework for defining heirarchical parser and ASTs.
See sibling ast module for an example usage.
"""

from abc import ABC, abstractmethod
from typing import (
    IO,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
)


class ParseCursor:
    """
    This makes it easier to parse a text by wrapping it an abstraction like a stack,
    so the parser can pop off the next character but also push back characters that need
    to be reprocessed.

    TODO: keep track of the current line number and position of the read head.
    """

    _line: int
    _position: int
    _source: Iterator[str]
    _pushback_stack: List[str]

    def __init__(self, source: Iterator[str]):
        self._source = source
        self._line = 0
        self._position = 0
        self._pushback_stack = []

    @classmethod
    def from_file(cls, file: IO[str]):
        def iter_chars():
            while char := file.read(1):
                yield char

        return cls(iter_chars())

    @classmethod
    def from_string(cls, string: str):
        return cls(char for char in string)

    def peek(self):
        if not self._pushback_stack:
            try:
                self._pushback_stack.append(next(self._source))
            except StopIteration:
                return None
        return self._pushback_stack[-1]

    def take(self):
        # TODO: update _line and _position
        if self._pushback_stack:
            return self._pushback_stack.pop()

        try:
            return next(self._source)
        except StopIteration:
            return None

    def pushback(self, *items: str):
        for item in reversed(items):
            # TODO: rewind _line and _position
            # HOW to get length of previous line which pushback a line break?
            #   would need to keep a stack of all previous line lengths to be sure!?
            self._pushback_stack.append(item)

    def __iter__(self):
        return self

    def __next__(self):
        if char := self.take():
            return char
        raise StopIteration

    def __bool__(self):
        return bool(self.peek())


class ParseConfig:
    substitute_nodes: Dict[Type["AstNode"], Type["AstNode"]]
    line_seperators: str

    def __init__(
        self,
        substitute_nodes: Optional[Dict[Type["AstNode"], Type["AstNode"]]] = None,
        line_seperators="",
    ):
        self.substitute_nodes = substitute_nodes or {}
        self.line_seperators = line_seperators

    def resolve_node_cls(self, klass: Type["AstNode"]) -> Type["AstNode"]:
        return self.substitute_nodes.get(klass, klass)


class AstNode(ABC):
    _cancelled: bool = False

    def __init__(self, chars: ParseCursor, config: ParseConfig = ParseConfig()):
        self.config = config
        self._parse(chars)

    @abstractmethod
    def _parse(self, chars: ParseCursor):
        ...

    @abstractmethod
    def pretty(self, indent: int = 0, increment: int = 4):
        ...

    def __bool__(self):
        return not self._cancelled

    @abstractmethod
    def __len__(self):
        ...


T = TypeVar("T")


class SyntaxNode(AstNode, Generic[T]):
    _children: List[T]

    def get_child_node_cls(self, node_type: Type[AstNode]) -> Type[T]:
        """
        Apply Node class substitution for the given node AstNode if specified in
        the ParseConfig.
        """
        return cast(Type[T], self.config.resolve_node_cls(node_type))

    @property
    def children(self) -> Tuple["SyntaxNode", ...]:
        return tuple(getattr(self, "_children", tuple()))

    def pretty(self, indent: int = 0, increment: int = 4):
        indent += increment
        return "\n".join(
            [
                f"{self.__class__.__name__}:",
                *(" " * indent + child.pretty(indent) for child in self),
            ]
        )

    def __getitem__(self, index: int):
        return self._children[index]

    def __iter__(self):
        return iter(self._children)

    def __len__(self):
        return len(self._children)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({', '.join(repr(c) for c in self._children)})"
        )

    def __eq__(self, other):
        if isinstance(other, tuple):
            return self.children == other
        return super().__eq__(other)


class ContentNode(AstNode):
    _content: str = ""

    @property
    def content(self) -> str:
        return self._content

    def pretty(self, indent: int = 0, increment: int = 4):
        return f"{self.__class__.__name__}: {self._content!r}"

    def __str__(self):
        return self._content

    def __len__(self):
        return len(self._content)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._content!r})"

    def __eq__(self, other):
        if isinstance(other, str):
            return self._content == other
        return super().__eq__(other)


class ParseError(RuntimeError):
    pass
