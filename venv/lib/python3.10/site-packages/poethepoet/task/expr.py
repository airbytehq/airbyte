import re
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from ..exceptions import ExpressionParseError
from .base import PoeTask

if TYPE_CHECKING:
    from ..config import PoeConfig
    from ..context import RunContext
    from ..env.manager import EnvVarsManager


class ExprTask(PoeTask):
    """
    A task consisting of a python expression
    """

    content: str

    __key__ = "expr"
    __options__: Dict[str, Union[Type, Tuple[Type, ...]]] = {
        "imports": list,
        "assert": (bool, int),
        "use_exec": bool,
    }

    def _handle_run(
        self,
        context: "RunContext",
        extra_args: Sequence[str],
        env: "EnvVarsManager",
    ) -> int:
        from ..helpers.python import format_class

        named_arg_values = self.get_named_arg_values(env)
        env.update(named_arg_values)

        imports = self.options.get("imports", tuple())

        expr, env_values = self.parse_content(named_arg_values, env, imports)
        argv = [
            self.name,
            *(env.fill_template(token) for token in extra_args),
        ]

        script = [
            f"import sys;" f"sys.path.append('src');" f"sys.argv = {argv!r};",
            (f"import {', '.join(imports)}; " if imports else ""),
            f"{format_class(named_arg_values)}",
            f"{format_class(env_values, classname='__env')}",
            f"result = ({expr});",
            "print(result);",
        ]

        falsy_return_code = int(self.options.get("assert", False))
        if falsy_return_code:
            script.append(f"exit(0 if result else {falsy_return_code});")

        # Exactly which python executable to use is usually resolved by the executor
        # It's important that the script contains no line breaks to avoid issues on
        # windows
        cmd = ("python", "-c", "".join(script))

        self._print_action(self.content.strip(), context.dry)
        return self._get_executor(context, env).execute(
            cmd, use_exec=self.options.get("use_exec", False)
        )

    @classmethod
    def _validate_task_def(
        cls, task_name: str, task_def: Dict[str, Any], config: "PoeConfig"
    ) -> Optional[str]:
        try:
            cls._substitute_env_vars(task_def["expr"].strip(), {})
        except (ValueError, ExpressionParseError) as error:
            return f"Task {task_name!r} contains invalid expression: {error}"

        return None

    def parse_content(
        self,
        args: Optional[Dict[str, Any]],
        env: "EnvVarsManager",
        imports=Iterable[str],
    ) -> Tuple[str, Dict[str, str]]:
        """
        Returns the expression to evaluate and the subset of env vars that it references

        Templated referenced to env vars are resolve before parsing the expression.

        Will raise an exception if the content contains invalid syntax or references
        python variables that are not in scope.
        """

        from ..helpers.python import resolve_expression

        expression, accessed_vars = self._substitute_env_vars(
            self.content.strip(), env.to_dict()
        )

        expression = resolve_expression(
            source=expression,
            arguments=set(args or tuple()),
            call_only=False,
            allowed_vars={"sys", "__env", *imports},
        )
        # Strip out any new lines because they can be problematic on windows
        expression = re.sub(r"((\r\n|\r|\n) | (\r\n|\r|\n))", " ", expression)
        expression = re.sub(r"(\r\n|\r|\n)", " ", expression)

        return expression, accessed_vars

    @classmethod
    def _substitute_env_vars(cls, content: str, env: Mapping[str, str]):
        """
        Substitute ${template} references to env vars with a refernece to a python class
        attribute like __env.var, and collect the accessed env vars so we can construct
        that class with the required attributes later.
        """

        from ..env.template import SpyDict, apply_envvars_to_template

        # Spy on access to the env, so that instead of replacing template ${keys} with
        # the corresponding value, replace them with a python name and keep track of
        # referenced env vars.
        accessed_vars: Dict[str, str] = {}

        def getitem_spy(obj: SpyDict, key: str, value: str):
            accessed_vars[key] = value
            return f"__env.{key}"

        expression = apply_envvars_to_template(
            content=content,
            env=SpyDict(env, getitem_spy=getitem_spy),
            require_braces=True,
        )

        return expression, accessed_vars
