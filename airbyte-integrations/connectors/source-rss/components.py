# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import html.entities
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Iterable, List, MutableMapping, Optional, Tuple
from urllib.parse import urljoin

import requests
from dateutil import parser as dateutil_parser

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


logger = logging.getLogger("airbyte")

ATOM_NS = "http://www.w3.org/2005/Atom"
ATOM_03_NS = "http://purl.org/atom/ns#"
RSS_10_NS = "http://purl.org/rss/1.0/"
RSS_090_NS = "http://my.netscape.com/rdf/simple/0.9/"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DC_NS = "http://purl.org/dc/elements/1.1/"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
MEDIA_NS = "http://search.yahoo.com/mrss/"
XML_BASE_ATTRIBUTE = "{http://www.w3.org/XML/1998/namespace}base"

_XML_ENTITIES = {"amp", "lt", "gt", "quot", "apos"}
_CDATA_SECTION = re.compile(r"(<!\[CDATA\[.*?\]\]>)", re.DOTALL)
_ENTITY_OR_AMPERSAND = re.compile(r"&(?:(#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);)?")
_XML_DECLARATION = re.compile(r"^<\?xml[^>]*\?>")
_DECLARED_ENCODING = re.compile(rb"^\s*<\?xml[^>]*encoding\s*=\s*[\"']([A-Za-z0-9._:-]+)[\"']")
_HEADER_CHARSET = re.compile(r"charset\s*=\s*[\"']?([^;\"'\s]+)", re.IGNORECASE)

# Control characters are not allowed in XML 1.0, but feeds still contain them. They are shifted into a
# private-use plane before parsing and shifted back afterwards, so their values survive unchanged.
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_SHIFTED_CONTROL_CHARACTERS = re.compile(r"[\U000f0000-\U000f001f]")
_CONTROL_CHARACTER_SHIFT = 0xF0000

Field = Tuple[str, str]


class CustomExtractor(RecordExtractor):
    """Extracts items from RSS 2.0, RSS 0.9x, RDF (RSS 1.0) and Atom feeds, newest last."""

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        root = _parse_feed(response)
        if root is None:
            return []

        base_url = urljoin(response.url or "", root.get(XML_BASE_ATTRIBUTE, ""))
        namespace, name = _split_tag(root.tag)
        if name == "feed" and namespace in (ATOM_NS, ATOM_03_NS):
            records = [_atom_entry_to_record(entry, namespace, base_url) for entry in root.iter(f"{{{namespace}}}entry")]
        elif name == "rss" and namespace == "":
            records = [_rss_item_to_record(item, "", base_url) for item in root.iter("item")]
        elif name == "RDF" and namespace == RDF_NS:
            records = [
                _rss_item_to_record(item, item_namespace, base_url)
                for item_namespace in (RSS_10_NS, RSS_090_NS)
                for item in root.iter(f"{{{item_namespace}}}item")
            ]
        else:
            logger.warning(
                f"The response from {response.url} is not an RSS, RDF or Atom feed: its root element is <{name}>. "
                "No records were extracted. Check that the configured URL points to a feed."
            )
            return []

        return records[::-1]


def _parse_feed(response: requests.Response) -> Optional[ET.Element]:
    document = _repair_document(_decode(response))
    try:
        return ET.fromstring(document)
    except ET.ParseError as error:
        logger.warning(
            f"The response from {response.url} could not be parsed as an RSS, RDF or Atom feed ({error}). "
            "No records were extracted. Check that the configured URL points to a feed."
        )
        return None


def _decode(response: requests.Response) -> str:
    content = response.content
    header_charset = _HEADER_CHARSET.search(response.headers.get("Content-Type", ""))
    declared_encoding = _DECLARED_ENCODING.match(content)
    candidates = [
        "utf-8-sig" if content.startswith(b"\xef\xbb\xbf") else None,
        "utf-16" if content.startswith((b"\xff\xfe", b"\xfe\xff")) else None,
        header_charset.group(1) if header_charset else None,
        declared_encoding.group(1).decode("ascii") if declared_encoding else None,
        "utf-8",
    ]
    for encoding in candidates:
        if not encoding:
            continue
        try:
            return content.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return content.decode("utf-8", errors="replace")


def _repair_document(document: str) -> str:
    document = _XML_DECLARATION.sub("", document.lstrip("\ufeff \t\r\n"), count=1)
    document = _CONTROL_CHARACTERS.sub(lambda match: chr(ord(match.group()) + _CONTROL_CHARACTER_SHIFT), document)
    return "".join(
        part if part.startswith("<![CDATA[") else _ENTITY_OR_AMPERSAND.sub(_repair_entity, part) for part in _CDATA_SECTION.split(document)
    )


def _repair_entity(match: "re.Match[str]") -> str:
    reference = match.group(1)
    if reference is None:
        return "&amp;"
    if reference.startswith("#"):
        try:
            code_point = int(reference[2:], 16) if reference[1] in "xX" else int(reference[1:])
            character = chr(code_point)
        except (ValueError, OverflowError):
            return f"&amp;{reference};"
        if _CONTROL_CHARACTERS.fullmatch(character):
            return chr(code_point + _CONTROL_CHARACTER_SHIFT)
        if code_point in (0xFFFE, 0xFFFF) or 0xD800 <= code_point <= 0xDFFF:
            return f"&amp;{reference};"
        return match.group(0)
    if reference in _XML_ENTITIES:
        return match.group(0)
    replacement = html.entities.html5.get(f"{reference};")
    if replacement is None:
        return f"&amp;{reference};"
    return "".join(f"&#{ord(character)};" for character in replacement)


def _split_tag(tag: str) -> Tuple[str, str]:
    if tag.startswith("{"):
        namespace, _, name = tag[1:].partition("}")
        return namespace, name
    return "", tag


def _qualified(field: Field) -> str:
    namespace, name = field
    return f"{{{namespace}}}{name}" if namespace else name


def _first(element: ET.Element, *fields: Field) -> Optional[ET.Element]:
    for field in fields:
        child = element.find(_qualified(field))
        if child is not None:
            return child
    return None


def _restore_control_characters(value: str) -> str:
    return _SHIFTED_CONTROL_CHARACTERS.sub(lambda match: chr(ord(match.group()) - _CONTROL_CHARACTER_SHIFT), value)


def _text(element: ET.Element) -> str:
    return _restore_control_characters("".join(element.itertext())).strip()


def _markup(element: ET.Element) -> str:
    """Return the element's content as published, keeping any child markup."""
    if len(element) == 0:
        return _text(element)
    inner = (element.text or "") + "".join(ET.tostring(child, encoding="unicode") for child in element)
    return _restore_control_characters(inner).strip()


def _to_utc_iso(value: str) -> Optional[str]:
    if not value:
        return None
    parsed: Optional[datetime]
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        try:
            parsed = dateutil_parser.parse(value)
        except (ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _set(record: MutableMapping[str, Any], key: str, element: Optional[ET.Element], read: Callable[[ET.Element], str]) -> None:
    if element is not None:
        record[key] = read(element)


def _set_published(record: MutableMapping[str, Any], candidates: List[Optional[ET.Element]]) -> None:
    for element in candidates:
        if element is not None:
            published = _to_utc_iso(_text(element))
            if published:
                record["published"] = published
                return


def _rss_item_to_record(item: ET.Element, namespace: str, base_url: str) -> MutableMapping[str, Any]:
    item_base_url = urljoin(base_url, item.get(XML_BASE_ATTRIBUTE, ""))
    record: MutableMapping[str, Any] = {}
    _set(record, "title", _first(item, (namespace, "title")), _text)

    link = _first(item, (namespace, "link"))
    guid = _first(item, (namespace, "guid"))
    if link is not None:
        record["link"] = _resolve(item_base_url, _text(link))
    elif guid is not None and guid.get("isPermaLink", "true").lower() != "false" and _text(guid).startswith(("http://", "https://")):
        record["link"] = _text(guid)

    _set(record, "description", _first(item, (namespace, "description"), (CONTENT_NS, "encoded")), _markup)
    _set(record, "author", _first(item, (namespace, "author"), (DC_NS, "creator")), _text)
    _set(record, "category", _first(item, (namespace, "category"), (DC_NS, "subject")), _text)
    _set(record, "comments", _first(item, (namespace, "comments")), _text)

    enclosure = _first(item, (namespace, "enclosure"))
    if enclosure is not None and enclosure.get("url") is not None:
        record["enclosure"] = _resolve(item_base_url, enclosure.get("url", "").strip())

    if guid is not None:
        record["guid"] = _text(guid)
    elif item.get(f"{{{RDF_NS}}}about") is not None:
        record["guid"] = item.get(f"{{{RDF_NS}}}about", "").strip()

    _set_published(record, [_first(item, (namespace, "pubDate")), _first(item, (DC_NS, "date"))])
    return record


def _atom_entry_to_record(entry: ET.Element, namespace: str, base_url: str) -> MutableMapping[str, Any]:
    entry_base_url = urljoin(base_url, entry.get(XML_BASE_ATTRIBUTE, ""))
    record: MutableMapping[str, Any] = {}
    _set(record, "title", _first(entry, (namespace, "title")), _text)

    links = entry.findall(_qualified((namespace, "link")))
    alternate = next((link for link in links if link.get("rel", "alternate") == "alternate" and link.get("href") is not None), None)
    if alternate is not None:
        record["link"] = _resolve(urljoin(entry_base_url, alternate.get(XML_BASE_ATTRIBUTE, "")), alternate.get("href", "").strip())
    enclosure = next((link for link in links if link.get("rel") == "enclosure" and link.get("href") is not None), None)
    if enclosure is not None:
        record["enclosure"] = _resolve(urljoin(entry_base_url, enclosure.get(XML_BASE_ATTRIBUTE, "")), enclosure.get("href", "").strip())

    description = _first(entry, (namespace, "summary"), (namespace, "content"))
    if description is None:
        description = entry.find(f".//{{{MEDIA_NS}}}description")
    _set(record, "description", description, _markup)

    author = _first(entry, (namespace, "author"))
    if author is not None:
        record["author"] = _atom_person(author, namespace)
    else:
        _set(record, "author", _first(entry, (DC_NS, "creator")), _text)

    category = _first(entry, (namespace, "category"))
    if category is not None and category.get("term") is not None:
        record["category"] = category.get("term", "").strip()
    else:
        _set(record, "category", _first(entry, (DC_NS, "subject")), _text)

    _set(record, "guid", _first(entry, (namespace, "id")), _text)
    _set_published(
        record,
        [
            _first(entry, (namespace, "published")),
            _first(entry, (namespace, "issued")),
            _first(entry, (namespace, "updated")),
            _first(entry, (namespace, "modified")),
            _first(entry, (DC_NS, "date")),
        ],
    )
    return record


def _atom_person(person: ET.Element, namespace: str) -> str:
    name_element = _first(person, (namespace, "name"))
    email_element = _first(person, (namespace, "email"))
    name = _text(name_element) if name_element is not None else ""
    email = _text(email_element) if email_element is not None else ""
    if name and email:
        return f"{name} ({email})"
    return name or email


def _resolve(base_url: str, link: str) -> str:
    return urljoin(base_url, link) if link and base_url else link
