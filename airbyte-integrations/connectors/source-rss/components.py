#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import xml.etree.ElementTree as ET
from datetime import timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional

import requests
from dateutil.parser import parse as dateutil_parse

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(element: Optional[ET.Element]) -> Optional[str]:
    if element is None or element.text is None:
        return None
    text = element.text.strip()
    return text or None


def _to_iso_utc(value: Optional[str]) -> Optional[str]:
    """Normalize an RFC 822 (RSS) or ISO 8601 (Atom) timestamp to an ISO 8601 string in UTC."""
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        try:
            parsed = dateutil_parse(value)
        except (ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


class CustomExtractor(RecordExtractor):
    """
    Parses an RSS 2.0 / RSS 1.0 (RDF) / Atom feed into flat item records.

    Records are emitted oldest-first (reverse document order, feeds list newest first) with the
    `published` timestamp normalized to ISO 8601 UTC so it can be used as the incremental cursor.
    """

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as error:
            raise ValueError(f"The response from {response.url} is not a valid RSS/Atom feed: {error}") from error

        if _local_name(root.tag) == "feed":
            records = [self._atom_entry_to_record(entry) for entry in root if _local_name(entry.tag) == "entry"]
        else:
            records = [self._rss_item_to_record(item) for item in root.iter() if _local_name(item.tag) == "item"]

        return records[::-1]

    @staticmethod
    def _rss_item_to_record(item: ET.Element) -> Dict[str, Any]:
        record: Dict[str, Any] = {}
        published: Optional[str] = None
        fallback_published: Optional[str] = None
        for child in item:
            name = _local_name(child.tag)
            if name in ("title", "link", "description", "author", "comments", "guid"):
                value = _text(child)
                if value is not None and name not in record:
                    record[name] = value
            elif name == "creator" and "author" not in record:
                value = _text(child)
                if value is not None:
                    record["author"] = value
            elif name == "category" and "category" not in record:
                value = _text(child)
                if value is not None:
                    record["category"] = value
            elif name == "enclosure":
                url = child.get("url")
                if url and "enclosure" not in record:
                    record["enclosure"] = url
            elif name == "pubDate":
                published = _text(child)
            elif name == "date" and fallback_published is None:
                fallback_published = _text(child)

        iso_published = _to_iso_utc(published) or _to_iso_utc(fallback_published)
        if iso_published is not None:
            record["published"] = iso_published
        return record

    @staticmethod
    def _atom_entry_to_record(entry: ET.Element) -> Dict[str, Any]:
        record: Dict[str, Any] = {}
        links: List[ET.Element] = []
        summary: Optional[str] = None
        content: Optional[str] = None
        published: Optional[str] = None
        updated: Optional[str] = None
        for child in entry:
            name = _local_name(child.tag)
            if name == "title":
                value = _text(child)
                if value is not None:
                    record["title"] = value
            elif name == "link":
                links.append(child)
            elif name == "summary":
                summary = _text(child)
            elif name == "content":
                content = _text(child)
            elif name == "author" and "author" not in record:
                author_name = next((_text(part) for part in child if _local_name(part.tag) == "name"), None)
                if author_name is not None:
                    record["author"] = author_name
            elif name == "category" and "category" not in record:
                term = child.get("term")
                if term:
                    record["category"] = term
            elif name == "id":
                value = _text(child)
                if value is not None:
                    record["guid"] = value
            elif name == "published":
                published = _text(child)
            elif name == "updated":
                updated = _text(child)

        alternate = next((link for link in links if link.get("rel") in (None, "alternate")), None)
        if alternate is not None and alternate.get("href"):
            record["link"] = alternate.get("href")
        description = summary or content
        if description is not None:
            record["description"] = description
        iso_published = _to_iso_utc(published) or _to_iso_utc(updated)
        if iso_published is not None:
            record["published"] = iso_published
        return record
