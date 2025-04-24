# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections import namedtuple
from typing import TYPE_CHECKING

from pylint.checkers import BaseChecker, DeprecatedMixin  # type: ignore

if TYPE_CHECKING:
    from typing import Set

    import astroid  # type: ignore
    from pylint.lint import PyLinter  # type: ignore

DeprecatedClass = namedtuple("DeprecatedClass", ["module", "name"])

DEPRECATED_CLASSES: Set[DeprecatedClass] = {
    DeprecatedClass("airbyte_cdk.logger", "AirbyteLogger"),
    DeprecatedClass(None, "GoogleAnalyticsDataApiBaseStream"),
}

DEPRECATED_MODULES = {"airbyte_cdk.sources.streams.http.auth"}

FORBIDDEN_METHOD_NAMES = {"get_updated_state"}


class ForbiddenMethodNameChecker(BaseChecker):
    name = "forbidden-method-name-checker"
    msgs = {
        "C9001": ('Method name "%s" is forbidden', "forbidden-method-name", "Used when a forbidden method name is detected."),
    }

    def visit_functiondef(self, node: astroid.node) -> None:
        if node.name in FORBIDDEN_METHOD_NAMES:
            self.add_message("forbidden-method-name", node=node, args=(node.name,))


class DeprecationChecker(DeprecatedMixin, BaseChecker):
    """Check for deprecated classes and modules.
    The DeprecatedMixin class is here:
    https://github.com/pylint-dev/pylint/blob/a5a77f6e891f6e143439d19b5e7f0a29eb5ea1cd/pylint/checkers/deprecated.py#L31
    """

    name = "deprecated"

    msgs = {
        **DeprecatedMixin.DEPRECATED_METHOD_MESSAGE,
        **DeprecatedMixin.DEPRECATED_ARGUMENT_MESSAGE,
        **DeprecatedMixin.DEPRECATED_CLASS_MESSAGE,
        **DeprecatedMixin.DEPRECATED_MODULE_MESSAGE,
    }

    def deprecated_modules(self) -> set[str]:
        """Callback method called by DeprecatedMixin for every module found in the code.

        Returns:
            collections.abc.Container of deprecated module names.
        """
        return DEPRECATED_MODULES

    def deprecated_classes(self, module: str) -> set[str]:
        """Callback method called by DeprecatedMixin for every class found in the code.

        Returns:
            collections.abc.Container of deprecated class names.
        """
        _deprecated_classes = set()
        for deprecated_class in DEPRECATED_CLASSES:
            if deprecated_class.module is None or deprecated_class.module == module:
                _deprecated_classes.add(deprecated_class.name)
        return _deprecated_classes


def register(linter: PyLinter) -> None:
    linter.register_checker(DeprecationChecker(linter))
    linter.register_checker(ForbiddenMethodNameChecker(linter))
