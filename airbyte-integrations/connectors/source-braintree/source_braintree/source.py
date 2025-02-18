#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import List, Iterable, Mapping, Any

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.yaml_declarative_source import (
    YamlDeclarativeSource,
)
from braintree.util.xml_util import XmlUtil

@dataclass
class BraintreeExtractor(RecordExtractor):
    """
    Extractor Template for all BrainTree streams.
    """

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        raise NotImplementedError()

    @staticmethod
    def _extract_as_array(container: dict | list, array_name: str):
        #  NOTE: So far what has been observed is that it is already a list when no
        #  records are returned.
        # examples: '<?xml version="1.0" encoding="UTF-8"?><plans type="array"/>'
        #           '<?xml version="1.0" encoding="UTF-8"?><discounts type="array"/>'
        if isinstance(container, list):
            return container

        record_list = container.get(array_name)
        if record_list is None:
            return []

        if not isinstance(record_list, list):
            return [record_list]

        return record_list

    def _extract_records(
            self,
            response: requests.Response,
            collection_name: str,
            array_name: str | None = None
    ) -> List[Mapping[str, Any]]:
        return self._extract_as_array(
            XmlUtil.dict_from_xml(response.text).get(collection_name),
            array_name or collection_name.removesuffix("s")
        )

@dataclass
class MerchantAccountExtractor(BraintreeExtractor):
    """
    Extractor for Merchant Accounts stream.
    It parses output XML and finds all `Merchant Account` occurrences in it.
    """

    def extract_records(
            self,
            response: requests.Response,
    ) -> List[Mapping[str, Any]]:
        return self._extract_records(response, "merchant_accounts")

@dataclass
class CustomerExtractor(BraintreeExtractor):
    """
    Extractor for Customers stream.
    It parses output XML and finds all `Customer` occurrences in it.
    """

    def extract_records(
            self,
            response: requests.Response,
    ) -> List[Mapping[str, Any]]:
        return self._extract_records(response, "customers")


@dataclass
class DiscountExtractor(BraintreeExtractor):
    """
    Extractor for Discounts stream.
    It parses output XML and finds all `Discount` occurrences in it.
    """

    def extract_records(
            self,
            response: requests.Response,
    ) -> List[Mapping[str, Any]]:
        return self._extract_records(response, "discounts")


@dataclass
class TransactionExtractor(BraintreeExtractor):
    """
    Extractor for Transactions stream.
    It parses output XML and finds all `Transaction` occurrences in it.
    """

    def extract_records(
            self,
            response: requests.Response,
    ) -> List[Mapping[str, Any]]:
        return self._extract_records(response, "credit_card_transactions", "transaction")

@dataclass
class SubscriptionExtractor(BraintreeExtractor):
    """
    Extractor for Subscriptions stream.
    It parses output XML and finds all `Subscription` occurrences in it.
    """

    def extract_records(
            self,
            response: requests.Response,
    ) -> List[Mapping[str, Any]]:
        return self._extract_records(response, "subscriptions")


@dataclass
class PlanExtractor(BraintreeExtractor):
    """
    Extractor for Plans stream.
    It parses output XML and finds all `Plan` occurrences in it.
    """

    def extract_records(
            self,
            response: requests.Response,
    ) -> List[Mapping[str, Any]]:
        return self._extract_records(response, "plans")


@dataclass
class DisputeExtractor(BraintreeExtractor):
    """
    Extractor for Disputes stream.
    It parses output XML and finds all `Dispute` occurrences in it.
    """

    def extract_records(
            self,
            response: requests.Response,
    ) -> List[Mapping[str, Any]]:
        return self._extract_records(response, "disputes")

# Declarative Source
class SourceBraintree(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})
