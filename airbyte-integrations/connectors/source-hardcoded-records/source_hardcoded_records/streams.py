# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from abc import ABC
from typing import Any, Iterable, Mapping

from airbyte_cdk.sources.streams import Stream


class HardcodedStream(Stream, ABC):
    primary_key = None
    sample_record = None

    def __init__(self, count: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """Generate records from the stream."""
        for _ in range(self.count):
            yield self.sample_record


class Products(HardcodedStream):
    sample_record = {
        "id": 1,
        "make": "Mazda",
        "model": "MX-5",
        "year": 2008,
        "price": 2869,
        "created_at": "2022-02-01T17:02:19+00:00",
        "updated_at": "2022-11-01T17:02:19+00:00",
    }


class Customers(HardcodedStream):
    sample_record = {
        "id": 6569096478909,
        "email": "test@test.com",
        "created_at": "2023-04-13T02:30:04-07:00",
        "updated_at": "2023-04-24T06:53:48-07:00",
        "first_name": "New Test",
        "last_name": "Customer",
        "orders_count": 0,
        "state": "disabled",
        "total_spent": 0.0,
        "last_order_id": None,
        "note": "updated_mon_24.04.2023",
        "verified_email": True,
        "multipass_identifier": None,
        "tax_exempt": False,
        "tags": "",
        "last_order_name": None,
        "currency": "USD",
        "phone": "+380639379992",
        "addresses": [
            {
                "id": 8092523135165,
                "customer_id": 6569096478909,
                "first_name": "New Test",
                "last_name": "Customer",
                "company": "Test Company",
                "address1": "My Best Accent",
                "address2": "",
                "city": "Fair Lawn",
                "province": "New Jersey",
                "country": "United States",
                "zip": "07410",
                "phone": "",
                "name": "New Test Customer",
                "province_code": "NJ",
                "country_code": "US",
                "country_name": "United States",
                "default": True,
            }
        ],
        "accepts_marketing": True,
        "accepts_marketing_updated_at": "2023-04-13T02:30:04-07:00",
        "marketing_opt_in_level": "single_opt_in",
        "tax_exemptions": "[]",
        "email_marketing_consent": {
            "state": "subscribed",
            "opt_in_level": "single_opt_in",
            "consent_updated_at": "2023-04-13T02:30:04-07:00",
        },
        "sms_marketing_consent": {
            "state": "not_subscribed",
            "opt_in_level": "single_opt_in",
            "consent_updated_at": None,
            "consent_collected_from": "SHOPIFY",
        },
        "admin_graphql_api_id": "gid://shopify/Customer/6569096478909",
        "default_address": {
            "id": 8092523135165,
            "customer_id": 6569096478909,
            "first_name": "New Test",
            "last_name": "Customer",
            "company": "Test Company",
            "address1": "My Best Accent",
            "address2": "",
            "city": "Fair Lawn",
            "province": "New Jersey",
            "country": "United States",
            "zip": "07410",
            "phone": "",
            "name": "New Test Customer",
            "province_code": "NJ",
            "country_code": "US",
            "country_name": "United States",
            "default": True,
        },
        "shop_url": "airbyte-integration-test",
    }


class DummyFields(HardcodedStream):
    sample_record = {
        "field1": "valuevaluevaluevaluevalue1",
        "field2": "valuevaluevaluevaluevalue1",
        "field3": "valuevaluevaluevaluevalue1",
        "field4": "valuevaluevaluevaluevalue1",
        "field5": "valuevaluevaluevaluevalue1",
    }
