from __future__ import annotations

from fnmatch import fnmatch
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from click import Context, Parameter

from rich_click._click_types_cache import Argument, Command, Group
from rich_click.rich_help_configuration import ColumnType, CommandColumnType, OptionColumnType
from rich_click.rich_parameter import RichArgument, RichParameter
from rich_click.utils import CommandGroupDict, OptionGroupDict


if TYPE_CHECKING:
    from rich.box import Box
    from rich.panel import Panel
    from rich.style import StyleType
    from rich.table import Table

    from rich_click.rich_command import RichCommand
    from rich_click.rich_context import RichContext
    from rich_click.rich_help_formatter import RichHelpFormatter


ColT = TypeVar("ColT", bound=ColumnType)
CT = TypeVar("CT", Command, Parameter)
GroupType = TypeVar("GroupType", OptionGroupDict, CommandGroupDict)


class RichPanel(Generic[CT, ColT]):
    """RichPanel base class."""

    panel_class: Optional[Type["Panel"]] = None
    table_class: Optional[Type["Table"]] = None
    _highlight: ClassVar[bool] = False
    _object_attr: ClassVar[str] = NotImplemented

    def __init__(
        self,
        name: str,
        *,
        help: Optional[str] = None,
        help_style: Optional["StyleType"] = None,
        table_styles: Optional[Dict[str, Any]] = None,
        panel_styles: Optional[Dict[str, Any]] = None,
        column_types: Optional[List[ColT]] = None,
        inline_help_in_title: Optional[bool] = None,
        title_style: Optional["StyleType"] = None,
    ) -> None:
        """Initialize a RichPanel."""
        self.name = name
        self.help = help
        self.help_style = help_style
        self.table_styles = table_styles or {}
        self.panel_styles = panel_styles or {}
        self.column_types = column_types
        self.inline_help_in_title = inline_help_in_title
        self.title_style = title_style

    @property
    def objects(self) -> List[str]:
        if self._object_attr is NotImplemented:
            raise NotImplementedError()
        return getattr(self, self._object_attr)  # type: ignore[no-any-return]

    def add_object(self, o: str) -> None:
        if self._object_attr is NotImplemented:
            raise NotImplementedError()
        getattr(self, self._object_attr).append(o)

    def get_box(self, box: Optional[Union[str, "Box"]]) -> Optional["Box"]:
        if box is None:
            return None
        from rich_click.rich_box import get_box

        return get_box(box)

    def to_info_dict(self, ctx: Context) -> Dict[str, Any]:
        if self._object_attr is NotImplemented:
            raise NotImplementedError()
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "help": self.help,
            self._object_attr: [i.name for i in self.get_objects(ctx.command, ctx)],
        }

    @classmethod
    def list_all_objects(cls, ctx: Context) -> List[Tuple[str, CT]]:
        """List all objects of the command that this panel type works with."""
        raise NotImplementedError()

    def get_objects(self, command: Command, ctx: Context) -> Generator[CT, None, None]:
        """List the proper names assigned to the panel."""
        raise NotImplementedError()

    def _get_base_table(self, **defaults: Any) -> "Table":
        if self.table_class is None:
            from rich.table import Table

            self.table_class = Table

        kw: Dict[str, Any] = {
            "highlight": self._highlight,
            "show_header": False,
        }

        kw.update(defaults)
        kw.update(self.table_styles)
        if "box" in kw and kw["box"] is not None:
            kw["box"] = self.get_box(kw.pop("box", None))
        return self.table_class(**kw)

    def get_table(
        self,
        command: "RichCommand",
        ctx: "RichContext",
        formatter: "RichHelpFormatter",
    ) -> "Table":
        raise NotImplementedError()

    def _get_base_panel(self, table: "Table", **defaults: Any) -> "Panel":

        if self.panel_class is None:
            from rich_click.rich_help_rendering import RichClickRichPanel

            self.panel_class = RichClickRichPanel
        kw = defaults
        kw.update(self.panel_styles)
        if "box" in kw:
            if kw["box"] is None:
                kw.pop("box")
                kw["box"] = self.get_box("SIMPLE")
            else:
                kw["box"] = self.get_box(kw.pop("box", None))

        return self.panel_class(table, **kw)

    def render(
        self,
        command: "RichCommand",
        ctx: "RichContext",
        formatter: "RichHelpFormatter",
    ) -> "Panel":
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"


class RichOptionPanel(RichPanel[Parameter, OptionColumnType]):
    """Panel for parameters."""

    _highlight: ClassVar[bool] = True
    _object_attr: ClassVar[str] = "options"

    def __init__(
        self,
        name: str,
        options: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a RichOptionPanel."""
        super().__init__(name, **kwargs)
        self.options = options or []

    @classmethod
    def list_all_objects(cls, ctx: Context) -> List[Tuple[str, Parameter]]:
        return [
            (i.opts[0] if getattr(i, "flag_value", None) and i.opts else i.name, i)  # type: ignore[misc]
            for i in ctx.command.get_params(ctx)
        ]

    def get_objects(self, command: Command, ctx: Context) -> Generator[Parameter, None, None]:
        """List the objects assigned to the panel."""
        for opt in self.options:
            # Get the param
            for param in command.get_params(ctx):
                if any([opt in [*param.opts, param.name]]):
                    break
            # Skip if option is not listed in this group
            else:
                continue
            yield param

    def get_table(
        self,
        command: "RichCommand",
        ctx: "RichContext",
        formatter: "RichHelpFormatter",
    ) -> "Table":
        t_styles = {
            "show_lines": formatter.config.style_options_table_show_lines,
            "leading": formatter.config.style_options_table_leading,
            "box": formatter.config.style_options_table_box,
            "border_style": formatter.config.style_options_table_border_style,
            "row_styles": formatter.config.style_options_table_row_styles,
            "pad_edge": formatter.config.style_options_table_pad_edge,
            "padding": formatter.config.style_options_table_padding,
            "expand": formatter.config.style_options_table_expand,
        }
        table = self._get_base_table(**t_styles)
        rows = []
        for param in self.get_objects(command, ctx):
            from rich_click.rich_help_rendering import get_parameter_rich_table_row

            cols = (
                param.get_rich_table_row(ctx, formatter, self)
                if isinstance(param, RichParameter)
                else get_parameter_rich_table_row(param, ctx, formatter, self)  # type: ignore[arg-type]
            )

            rows.append(cols)

        headers = [i.replace("_", " ").title() for i in formatter.config.options_table_column_types]

        filtered = [(h, c) for h, c in zip(headers, zip(*rows)) if any(cell for cell in c)]
        headers, rows = zip(*filtered) if filtered else ([], [])
        rows = list(map(list, zip(*rows))) if rows else []

        for row in rows:
            table.add_row(*row)

        for col, header in zip(table.columns, headers):
            col.header = header

        return table

    def render(
        self,
        command: "RichCommand",
        ctx: "RichContext",
        formatter: "RichHelpFormatter",
    ) -> "Panel":
        from rich.text import Text

        from rich_click.rich_help_rendering import RichClickRichPanel

        inner: Any = self.get_table(command, ctx, formatter)

        p_styles: Dict[str, Any] = {
            "border_style": formatter.config.style_options_panel_border,
            "title_align": formatter.config.align_options_panel,
            "box": formatter.config.style_options_panel_box,
            "padding": formatter.config.style_options_panel_padding,
            "style": formatter.config.style_options_panel_style,
        }
        if self.panel_class is None or issubclass(self.panel_class, RichClickRichPanel):
            p_styles["title_padding"] = formatter.config.panel_title_padding

        if self.title_style is None:
            title_style = formatter.config.style_options_panel_title_style
        else:
            title_style = self.title_style

        title = formatter.config.panel_title_string.format(self.name)

        if self.help:
            if self.help_style is None:
                help_style = formatter.config.style_options_panel_help_style
            else:
                help_style = self.help_style
            if self.inline_help_in_title is None:
                inline_help_in_title = formatter.config.panel_inline_help_in_title
            else:
                inline_help_in_title = self.inline_help_in_title

            if inline_help_in_title:

                p_styles["title"] = Text("", overflow="ellipsis").join(
                    [
                        Text(title, style=title_style),
                        Text(formatter.config.panel_inline_help_delimiter),
                        Text(self.help, style=help_style),
                    ]
                )
            else:
                p_styles["title"] = Text(title, style=title_style)
                from rich.containers import Renderables

                inner = Renderables([formatter.rich_text(self.help, style=help_style), inner])
        else:
            p_styles["title"] = Text(title, style=title_style)
        panel = self._get_base_panel(inner, **p_styles)
        return panel


class RichCommandPanel(RichPanel[Command, CommandColumnType]):
    """Panel for parameters."""

    _object_attr: ClassVar[str] = "commands"

    def __init__(
        self,
        name: str,
        commands: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a RichCommandPanel."""
        super().__init__(name, **kwargs)
        self.commands = commands or []

    @classmethod
    def list_all_objects(cls, ctx: Context) -> List[Tuple[str, Command]]:
        if not isinstance(ctx.command, Group):
            return []
        commands = []
        for cmd_name in ctx.command.list_commands(ctx):
            cmd = ctx.command.get_command(ctx, cmd_name)
            if cmd is not None:
                commands.append((cmd_name, cmd))
        return commands

    def get_objects(self, command: Command, ctx: Context) -> Generator[Command, None, None]:
        """List the objects assigned to the panel."""
        if not isinstance(command, Group):
            return

        commands_list = command.list_commands(ctx)
        callback_names = {c.callback.__name__: c for c in command.commands.values() if c.callback is not None}

        for cmd_name in self.commands:

            if cmd_name in commands_list:
                yield command.get_command(ctx, cmd_name)  # type: ignore[misc]
            elif cmd_name in callback_names:
                yield callback_names[cmd_name]
            else:
                continue

    def get_table(
        self,
        command: "RichCommand",
        ctx: "RichContext",
        formatter: "RichHelpFormatter",
    ) -> "Table":
        t_styles = {
            "show_lines": formatter.config.style_commands_table_show_lines,
            "leading": formatter.config.style_commands_table_leading,
            "box": formatter.config.style_commands_table_box,
            "border_style": formatter.config.style_commands_table_border_style,
            "row_styles": formatter.config.style_commands_table_row_styles,
            "pad_edge": formatter.config.style_commands_table_pad_edge,
            "padding": formatter.config.style_commands_table_padding,
            "expand": formatter.config.style_commands_table_expand,
        }
        table = self._get_base_table(**t_styles)

        # Define formatting in first column, as commands don't match highlighter regex
        # and set column ratio for first and second column, if a ratio has been set
        if formatter.config.style_commands_table_column_width_ratio is None:
            table_column_width_ratio: Union[Tuple[None, None], Tuple[int, int]] = (None, None)
        else:
            table_column_width_ratio = formatter.config.style_commands_table_column_width_ratio

        # TODO
        # columns = self.columns or formatter.config.commands_table_column_types

        table.add_column(style=formatter.config.style_command, no_wrap=True, ratio=table_column_width_ratio[0])
        table.add_column(
            no_wrap=False,
            ratio=table_column_width_ratio[1],
        )

        if not isinstance(command, Group):
            return table

        rows = []

        for cmd in self.get_objects(command, ctx):

            from rich_click.rich_command import RichCommand
            from rich_click.rich_help_rendering import get_command_rich_table_row

            cols = (
                cmd.get_rich_table_row(ctx, formatter, self)
                if isinstance(cmd, RichCommand)
                else get_command_rich_table_row(cmd, ctx, formatter, self)
            )

            rows.append(cols)

        headers = [i.replace("_", " ").title() for i in formatter.config.commands_table_column_types]

        filtered = [(h, c) for h, c in zip(headers, zip(*rows)) if any(cell for cell in c)]
        headers, rows = zip(*filtered) if filtered else ([], [])
        rows = list(map(list, zip(*rows))) if rows else []

        for row in rows:
            table.add_row(*row)

        for col, header in zip(table.columns, headers):
            col.header = header

        return table

    def render(
        self,
        command: "RichCommand",
        ctx: "RichContext",
        formatter: "RichHelpFormatter",
    ) -> "Panel":
        from rich.text import Text

        from rich_click.rich_help_rendering import RichClickRichPanel

        inner: Any = self.get_table(command, ctx, formatter)

        p_styles: Dict[str, Any] = {
            "border_style": formatter.config.style_commands_panel_border,
            "title_align": formatter.config.align_commands_panel,
            "box": formatter.config.style_commands_panel_box,
            "padding": formatter.config.style_commands_panel_padding,
            "style": formatter.config.style_commands_panel_style,
        }
        if self.panel_class is None or issubclass(self.panel_class, RichClickRichPanel):
            p_styles["title_padding"] = formatter.config.panel_title_padding

        if self.title_style is None:
            title_style = formatter.config.style_commands_panel_title_style
        else:
            title_style = self.title_style

        title = formatter.config.panel_title_string.format(self.name)

        if self.help:
            if self.help_style is None:
                help_style = formatter.config.style_commands_panel_help_style
            else:
                help_style = self.help_style
            if self.inline_help_in_title is None:
                inline_help_in_title = formatter.config.panel_inline_help_in_title
            else:
                inline_help_in_title = self.inline_help_in_title

            if inline_help_in_title:

                p_styles["title"] = Text("", overflow="ellipsis").join(
                    [
                        Text(title, style=title_style),
                        Text(formatter.config.panel_inline_help_delimiter),
                        Text(self.help, style=help_style),
                    ]
                )
            else:
                p_styles["title"] = Text(title, style=title_style)
                from rich.containers import Renderables

                inner = Renderables([formatter.rich_text(self.help, style=help_style), inner])
        else:
            p_styles["title"] = Text(title, style=title_style)

        panel = self._get_base_panel(inner, **p_styles)
        return panel


# Using config to define panels is silently deprecated.
# We do not intend on removing this for a very long time, possibly ever.


def _resolve_panels_from_config(
    ctx: "RichContext",
    formatter: "RichHelpFormatter",
    groups: Dict[str, List[GroupType]],
    panel_cls: Type[RichPanel[CT, ColT]],
) -> List[RichPanel[CT, ColT]]:
    """Logic for resolving the groups."""
    # Step 1: get valid name(s) for the command currently being executed
    assert panel_cls._object_attr is not NotImplemented, "RichPanel must have a defined _object_attr"

    cmd_name = ctx.command.name
    _ctx: "RichContext" = ctx
    while _ctx.parent is not None:
        _ctx = _ctx.parent  # type: ignore[assignment]
        cmd_name = f"{_ctx.command.name} {cmd_name}"
    # 'command_path' is sometimes the file name, e.g. hello.py.
    # We also want to make sure that the actual command name is supported as well.
    if cmd_name != ctx.command_path:
        paths = [cmd_name, ctx.command_path]
    else:
        paths = [cmd_name]
    # Also handle 'python -m foo' when the user specifies a key of 'foo':
    if ctx.command_path.startswith("python -m "):
        extra = ctx.command_path.replace("python -m ", "", 1)
        paths.append(extra)
    final_groups_list: List[GroupType] = []

    # Step 2: Match currently executing command to keys
    # Assign wildcards, but make sure we do not overwrite anything already defined.
    for mtch in reversed(sorted([_ for _ in groups if any(fnmatch(_path, _) for _path in paths)])):
        wildcard_option_groups = groups[mtch]
        for grp in wildcard_option_groups:
            grp = grp.copy()
            opts: List[str] = grp.get(panel_cls._object_attr, [])  # type: ignore[assignment]
            traversed = []
            for opt in grp.get(panel_cls._object_attr, []):  # type: ignore[attr-defined]

                if grp.get("deduplicate", True) and opt in [
                    _opt
                    for _grp in final_groups_list
                    for _opt in _grp.get(panel_cls._object_attr, [])  # type: ignore[attr-defined]
                ]:
                    opts.remove(opt)
                traversed.append(opt)
            grp[panel_cls._object_attr] = opts  # type: ignore[literal-required]
            grp.pop("deduplicate", None)
            final_groups_list.append(grp)

    return [panel_cls(**grp) for grp in final_groups_list]  # type: ignore[misc,arg-type]


def construct_panels(
    command: "RichCommand",
    ctx: "RichContext",
    formatter: "RichHelpFormatter",
) -> List[RichPanel[Any, Any]]:
    """Construct panels from the command as well as from the old groups config."""
    _show_arguments = formatter.config.show_arguments

    # If only an options or a commands panel is defined,
    # then we respect intra-type sort order but not inter-type sort order.
    defined_commands = False
    defined_options = False
    # Handling ordering is tricky with the "groups" feature.
    # it's safest to flag and treat specially.
    using_groups_feat = False

    # Start with list of panels already defined.
    defined_panels: Dict[Tuple[str, str], RichPanel[Any, Any]] = {}

    for p in command.panels:
        defined_panels[(p._object_attr, p.name)] = p
        if p._object_attr == "options":
            defined_options = True
        elif p._object_attr == "commands":
            defined_commands = True

    if formatter.config.option_groups:
        option_groups_from_config = _resolve_panels_from_config(
            ctx, formatter, formatter.config.option_groups, formatter.option_panel_class
        )
        if option_groups_from_config:
            defined_panels.update({(p._object_attr, p.name): p for p in option_groups_from_config})
            using_groups_feat = True

    if isinstance(command, Group):
        if formatter.config.command_groups:
            command_groups_from_config = _resolve_panels_from_config(
                ctx, formatter, formatter.config.command_groups, formatter.command_panel_class
            )
            if command_groups_from_config:
                defined_panels.update({(p._object_attr, p.name): p for p in command_groups_from_config})
                using_groups_feat = True

    # Separate out default panels because we need to sort them properly later.
    # We will reversed() through this so order is flipped.
    # Also-- we have to decouple name from obj because commands can have different names
    # than their mappings to a Group.
    new_panels: Dict[Tuple[str, str], List[str]] = {}
    pre_default_panels: Dict[Tuple[str, str], List[str]] = {}
    post_default_panels: Dict[Tuple[str, str], List[str]]
    if isinstance(command, Group):
        if formatter.config.commands_before_options:
            if defined_commands != defined_options or using_groups_feat:
                pre_default_panels = {
                    ("commands", formatter.config.commands_panel_title): [],
                }
                post_default_panels = {
                    ("options", formatter.config.arguments_panel_title): [],
                    ("options", formatter.config.options_panel_title): [],
                }
            else:
                post_default_panels = {
                    ("commands", formatter.config.commands_panel_title): [],
                    ("options", formatter.config.arguments_panel_title): [],
                    ("options", formatter.config.options_panel_title): [],
                }
        else:
            if defined_commands != defined_options or using_groups_feat:
                pre_default_panels = {
                    ("options", formatter.config.arguments_panel_title): [],
                    ("options", formatter.config.options_panel_title): [],
                }
                post_default_panels = {
                    ("commands", formatter.config.commands_panel_title): [],
                }
            else:
                post_default_panels = {
                    ("options", formatter.config.arguments_panel_title): [],
                    ("options", formatter.config.options_panel_title): [],
                    ("commands", formatter.config.commands_panel_title): [],
                }
    else:
        post_default_panels = {
            ("options", formatter.config.arguments_panel_title): [],
            ("options", formatter.config.options_panel_title): [],
        }

    if ("commands", formatter.config.commands_panel_title) in defined_panels:
        pre_default_panels.pop(("commands", formatter.config.commands_panel_title), None)
        post_default_panels.pop(("commands", formatter.config.commands_panel_title), None)

    if ("options", formatter.config.options_panel_title) in defined_panels:
        pre_default_panels.pop(("options", formatter.config.options_panel_title), None)
        post_default_panels.pop(("options", formatter.config.options_panel_title), None)

    if ("options", formatter.config.arguments_panel_title) in defined_panels:
        pre_default_panels.pop(("options", formatter.config.arguments_panel_title), None)
        post_default_panels.pop(("options", formatter.config.arguments_panel_title), None)

    # Go through objects to see whether they are assigned.
    # Need to do tuples because commands and options can have same name.
    assigned_objects: Dict[Tuple[str, str], Set[str]] = {}
    for p in defined_panels.values():
        for o in p.objects:
            assigned_objects.setdefault((p._object_attr, o), set())
            assigned_objects[(p._object_attr, o)].add(p.name)

    if ("options", formatter.config.arguments_panel_title) in defined_panels:
        _show_arguments = True

    objs: List[Tuple[str, str, Union[Parameter, Command]]] = [
        ("options", name, o) for name, o in formatter.option_panel_class.list_all_objects(ctx)
    ]
    if isinstance(command, Group):
        objs.extend([("commands", name, o) for name, o in formatter.command_panel_class.list_all_objects(ctx)])

    from rich_click.rich_command import RichGroup

    # Here we are interested in:
    # 1. assigning objs based on panel=...
    # 2. getting unassigned objs
    for typ, name, obj in objs:
        if TYPE_CHECKING:
            assert isinstance(obj.name, str)
        if getattr(obj, "hidden", False):
            continue
        names = {name, obj.name}
        if isinstance(obj, Parameter):
            names.update(obj.opts)
        elif isinstance(obj, Command) and obj.callback is not None:
            names.add(obj.callback.__name__)
        assigned_to = set()
        for n in names:
            _assigned_panels = assigned_objects.get((typ, n), set())
            for ap in _assigned_panels:
                assigned_to.add((typ, ap))
        assigned = bool(assigned_to)
        inferred = False
        panel_list: List[str] = []
        if hasattr(obj, "panel"):
            if isinstance(obj.panel, str):
                panel_list = [obj.panel]
            elif obj.panel is None:
                if assigned:
                    continue
            else:
                panel_list = obj.panel
        elif typ == "commands" and isinstance(command, RichGroup):
            _p = command._panel_command_mapping.get(name)
            if _p:
                panel_list.extend(_p)
        if not panel_list:
            inferred = True
            if typ == "options":
                if not formatter.config.group_arguments_options and isinstance(obj, Argument):
                    if _show_arguments is not False:
                        panel_list = [formatter.config.arguments_panel_title]
                    else:
                        panel_list = []
                else:
                    panel_list = [formatter.config.options_panel_title]
            elif typ == "commands":
                panel_list = [formatter.config.commands_panel_title]
            else:
                panel_list = []
        for panel_name in panel_list:
            # Ensure we don't reassign if already assigned.
            if (typ, panel_name) not in assigned_to:
                if (typ, panel_name) in defined_panels:
                    defined_panels[(typ, panel_name)].add_object(name)
                elif assigned:
                    pass
                elif (typ, panel_name) in pre_default_panels:
                    pre_default_panels[(typ, panel_name)].append(name)
                elif (typ, panel_name) in post_default_panels:
                    post_default_panels[(typ, panel_name)].append(name)
                else:
                    new_panels.setdefault((typ, panel_name), []).append(name)
            if (
                _show_arguments is None
                and panel_name == formatter.config.arguments_panel_title
                and isinstance(obj, RichArgument)
                and (not inferred or obj.help is not None)
            ):
                _show_arguments = True

    if not _show_arguments:
        pre_default_panels.pop(("options", formatter.config.arguments_panel_title), None)
        post_default_panels.pop(("options", formatter.config.arguments_panel_title), None)

    final_panels: List[RichPanel[Any, Any]] = []

    all_panel_mappings: List[Union[Dict[Tuple[str, str], List[str]], Dict[Tuple[str, str], RichPanel[Any, Any]]]] = [
        pre_default_panels,
        defined_panels,
        new_panels,
        post_default_panels,
    ]
    for d in all_panel_mappings:
        for (typ, panel_name), obj_list in d.items():
            cls: Type[RichPanel[Any, Any]]
            if typ == "options":
                cls = formatter.option_panel_class
            elif typ == "commands":
                cls = formatter.command_panel_class
            else:
                continue
            panel: RichPanel[Any, Any]
            if isinstance(obj_list, RichPanel):
                panel = obj_list
            elif (typ, panel_name) not in defined_panels:
                panel = cls(panel_name)
                setattr(panel, panel._object_attr, [i for i in obj_list])
            else:
                panel = defined_panels[(typ, panel_name)]
                for _obj in obj_list:
                    panel.add_object(_obj)
            final_panels.append(panel)

    return final_panels
