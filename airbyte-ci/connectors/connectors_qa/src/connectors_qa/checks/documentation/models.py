# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import re
from pathlib import Path
from typing import Any, Dict, Iterator, List

from connector_ops.utils import Connector  # type: ignore
from jinja2 import Environment, FileSystemLoader
from markdown_it.tree import SyntaxTreeNode

from .helpers import documentation_node, header_name, remove_step_from_heading


class SectionLines:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"{self.start} - {self.end}"


class SectionContent:
    def __init__(self, header: str):
        self.header = header
        self._content: List[str] = []

    @property
    def content(self) -> List[str]:
        return self._content

    @content.setter
    def content(self, content: str) -> None:
        self._content.append(content)

    def __repr__(self) -> str:
        return f"{self.header}: {self.content}"


class Content:
    HEADING = "heading"
    supported_header_levels = ["h1", "h2", "h3", "h4"]

    def __init__(self) -> None:
        self.content = self._content()
        self.node = self._node()
        self.header_line_map = self._header_line_map()
        self.headers = self._headers()
        self.sections = self._sections()

    def _content(self) -> str:
        raise NotImplementedError

    def _sections(self) -> List[SectionContent]:
        raise NotImplementedError

    def _node(self) -> SyntaxTreeNode:
        node = documentation_node(self.content)
        return node

    def _headers(self) -> List[str]:
        headers = []
        for n in self.node.walk():  # type: SyntaxTreeNode
            if n.type == self.HEADING and n.tag in self.supported_header_levels:
                headers.append(remove_step_from_heading(header_name(n)))
        return headers

    def _header_line_map(self) -> Dict[str, List[SectionLines]]:
        headers: List[str] = []
        starts: List[int] = []
        header_line_map: Dict[str, List[SectionLines]] = {}

        for n in self.node.walk():  # type: SyntaxTreeNode
            if n.type == self.HEADING and n.map is not None:
                headers.append(header_name(n))
                starts.append(n.map[1])

        i = 0
        while len(headers) > i:
            header = headers[i]
            start_index = i
            end_index: int | None = starts[start_index + 1] - 1 if start_index + 1 < len(headers) else None
            section_lines = SectionLines(start=starts[start_index], end=end_index if end_index is not None else -1)

            if header not in header_line_map:
                header_line_map[header] = [section_lines]
            else:
                header_line_map[header].append(section_lines)
            i += 1

        return header_line_map

    def section(self, header: str) -> List[str] | None:
        for s in self.sections:
            if s.header == header:
                return s.content
        return None


class DocumentationContent(Content):
    def __init__(self, connector: Connector):
        self.connector = connector
        super().__init__()
        self.links = self._links()

    def _content(self) -> str:
        return self.connector.documentation_file_path.read_text().rstrip()

    def _links(self) -> list[str]:
        return re.findall("(?<!example: )(https?://[^\s\`)]+)", self.content)

    def _sections(self) -> list[SectionContent]:
        sections_list = []

        with open(self.connector.documentation_file_path) as docs_file:
            doc_lines = docs_file.readlines()

            for key, value in self.header_line_map.items():
                section = SectionContent(header=key)
                sections_list.append(section)

                for lines in value:
                    section_content = "".join(doc_lines[lines.start : lines.end])
                    section.content = section_content  # type: ignore

        return sections_list


class TemplateContent(Content):
    template_file = "template.md.j2"
    template_folder = Path(__file__).parent / "templates/"

    def __init__(self, connector_name: str):
        self.connector_name = connector_name
        super().__init__()
        self.sections = self._sections()

    def _content(self) -> str:
        environment = Environment(loader=FileSystemLoader(self.template_folder))
        template = environment.get_template(self.template_file)
        template_content = template.render(connector_name=self.connector_name)
        return template_content

    def _sections(self) -> list[SectionContent]:
        template_lines = self.content.splitlines(keepends=True)

        sections_list = []

        for key, value in self.header_line_map.items():
            section = SectionContent(header=key)
            sections_list.append(section)

            for lines in value:
                section_content = "".join(template_lines[lines.start : lines.end])
                section.content = section_content  # type: ignore

        return sections_list

    def headers_with_tag(self) -> list[str]:
        headers = []
        for n in self.node:  # type: ignore
            if n.type == self.HEADING and n.tag in self.supported_header_levels:
                header = "#" * int(n.tag.replace("h", "")) + " " + remove_step_from_heading(header_name(n))
                headers.append(header)

        return headers
