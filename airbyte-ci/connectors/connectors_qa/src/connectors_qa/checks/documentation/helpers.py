# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import re
from difflib import get_close_matches
from pathlib import Path
from typing import Any

from connector_ops.utils import Connector  # type: ignore
from jinja2 import Environment, FileSystemLoader
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
    spec_required = spec.get("required")
    if not spec_required:
        return [], False

    spec_properties = spec["properties"].keys()
    creds = ["credentials", "client_id", "client_secret", "access_token", "refresh_token", "authorization"]

    if any(x in spec_required for x in creds):
        has_credentials = True
    if any(x in spec_properties for x in creds):
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
    return n.to_tokens()[1].children[0].content  # type: ignore


def replace_connector_specific_urls_from_section(content: str) -> str:
    link_to_replace = "{docs_link}"

    def _replace_link(docs_string: str) -> str:
        links = re.findall("(https?://[^\s)]+)", docs_string)
        for link in links:
            docs_string = docs_string.replace(link, link_to_replace)
        return docs_string

    content = _replace_link(content)
    return content


def remove_not_required_step_headers(headers: list[str]) -> list[str]:
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

    headers = headers[:step_one_index] + step_headers
    return headers


def reason_titles_not_match(heading_names_value: str, template_headings_value: str, template_headings: list[str]) -> str:
    reason = f"Heading '{heading_names_value}' is not in the right place, the name of heading is incorrect or not expected.\n"
    close_titles = get_close_matches(heading_names_value, template_headings)
    if close_titles and close_titles[0] != heading_names_value:
        diff = f"Diff:\nActual Heading: '{heading_names_value}'. Possible correct heading: '{close_titles}'. Expected Heading: '{template_headings_value}'"
    else:
        diff = f"Diff:\nActual Heading: '{heading_names_value}'. Expected Heading: '{template_headings_value}'"
    return reason + diff


def reason_missing_titles(template_headings_index: int, template_headings: list[str], not_required_headers: list[str]) -> str:
    missing = template_headings[template_headings_index:]
    required = [m for m in missing if m not in not_required_headers]
    return f"Required missing headers: {required}. All missing headers: {missing}"


def description_end_line_index(heading: str, actual_headings: tuple[str, ...], header_line_map: dict[str, int]) -> int:
    if actual_headings.index(heading) + 1 == len(actual_headings):
        return  # type: ignore
    return header_line_map[actual_headings[actual_headings.index(heading) + 1]] - 1


def prepare_headers(headers: list[str]) -> list[str]:
    headers = remove_not_required_step_headers(headers)  # remove Step 1.1 Step 3 ... headers
    headers = [remove_step_from_heading(h) for h in headers]  # remove Step 1 and Step 2 from header name
    return headers


def prepare_changelog_to_compare(docs: str) -> str:
    docs_to_compare = []
    _siblings_content = []
    n = "\n"
    node = documentation_node(docs)

    for sibling in node[0].siblings:
        _siblings_content.append(sibling.content.rstrip())

    for c in _siblings_content:
        if n in c:
            docs_to_compare += [_c + n for _c in c.split(n)]
        else:
            docs_to_compare.append(c)

    return "".join(docs_to_compare)


def generate_description(template_file: str, kwargs: dict[str, Any]) -> str:
    environment = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates/"))
    template = environment.get_template(template_file)
    template_content = template.render(**kwargs)
    return template_content
