# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

# Source: https://click.palletsprojects.com/en/8.1.x/complex/

import importlib
from typing import Any, Dict, List, Optional

import asyncclick as click


class LazyGroup(click.Group):
    """
    A click Group that can lazily load subcommands.
    """

    def __init__(self, *args: Any, lazy_subcommands: Optional[Dict[str, str]] = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # lazy_subcommands is a map of the form:
        #
        #   {command-name} -> {module-name}.{command-object-name}
        #
        self.lazy_subcommands = lazy_subcommands or {}

    def list_commands(self, ctx: click.Context) -> List[str]:
        base = super().list_commands(ctx)
        lazy = sorted(self.lazy_subcommands.keys())
        return base + lazy

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        if cmd_name in self.lazy_subcommands:
            return self._lazy_load(cmd_name)
        return super().get_command(ctx, cmd_name)

    def _lazy_load(self, cmd_name: str) -> click.Command:
        # lazily loading a command, first get the module name and attribute name
        import_path = self.lazy_subcommands[cmd_name]
        modname, cmd_object_name = import_path.rsplit(".", 1)
        # do the import
        mod = importlib.import_module(modname)
        # get the Command object from that module
        cmd_object = getattr(mod, cmd_object_name)
        # check the result to make debugging easier
        if not isinstance(cmd_object, click.Command):
            print(f"{cmd_object} is of instance {type(cmd_object)}")
            raise ValueError(f"Lazy loading of {import_path} failed by returning " "a non-command object")
        return cmd_object
