from typing import Optional


# ruff: noqa: N818
class PoeException(RuntimeError):
    cause: Optional[str]

    def __init__(self, msg, *args):
        self.msg = msg
        self.cause = args[0].args[0] if args else None
        self.args = (msg, *args)


class CyclicDependencyError(PoeException):
    pass


class ExpressionParseError(PoeException):
    pass


class ExecutionError(RuntimeError):
    cause: Optional[str]

    def __init__(self, msg, *args):
        self.msg = msg
        self.cause = args[0].args[0] if args else None
        self.args = (msg, *args)


class PoePluginException(PoeException):
    pass
