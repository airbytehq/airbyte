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
from braintree.merchant_account.merchant_account import MerchantAccount
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

    def _get_json_from_resource(self, resource_obj: Union[AttributeGetter, List[AttributeGetter]]):
        if isinstance(resource_obj, list):
            return [obj if not isinstance(obj, AttributeGetter) else self._get_json_from_resource(obj) for obj in resource_obj]
        obj_dict = resource_obj.__dict__
        result = dict()
        for attr in obj_dict:
            if not attr.startswith("_"):
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
        merchant_accounts = data.get('merchant_account')
        return [] if not merchant_accounts else [self._get_json_from_resource(MerchantAccount(None, merchant_account)) \
                                                 for merchant_account in merchant_accounts]


@dataclass
class CustomerExtractor(BraintreeExtractor):
    """
    Extractor for Customers stream.
    It parses output XML and finds all `Customer` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)['customers']
        customers = data.get('customer')
        return [] if not customers else [self._get_json_from_resource(Customer(None, customer)) \
                                         for customer in customers]


@dataclass
class DiscountExtractor(BraintreeExtractor):
    """
    Extractor for Discounts stream.
    It parses output XML and finds all `Discount` occurrences in it.
    """

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)
        discounts = data['discounts']
        return [] if not discounts else [self._get_json_from_resource(Discount(None, discount)) \
                                         for discount in discounts]


# Declarative Source
class SourceBraintreeNoCode(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})
