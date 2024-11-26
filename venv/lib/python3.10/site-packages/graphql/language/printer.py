from typing import Any, Collection, Optional

from ..language.ast import Node, OperationType
from .block_string import print_block_string
from .print_string import print_string
from .visitor import visit, Visitor

__all__ = ["print_ast"]


MAX_LINE_LENGTH = 80

Strings = Collection[str]


class PrintedNode:
    """A union type for all nodes that have been processed by the printer."""

    alias: str
    arguments: Strings
    block: bool
    default_value: str
    definitions: Strings
    description: str
    directives: str
    fields: Strings
    interfaces: Strings
    locations: Strings
    name: str
    operation: OperationType
    operation_types: Strings
    repeatable: bool
    selection_set: str
    selections: Strings
    type: str
    type_condition: str
    types: Strings
    value: str
    values: Strings
    variable: str
    variable_definitions: Strings


def print_ast(ast: Node) -> str:
    """Convert an AST into a string.

    The conversion is done using a set of reasonable formatting rules.
    """
    return visit(ast, PrintAstVisitor())


class PrintAstVisitor(Visitor):
    @staticmethod
    def leave_name(node: PrintedNode, *_args: Any) -> str:
        return node.value

    @staticmethod
    def leave_variable(node: PrintedNode, *_args: Any) -> str:
        return f"${node.name}"

    # Document

    @staticmethod
    def leave_document(node: PrintedNode, *_args: Any) -> str:
        return join(node.definitions, "\n\n")

    @staticmethod
    def leave_operation_definition(node: PrintedNode, *_args: Any) -> str:
        var_defs = wrap("(", join(node.variable_definitions, ", "), ")")
        prefix = join(
            (
                node.operation.value,
                join((node.name, var_defs)),
                join(node.directives, " "),
            ),
            " ",
        )
        # Anonymous queries with no directives or variable definitions can use the
        # query short form.
        return ("" if prefix == "query" else prefix + " ") + node.selection_set

    @staticmethod
    def leave_variable_definition(node: PrintedNode, *_args: Any) -> str:
        return (
            f"{node.variable}: {node.type}"
            f"{wrap(' = ', node.default_value)}"
            f"{wrap(' ', join(node.directives, ' '))}"
        )

    @staticmethod
    def leave_selection_set(node: PrintedNode, *_args: Any) -> str:
        return block(node.selections)

    @staticmethod
    def leave_field(node: PrintedNode, *_args: Any) -> str:
        prefix = wrap("", node.alias, ": ") + node.name
        args_line = prefix + wrap("(", join(node.arguments, ", "), ")")

        if len(args_line) > MAX_LINE_LENGTH:
            args_line = prefix + wrap("(\n", indent(join(node.arguments, "\n")), "\n)")

        return join((args_line, join(node.directives, " "), node.selection_set), " ")

    @staticmethod
    def leave_argument(node: PrintedNode, *_args: Any) -> str:
        return f"{node.name}: {node.value}"

    # Fragments

    @staticmethod
    def leave_fragment_spread(node: PrintedNode, *_args: Any) -> str:
        return f"...{node.name}{wrap(' ', join(node.directives, ' '))}"

    @staticmethod
    def leave_inline_fragment(node: PrintedNode, *_args: Any) -> str:
        return join(
            (
                "...",
                wrap("on ", node.type_condition),
                join(node.directives, " "),
                node.selection_set,
            ),
            " ",
        )

    @staticmethod
    def leave_fragment_definition(node: PrintedNode, *_args: Any) -> str:
        # Note: fragment variable definitions are deprecated and will be removed in v3.3
        return (
            f"fragment {node.name}"
            f"{wrap('(', join(node.variable_definitions, ', '), ')')}"
            f" on {node.type_condition}"
            f" {wrap('', join(node.directives, ' '), ' ')}"
            f"{node.selection_set}"
        )

    # Value

    @staticmethod
    def leave_int_value(node: PrintedNode, *_args: Any) -> str:
        return node.value

    @staticmethod
    def leave_float_value(node: PrintedNode, *_args: Any) -> str:
        return node.value

    @staticmethod
    def leave_string_value(node: PrintedNode, *_args: Any) -> str:
        if node.block:
            return print_block_string(node.value)
        return print_string(node.value)

    @staticmethod
    def leave_boolean_value(node: PrintedNode, *_args: Any) -> str:
        return "true" if node.value else "false"

    @staticmethod
    def leave_null_value(_node: PrintedNode, *_args: Any) -> str:
        return "null"

    @staticmethod
    def leave_enum_value(node: PrintedNode, *_args: Any) -> str:
        return node.value

    @staticmethod
    def leave_list_value(node: PrintedNode, *_args: Any) -> str:
        return f"[{join(node.values, ', ')}]"

    @staticmethod
    def leave_object_value(node: PrintedNode, *_args: Any) -> str:
        return f"{{{join(node.fields, ', ')}}}"

    @staticmethod
    def leave_object_field(node: PrintedNode, *_args: Any) -> str:
        return f"{node.name}: {node.value}"

    # Directive

    @staticmethod
    def leave_directive(node: PrintedNode, *_args: Any) -> str:
        return f"@{node.name}{wrap('(', join(node.arguments, ', '), ')')}"

    # Type

    @staticmethod
    def leave_named_type(node: PrintedNode, *_args: Any) -> str:
        return node.name

    @staticmethod
    def leave_list_type(node: PrintedNode, *_args: Any) -> str:
        return f"[{node.type}]"

    @staticmethod
    def leave_non_null_type(node: PrintedNode, *_args: Any) -> str:
        return f"{node.type}!"

    # Type System Definitions

    @staticmethod
    def leave_schema_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            (
                "schema",
                join(node.directives, " "),
                block(node.operation_types),
            ),
            " ",
        )

    @staticmethod
    def leave_operation_type_definition(node: PrintedNode, *_args: Any) -> str:
        return f"{node.operation.value}: {node.type}"

    @staticmethod
    def leave_scalar_type_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            (
                "scalar",
                node.name,
                join(node.directives, " "),
            ),
            " ",
        )

    @staticmethod
    def leave_object_type_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            (
                "type",
                node.name,
                wrap("implements ", join(node.interfaces, " & ")),
                join(node.directives, " "),
                block(node.fields),
            ),
            " ",
        )

    @staticmethod
    def leave_field_definition(node: PrintedNode, *_args: Any) -> str:
        args = node.arguments
        args = (
            wrap("(\n", indent(join(args, "\n")), "\n)")
            if has_multiline_items(args)
            else wrap("(", join(args, ", "), ")")
        )
        directives = wrap(" ", join(node.directives, " "))
        return (
            wrap("", node.description, "\n")
            + f"{node.name}{args}: {node.type}{directives}"
        )

    @staticmethod
    def leave_input_value_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            (
                f"{node.name}: {node.type}",
                wrap("= ", node.default_value),
                join(node.directives, " "),
            ),
            " ",
        )

    @staticmethod
    def leave_interface_type_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            (
                "interface",
                node.name,
                wrap("implements ", join(node.interfaces, " & ")),
                join(node.directives, " "),
                block(node.fields),
            ),
            " ",
        )

    @staticmethod
    def leave_union_type_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            (
                "union",
                node.name,
                join(node.directives, " "),
                wrap("= ", join(node.types, " | ")),
            ),
            " ",
        )

    @staticmethod
    def leave_enum_type_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            ("enum", node.name, join(node.directives, " "), block(node.values)), " "
        )

    @staticmethod
    def leave_enum_value_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            (node.name, join(node.directives, " ")), " "
        )

    @staticmethod
    def leave_input_object_type_definition(node: PrintedNode, *_args: Any) -> str:
        return wrap("", node.description, "\n") + join(
            ("input", node.name, join(node.directives, " "), block(node.fields)), " "
        )

    @staticmethod
    def leave_directive_definition(node: PrintedNode, *_args: Any) -> str:
        args = node.arguments
        args = (
            wrap("(\n", indent(join(args, "\n")), "\n)")
            if has_multiline_items(args)
            else wrap("(", join(args, ", "), ")")
        )
        repeatable = " repeatable" if node.repeatable else ""
        locations = join(node.locations, " | ")
        return (
            wrap("", node.description, "\n")
            + f"directive @{node.name}{args}{repeatable} on {locations}"
        )

    @staticmethod
    def leave_schema_extension(node: PrintedNode, *_args: Any) -> str:
        return join(
            ("extend schema", join(node.directives, " "), block(node.operation_types)),
            " ",
        )

    @staticmethod
    def leave_scalar_type_extension(node: PrintedNode, *_args: Any) -> str:
        return join(("extend scalar", node.name, join(node.directives, " ")), " ")

    @staticmethod
    def leave_object_type_extension(node: PrintedNode, *_args: Any) -> str:
        return join(
            (
                "extend type",
                node.name,
                wrap("implements ", join(node.interfaces, " & ")),
                join(node.directives, " "),
                block(node.fields),
            ),
            " ",
        )

    @staticmethod
    def leave_interface_type_extension(node: PrintedNode, *_args: Any) -> str:
        return join(
            (
                "extend interface",
                node.name,
                wrap("implements ", join(node.interfaces, " & ")),
                join(node.directives, " "),
                block(node.fields),
            ),
            " ",
        )

    @staticmethod
    def leave_union_type_extension(node: PrintedNode, *_args: Any) -> str:
        return join(
            (
                "extend union",
                node.name,
                join(node.directives, " "),
                wrap("= ", join(node.types, " | ")),
            ),
            " ",
        )

    @staticmethod
    def leave_enum_type_extension(node: PrintedNode, *_args: Any) -> str:
        return join(
            ("extend enum", node.name, join(node.directives, " "), block(node.values)),
            " ",
        )

    @staticmethod
    def leave_input_object_type_extension(node: PrintedNode, *_args: Any) -> str:
        return join(
            ("extend input", node.name, join(node.directives, " "), block(node.fields)),
            " ",
        )


def join(strings: Optional[Strings], separator: str = "") -> str:
    """Join strings in a given collection.

    Return an empty string if it is None or empty, otherwise join all items together
    separated by separator if provided.
    """
    return separator.join(s for s in strings if s) if strings else ""


def block(strings: Optional[Strings]) -> str:
    """Return strings inside a block.

    Given a collection of strings, return a string with each item on its own line,
    wrapped in an indented "{ }" block.
    """
    return wrap("{\n", indent(join(strings, "\n")), "\n}")


def wrap(start: str, string: Optional[str], end: str = "") -> str:
    """Wrap string inside other strings at start and end.

    If the string is not None or empty, then wrap with start and end, otherwise return
    an empty string.
    """
    return f"{start}{string}{end}" if string else ""


def indent(string: str) -> str:
    """Indent string with two spaces.

    If the string is not None or empty, add two spaces at the beginning of every line
    inside the string.
    """
    return wrap("  ", string.replace("\n", "\n  "))


def is_multiline(string: str) -> bool:
    """Check whether a string consists of multiple lines."""
    return "\n" in string


def has_multiline_items(strings: Optional[Strings]) -> bool:
    """Check whether one of the items in the list has multiple lines."""
    return any(is_multiline(item) for item in strings) if strings else False
