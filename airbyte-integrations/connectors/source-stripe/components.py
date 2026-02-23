#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, MutableMapping

import dpath
import requests

from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.types import Config


@dataclass
class InvoiceLineItemsEventExtractor(RecordExtractor):
    """
    Extracts individual line items from Stripe invoice events.

    The Stripe events API returns invoice objects at data.object, with line items
    nested at data.object.lines.data. The standard DpathExtractor + DpathFlattenFields
    approach emits the invoice object itself rather than individual line items because
    DpathFlattenFields only handles dicts (not arrays) and transformations are 1:1.

    This extractor iterates over events, extracts line items from each invoice,
    and yields one record per line item with parent invoice metadata attached.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        for body in self.decoder.decode(response):
            events = dpath.get(body, "data", default=[])
            if not isinstance(events, list):
                continue
            for event in events:
                yield from self._extract_line_items_from_event(event)

    def _extract_line_items_from_event(self, event: Mapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        invoice = event.get("data", {}).get("object")
        if not invoice or not isinstance(invoice, dict):
            return

        is_deleted = event.get("type", "").endswith(".deleted")
        now_ts = int(datetime.now(timezone.utc).timestamp())
        invoice_updated = int(event.get("created", now_ts))
        invoice_id = invoice.get("id")
        invoice_created = invoice.get("created")

        lines_obj = invoice.get("lines")
        if not isinstance(lines_obj, dict):
            return
        lines_data = lines_obj.get("data")
        if not isinstance(lines_data, list):
            return

        for line_item in lines_data:
            if not isinstance(line_item, dict):
                continue
            record: MutableMapping[str, Any] = dict(line_item)
            record["invoice_id"] = invoice_id
            record["invoice_created"] = invoice_created
            record["invoice_updated"] = invoice_updated
            if is_deleted:
                record["is_deleted"] = True
            yield record
