#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
import json
from dataclasses import dataclass
from typing import List, Union

from braintree.attribute_getter import AttributeGetter
from braintree.customer import Customer
from braintree.discount import Discount
from braintree.dispute import Dispute
from braintree.merchant_account.merchant_account import MerchantAccount
from braintree.plan import Plan
from braintree.subscription import Subscription
from braintree.transaction import Transaction
from braintree.util.xml_util import XmlUtil

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


@dataclass
class BraintreeExtractor(RecordExtractor):
    """
    Extractor Template for all BrainTree streams.
    """

    @staticmethod
    def _extract_as_array(results, attribute):
        if attribute not in results:
            return []

        value = results[attribute]
        if not isinstance(value, list):
            value = [value]
        return value

    def _get_json_from_resource(self, resource_obj: Union[AttributeGetter, List[AttributeGetter]]):
        if isinstance(resource_obj, list):
            return [obj if not isinstance(obj, AttributeGetter) else self._get_json_from_resource(obj) for obj in resource_obj]
        obj_dict = resource_obj.__dict__
        result = dict()
        for attr in obj_dict:
            if not attr.startswith("_"):
                if callable(obj_dict[attr]):
                    continue
                result[attr] = (
                    self._get_json_from_resource(obj_dict[attr])
                    if isinstance(obj_dict[attr], (AttributeGetter, list))
                    else obj_dict[attr].strftime('%Y-%m-%dT%H:%M:%SZ')
                    if isinstance(obj_dict[attr], datetime.datetime) else obj_dict[attr]
                )
        return result


@dataclass
class MerchantAccountExtractor(BraintreeExtractor):
    """
    Extractor for Merchant Accounts stream.
    It parses output XML and finds all `Merchant Account` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)['merchant_accounts']
        merchant_accounts = self._extract_as_array(data, 'merchant_account')
        return [self._get_json_from_resource(MerchantAccount(None, merchant_account)) for merchant_account in merchant_accounts]


@dataclass
class CustomerExtractor(BraintreeExtractor):
    """
    Extractor for Customers stream.
    It parses output XML and finds all `Customer` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)['customers']
        customers = self._extract_as_array(data, 'customer')
        return [self._get_json_from_resource(Customer(None, customer)) for customer in customers]


@dataclass
class DiscountExtractor(BraintreeExtractor):
    """
    Extractor for Discounts stream.
    It parses output XML and finds all `Discount` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)
        discounts = self._extract_as_array(data, 'discounts')
        return [self._get_json_from_resource(Discount(None, discount)) for discount in discounts]


@dataclass
class TransactionExtractor(BraintreeExtractor):
    """
    Extractor for Transactions stream.
    It parses output XML and finds all `Transaction` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)['credit_card_transactions']
        transactions = self._extract_as_array(data, 'transaction')
        return [self._get_json_from_resource(Transaction(None, transaction)) for transaction in transactions]


@dataclass
class SubscriptionExtractor(BraintreeExtractor):
    """
    Extractor for Subscriptions stream.
    It parses output XML and finds all `Subscription` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)['subscriptions']
        subscriptions = self._extract_as_array(data, 'subscription')
        return [self._get_json_from_resource(Subscription(None, subscription)) for subscription in subscriptions]


@dataclass
class PlanExtractor(BraintreeExtractor):
    """
    Extractor for Plans stream.
    It parses output XML and finds all `Plan` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)
        plans = self._extract_as_array(data, 'plans')
        return [self._get_json_from_resource(Plan(None, plan)) for plan in plans]

@dataclass
class DisputeExtractor(BraintreeExtractor):
    """
    Extractor for Disputes stream.
    It parses output XML and finds all `Dispute` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)['disputes']
        disputes = self._extract_as_array(data, 'dispute')
        return [self._get_json_from_resource(Dispute(None, dispute)) for dispute in disputes]


# Declarative Source
class SourceBraintreeNoCode(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})
