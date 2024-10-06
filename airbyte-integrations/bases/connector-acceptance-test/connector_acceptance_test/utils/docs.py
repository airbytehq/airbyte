# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import re
from difflib import get_close_matches
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
    has_credentials = False
    spec_required = spec["required"]
    spec_properties = spec["properties"].keys()
    creds = ["credentials", "client_id", "client_secret", "access_token", "refresh_token"]

    if "credentials" in spec["required"] or "client_id" in spec["required"] or "client_secret" in spec_required:
        has_credentials = True
    if "credentials" in spec["required"] or "client_id" in spec["required"] or "client_secret" in spec_properties:
        has_credentials = True
    if has_credentials:
        [spec_required.remove(cred) for cred in creds if cred in spec_required]

    titles = [spec["properties"][field]["title"].lower() for field in spec_required]
    return titles, has_credentials


def documentation_node(connector_documentation: str) -> SyntaxTreeNode:
    md = MarkdownIt("commonmark")
    tokens = md.parse(connector_documentation)
    return SyntaxTreeNode(tokens)


def header_name(n: SyntaxTreeNode) -> str:
    return n.to_tokens()[1].children[0].content


def prepare_lines_to_compare(connector_name: str, docs_line: str, template_line: str) -> tuple[str]:
    def _replace_link(docs_string: str, link_to_replace: str) -> str:
        try:
            docs_string = docs_string[: docs_string.index("(")] + link_to_replace + docs_string[docs_string.index(")") + 1 :]
            return docs_string
        except ValueError:  # ValueError if actual docs doesn't have expected links
            return docs_string

    connector_name_to_replace = "{connector_name}"
    link_to_replace = "({docs_link})"

    template_line = (
        template_line.replace(connector_name_to_replace, connector_name) if connector_name_to_replace in template_line else template_line
    )
    docs_line = _replace_link(docs_line, link_to_replace) if link_to_replace in template_line else docs_line

    return docs_line, template_line


def remove_not_required_step_headers(headers: tuple[str]) -> tuple[str]:
    """
    Removes headers like Step 1.1 Step 3 Step 2.3 from actual headers, if they placed after Step 1: header.
    from: "Connector name", "Prerequisites", "Setup guide", "Step 1: do something 1", "Step 1.11: do something 11",
           "Step 2: do something 2", "Step 2.1: do something 2.1", "Changelog"
    To: "Connector name", "Prerequisites", "Setup guide", "Step 1: do something 1", "Step 2: do something 2", "Changelog"
    This is connector specific headers, so we can ignore them.
    """
    step_one_index = None
    for header in headers:
        if re.search("Step 1: ", header):
            step_one_index = headers.index(header)
    if not step_one_index:  # docs doesn't have Step 1 headers
        return headers

    step_headers = headers[step_one_index:]
    pattern = "Step \d+.?\d*: "
    step = "Step 1: "
    i = 0
    while i < len(step_headers):
        if step in step_headers[i]:  # if Step 1/2: is substring of current header
            if i + 1 < len(step_headers) and re.match(pattern, step_headers[i + 1]):  # check that header has Step x:
                if "Step 2: " in step_headers[i + 1]:  # found Step 2, it's required header, move to the next one
                    step = "Step 2: "
                    i += 1
                    continue
                else:
                    step_headers.remove(step_headers[i + 1])  # remove all other steps from headers
                    continue  # move to the next header after Step 1/2 header
            else:
                break
        break

    headers = headers[:step_one_index]
    headers.extend(step_headers)
    return headers


def reason_titles_not_match(heading_names_value: str, template_headings_value: str, template_headings: list[str]) -> str:
    reason = (
        f"Documentation structure doesn't follow standard template. Heading '{heading_names_value}' is not in the right place, "
        f"the name of heading is incorrect or the heading name is not expected.\n"
    )
    close_titles = get_close_matches(heading_names_value, template_headings)
    if close_titles and close_titles[0] != heading_names_value:
        diff = f"Diff:\nActual Heading: '{heading_names_value}'. Possible correct heading: '{close_titles}'. Expected Heading: '{template_headings_value}'."
    else:
        diff = f"Diff:\nActual Heading: '{heading_names_value}'. Expected Heading: '{template_headings_value}'"
    return reason + diff


def reason_missing_titles(template_headings_index: int, template_headings: list[str]) -> str:
    return (
        f"Documentation structure doesn't follow standard template. docs is not full."
        f"\nMissing headers: {template_headings[template_headings_index:]}"
    )


def description_end_line_index(heading: str, actual_headings: list[str], header_line_map: dict[str, int]) -> int:
    if actual_headings.index(heading) + 1 == len(actual_headings):
        return -1
    return header_line_map[actual_headings[actual_headings.index(heading) + 1]]


def prepare_headers(connector_documentation: dict) -> list[str]:
    node = documentation_node(connector_documentation)
    headers = [header_name(n) for n in node if n.type == "heading"]  # find all headers
    headers = remove_not_required_step_headers(headers)  # remove Step 1.1 Step 3 ... headers
    headers = tuple([remove_step_from_heading(h) for h in headers])  # remove Step 1 and Step 2 from header name
    return headers
