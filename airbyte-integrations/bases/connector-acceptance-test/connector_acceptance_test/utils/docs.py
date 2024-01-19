# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode


def remove_step_from_heading(heading: str) -> str:
    if "Step 1: " in heading:
        return heading.replace("Step 1: ", "")
    if "Step 2: " in heading:
        return heading.replace("Step 2: ", "")
    return heading


def required_titles_from_spec(spec: dict[str, Any]) -> tuple[list[str], bool]:
    titles = [spec["properties"][field]["title"].lower() for field in spec["required"] if field != "credentials"]
    has_credentials = True if "credentials" in spec["required"] else False
    return titles, has_credentials


def documentation_node(connector_documentation: str) -> SyntaxTreeNode:
    md = MarkdownIt("commonmark")
    tokens = md.parse(connector_documentation)
    return SyntaxTreeNode(tokens)


def header_name(n: SyntaxTreeNode) -> str:
    return n.to_tokens()[1].children[0].content


def prepare_lines_to_compare(connector_name: str, docs_line: str, template_line: str) -> tuple[str, str]:
    def _replace_link(docs_string: str, link_to_replace: str) -> str:
        docs_string = docs_string[: docs_string.index("(")] + link_to_replace + docs_string[docs_string.index(")") + 1 :]
        return docs_string

    connector_name_to_replace = "{connector_name}"
    link_to_replace = "({docs_link})"

    template_line = (
        template_line.replace(connector_name_to_replace, connector_name) if connector_name_to_replace in template_line else template_line
    )
    docs_line = _replace_link(docs_line, link_to_replace) if link_to_replace in template_line else docs_line

    return docs_line, template_line
