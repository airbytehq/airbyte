#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import csv
import gzip
import json
import logging
from dataclasses import InitVar, dataclass
from io import StringIO
from typing import Any, Generator, List, Mapping, MutableMapping

import requests
import xmltodict

from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


logger = logging.getLogger("airbyte")


@dataclass
class GzipCsvDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        yield from csv.DictReader(StringIO(document), delimiter="\t")


@dataclass
class GzipXmlDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        try:
            parsed = xmltodict.parse(document, attr_prefix="", cdata_key="value", force_list={"Message"})
        except Exception as e:
            logger.warning(f"Unable to parse the report for the stream {self.name}, error: {str(e)}")
            return []

        reports = parsed.get("AmazonEnvelope", {}).get("Message", {})
        for report in reports:
            yield report.get("OrderReport", {})


@dataclass
class GzipJsonDecoder(Decoder):
    """
    Decoder strategy that attempts to decompress a response using GZIP first and then parses the resulting
    document as JSON. Also as a backup, this works for uncompressed responses that are already in JSON format
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        try:
            body_json = json.loads(document)
            yield from self.parse_body_json(body_json)
        except requests.exceptions.JSONDecodeError:
            logger.warning(f"Response cannot be parsed into json: {response.status_code=}, {response.text=}")
            yield {}

    @staticmethod
    def parse_body_json(
        body_json: MutableMapping[str, Any] | List[MutableMapping[str, Any]],
    ) -> Generator[MutableMapping[str, Any], None, None]:
        if not isinstance(body_json, list):
            body_json = [body_json]
        if len(body_json) == 0:
            yield {}
        else:
            yield from body_json


@dataclass
class SellerFeedbackReportsGzipCsvDecoder(Decoder):
    parameters: InitVar[Mapping[str, Any]]
    NORMALIZED_FIELD_NAMES = ["date", "rating", "comments", "response", "order_id", "rater_email"]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        # csv header field names for this report differ per marketplace (are localized to marketplace language)
        # but columns come in the same order, so we set fieldnames to our custom ones
        # and raise error if original and custom header field count does not match
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        reader = csv.DictReader(StringIO(document), delimiter="\t", fieldnames=self.NORMALIZED_FIELD_NAMES)
        original_fieldnames = next(reader)
        if len(original_fieldnames) != len(self.NORMALIZED_FIELD_NAMES):
            raise ValueError("Original and normalized header field count does not match")

        yield from reader


@dataclass
class GetXmlBrowseTreeDataDecoder(Decoder):
    parameters: InitVar[Mapping[str, Any]]
    NORMALIZED_FIELD_NAMES = ["date", "rating", "comments", "response", "order_id", "rater_email"]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        # csv header field names for this report differ per marketplace (are localized to marketplace language)
        # but columns come in the same order, so we set fieldnames to our custom ones
        # and raise error if original and custom header field count does not match
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        try:
            parsed = xmltodict.parse(
                document,
                dict_constructor=dict,
                attr_prefix="",
                cdata_key="text",
                force_list={"attribute", "id", "refinementField"},
            )
        except Exception as e:
            logger.warning(f"Unable to parse the report for the stream, error: {str(e)}")
            parsed = {}

        yield from parsed.get("Result", {}).get("Node", [])
