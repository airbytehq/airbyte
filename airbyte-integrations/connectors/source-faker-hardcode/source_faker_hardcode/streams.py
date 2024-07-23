#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping

from airbyte_cdk.sources.streams import Stream


class Countries(Stream):
    primary_key = "id"
    cursor_field = "updated_at"

    def __init__(self, count: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """ """
        sample_record = {
            "id": 417014808765,
            "name": "Ukraine",
            "code": "UA",
            "tax_name": "PDV",
            "tax": 0.2,
            "provinces": [],
            "shop_url": "airbyte-integration-test",
        }
        for _ in range(self.count):
            yield sample_record


class Orders(Stream):
    primary_key = "id"
    cursor_field = "updated_at"

    def __init__(self, count: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """ """
        sample_record = {
            "id": 4554821468349,
            "admin_graphql_api_id": "gid://shopify/Order/4554821468349",
            "app_id": 580111,
            "browser_ip": "176.113.167.23",
            "buyer_accepts_marketing": False,
            "cancel_reason": None,
            "cancelled_at": None,
            "cart_token": None,
            "checkout_id": 25048437719229,
            "checkout_token": "cf5d16a0a0688905bd551c6dec591506",
            "client_details": {
                "accept_language": "en-US,en;q=0.9,uk;q=0.8",
                "browser_height": 754,
                "browser_ip": "176.113.167.23",
                "browser_width": 1519,
                "session_hash": None,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53",
            },
            "closed_at": "2022-06-15T06:25:43-07:00",
            "company": None,
            "confirmation_number": None,
            "confirmed": True,
            "contact_email": "integration-test@airbyte.io",
            "created_at": "2022-06-15T05:16:53-07:00",
            "currency": "USD",
            "current_subtotal_price": 0.0,
            "current_subtotal_price_set": {
                "shop_money": {"amount": 0.0, "currency_code": "USD"},
                "presentment_money": {"amount": 0.0, "currency_code": "USD"},
            },
            "current_total_additional_fees_set": None,
            "current_total_discounts": 0.0,
            "current_total_discounts_set": {
                "shop_money": {"amount": 0.0, "currency_code": "USD"},
                "presentment_money": {"amount": 0.0, "currency_code": "USD"},
            },
            "current_total_duties_set": None,
            "current_total_price": 0.0,
            "current_total_price_set": {
                "shop_money": {"amount": 0.0, "currency_code": "USD"},
                "presentment_money": {"amount": 0.0, "currency_code": "USD"},
            },
            "current_total_tax": 0.0,
            "current_total_tax_set": {
                "shop_money": {"amount": 0.0, "currency_code": "USD"},
                "presentment_money": {"amount": 0.0, "currency_code": "USD"},
            },
            "customer_locale": "en",
            "device_id": None,
            "discount_codes": [],
            "email": "integration-test@airbyte.io",
            "estimated_taxes": False,
            "financial_status": "refunded",
            "fulfillment_status": "fulfilled",
            "landing_site": "/wallets/checkouts.json",
            "landing_site_ref": None,
            "location_id": None,
            "merchant_of_record_app_id": None,
            "name": "#1136",
            "note": "updated_mon_24.04.2023",
            "note_attributes": [],
            "number": 136,
            "order_number": 1136,
            "order_status_url": "https://airbyte-integration-test.myshopify.com/58033176765/orders/e4f98630ea44a884e33e700203ce2130/authenticate?key=edf087d6ae55a4541bf1375432f6a4b8",
            "original_total_additional_fees_set": None,
            "original_total_duties_set": None,
            "payment_gateway_names": ["bogus"],
            "phone": None,
            "po_number": None,
            "presentment_currency": "USD",
            "processed_at": "2022-06-15T05:16:53-07:00",
            "reference": None,
            "referring_site": "https://airbyte-integration-test.myshopify.com/products/all-black-sneaker-right-foot",
            "source_identifier": None,
            "source_name": "web",
            "source_url": None,
            "subtotal_price": 57.23,
            "subtotal_price_set": {
                "shop_money": {"amount": 57.23, "currency_code": "USD"},
                "presentment_money": {"amount": 57.23, "currency_code": "USD"},
            },
            "tags": "Refund",
            "tax_exempt": False,
            "tax_lines": [],
            "taxes_included": True,
            "test": True,
            "token": "e4f98630ea44a884e33e700203ce2130",
            "total_discounts": 1.77,
            "total_discounts_set": {
                "shop_money": {"amount": 1.77, "currency_code": "USD"},
                "presentment_money": {"amount": 1.77, "currency_code": "USD"},
            },
            "total_line_items_price": 59.0,
            "total_line_items_price_set": {
                "shop_money": {"amount": 59.0, "currency_code": "USD"},
                "presentment_money": {"amount": 59.0, "currency_code": "USD"},
            },
            "total_outstanding": 0.0,
            "total_price": 57.23,
            "total_price_set": {
                "shop_money": {"amount": 57.23, "currency_code": "USD"},
                "presentment_money": {"amount": 57.23, "currency_code": "USD"},
            },
            "total_shipping_price_set": {
                "shop_money": {"amount": 0.0, "currency_code": "USD"},
                "presentment_money": {"amount": 0.0, "currency_code": "USD"},
            },
            "total_tax": 0.0,
            "total_tax_set": {
                "shop_money": {"amount": 0.0, "currency_code": "USD"},
                "presentment_money": {"amount": 0.0, "currency_code": "USD"},
            },
            "total_tip_received": 0.0,
            "total_weight": 0,
            "updated_at": "2023-04-24T07:00:37-07:00",
            "user_id": None,
            "billing_address": {
                "first_name": "Iryna",
                "address1": "2261 Market Street",
                "phone": None,
                "city": "San Francisco",
                "zip": "94114",
                "province": "California",
                "country": "United States",
                "last_name": "Grankova",
                "address2": "4381",
                "company": None,
                "latitude": 37.7647751,
                "longitude": -122.4320369,
                "name": "Iryna Grankova",
                "country_code": "US",
                "province_code": "CA",
            },
            "customer": {
                "id": 5362027233469,
                "email": "integration-test@airbyte.io",
                "created_at": "2021-07-08T05:41:47-07:00",
                "updated_at": "2022-06-22T03:50:13-07:00",
                "first_name": "Airbyte",
                "last_name": "Team",
                "state": "disabled",
                "note": None,
                "verified_email": True,
                "multipass_identifier": None,
                "tax_exempt": False,
                "phone": None,
                "email_marketing_consent": {"state": "not_subscribed", "opt_in_level": "single_opt_in", "consent_updated_at": None},
                "sms_marketing_consent": None,
                "tags": "",
                "currency": "USD",
                "accepts_marketing": False,
                "accepts_marketing_updated_at": None,
                "marketing_opt_in_level": "single_opt_in",
                "tax_exemptions": [],
                "admin_graphql_api_id": "gid://shopify/Customer/5362027233469",
                "default_address": {
                    "id": 7492260823229,
                    "customer_id": 5362027233469,
                    "first_name": "Airbyte",
                    "last_name": "Team",
                    "company": None,
                    "address1": "2261 Market Street",
                    "address2": "4381",
                    "city": "San Francisco",
                    "province": "California",
                    "country": "United States",
                    "zip": "94114",
                    "phone": None,
                    "name": "Airbyte Team",
                    "province_code": "CA",
                    "country_code": "US",
                    "country_name": "United States",
                    "default": True,
                },
            },
            "discount_applications": [
                {
                    "target_type": "line_item",
                    "type": "automatic",
                    "value": "3.0",
                    "value_type": "percentage",
                    "allocation_method": "across",
                    "target_selection": "all",
                    "title": "eeeee",
                }
            ],
            "fulfillments": [
                {
                    "id": 4075788501181,
                    "admin_graphql_api_id": "gid://shopify/Fulfillment/4075788501181",
                    "created_at": "2022-06-15T05:16:55-07:00",
                    "location_id": 63590301885,
                    "name": "#1136.1",
                    "order_id": 4554821468349,
                    "origin_address": {},
                    "receipt": {},
                    "service": "manual",
                    "shipment_status": None,
                    "status": "success",
                    "tracking_company": None,
                    "tracking_number": None,
                    "tracking_numbers": [],
                    "tracking_url": None,
                    "tracking_urls": [],
                    "updated_at": "2022-06-15T05:16:55-07:00",
                    "line_items": [
                        {
                            "id": 11406125564093,
                            "admin_graphql_api_id": "gid://shopify/LineItem/11406125564093",
                            "fulfillable_quantity": 0,
                            "fulfillment_service": "manual",
                            "fulfillment_status": "fulfilled",
                            "gift_card": False,
                            "grams": 0,
                            "name": "All Black Sneaker Right Foot - ivory",
                            "price": 59.0,
                            "price_set": {
                                "shop_money": {"amount": 59.0, "currency_code": "USD"},
                                "presentment_money": {"amount": 59.0, "currency_code": "USD"},
                            },
                            "product_exists": True,
                            "product_id": 6796226560189,
                            "properties": [],
                            "quantity": 1,
                            "requires_shipping": False,
                            "sku": "",
                            "taxable": True,
                            "title": "All Black Sneaker Right Foot",
                            "total_discount": 0.0,
                            "total_discount_set": {
                                "shop_money": {"amount": 0.0, "currency_code": "USD"},
                                "presentment_money": {"amount": 0.0, "currency_code": "USD"},
                            },
                            "variant_id": 40090597884093,
                            "variant_inventory_management": "shopify",
                            "variant_title": "ivory",
                            "vendor": "Becker - Moore",
                            "tax_lines": [],
                            "duties": [],
                            "discount_allocations": [
                                {
                                    "amount": "1.77",
                                    "amount_set": {
                                        "shop_money": {"amount": "1.77", "currency_code": "USD"},
                                        "presentment_money": {"amount": "1.77", "currency_code": "USD"},
                                    },
                                    "discount_application_index": 0,
                                }
                            ],
                        }
                    ],
                }
            ],
            "line_items": [
                {
                    "id": 11406125564093,
                    "admin_graphql_api_id": "gid://shopify/LineItem/11406125564093",
                    "fulfillable_quantity": 0,
                    "fulfillment_service": "manual",
                    "fulfillment_status": "fulfilled",
                    "gift_card": False,
                    "grams": 0,
                    "name": "All Black Sneaker Right Foot - ivory",
                    "price": 59.0,
                    "price_set": {
                        "shop_money": {"amount": 59.0, "currency_code": "USD"},
                        "presentment_money": {"amount": 59.0, "currency_code": "USD"},
                    },
                    "product_exists": True,
                    "product_id": 6796226560189,
                    "properties": [],
                    "quantity": 1,
                    "requires_shipping": False,
                    "sku": "",
                    "taxable": True,
                    "title": "All Black Sneaker Right Foot",
                    "total_discount": 0.0,
                    "total_discount_set": {
                        "shop_money": {"amount": 0.0, "currency_code": "USD"},
                        "presentment_money": {"amount": 0.0, "currency_code": "USD"},
                    },
                    "variant_id": 40090597884093,
                    "variant_inventory_management": "shopify",
                    "variant_title": "ivory",
                    "vendor": "Becker - Moore",
                    "tax_lines": [],
                    "duties": [],
                    "discount_allocations": [
                        {
                            "amount": "1.77",
                            "amount_set": {
                                "shop_money": {"amount": "1.77", "currency_code": "USD"},
                                "presentment_money": {"amount": "1.77", "currency_code": "USD"},
                            },
                            "discount_application_index": 0,
                        }
                    ],
                }
            ],
            "payment_terms": None,
            "refunds": [
                {
                    "id": 852809646269,
                    "admin_graphql_api_id": "gid://shopify/Refund/852809646269",
                    "created_at": "2022-06-15T06:25:43-07:00",
                    "note": None,
                    "order_id": 4554821468349,
                    "processed_at": "2022-06-15T06:25:43-07:00",
                    "restock": True,
                    "total_duties_set": {
                        "shop_money": {"amount": 0.0, "currency_code": "USD"},
                        "presentment_money": {"amount": 0.0, "currency_code": "USD"},
                    },
                    "user_id": 74861019325,
                    "order_adjustments": [],
                    "transactions": [
                        {
                            "id": 5721170968765,
                            "admin_graphql_api_id": "gid://shopify/OrderTransaction/5721170968765",
                            "amount": "57.23",
                            "authorization": None,
                            "created_at": "2022-06-15T06:25:42-07:00",
                            "currency": "USD",
                            "device_id": None,
                            "error_code": None,
                            "gateway": "bogus",
                            "kind": "refund",
                            "location_id": None,
                            "message": "Bogus Gateway: Forced success",
                            "order_id": 4554821468349,
                            "parent_id": 5721110872253,
                            "payment_id": "c25048437719229.2",
                            "processed_at": "2022-06-15T06:25:42-07:00",
                            "receipt": {"paid_amount": "57.23"},
                            "source_name": "1830279",
                            "status": "success",
                            "test": True,
                            "user_id": None,
                            "payment_details": {
                                "credit_card_bin": "1",
                                "avs_result_code": None,
                                "cvv_result_code": None,
                                "credit_card_number": "•••• •••• •••• 1",
                                "credit_card_company": "Bogus",
                                "buyer_action_info": None,
                                "credit_card_name": "Bogus Gateway",
                                "credit_card_wallet": None,
                                "credit_card_expiration_month": 2,
                                "credit_card_expiration_year": 2025,
                            },
                        }
                    ],
                    "refund_line_items": [
                        {
                            "id": 363131404477,
                            "line_item_id": 11406125564093,
                            "location_id": 63590301885,
                            "quantity": 1,
                            "restock_type": "return",
                            "subtotal": 57.23,
                            "subtotal_set": {
                                "shop_money": {"amount": "57.23", "currency_code": "USD"},
                                "presentment_money": {"amount": "57.23", "currency_code": "USD"},
                            },
                            "total_tax": 0.0,
                            "total_tax_set": {
                                "shop_money": {"amount": "0.00", "currency_code": "USD"},
                                "presentment_money": {"amount": "0.00", "currency_code": "USD"},
                            },
                            "line_item": {
                                "id": 11406125564093,
                                "admin_graphql_api_id": "gid://shopify/LineItem/11406125564093",
                                "fulfillable_quantity": 0,
                                "fulfillment_service": "manual",
                                "fulfillment_status": "fulfilled",
                                "gift_card": False,
                                "grams": 0,
                                "name": "All Black Sneaker Right Foot - ivory",
                                "price": "59.00",
                                "price_set": {
                                    "shop_money": {"amount": "59.00", "currency_code": "USD"},
                                    "presentment_money": {"amount": "59.00", "currency_code": "USD"},
                                },
                                "product_exists": True,
                                "product_id": 6796226560189,
                                "properties": [],
                                "quantity": 1,
                                "requires_shipping": False,
                                "sku": "",
                                "taxable": True,
                                "title": "All Black Sneaker Right Foot",
                                "total_discount": "0.00",
                                "total_discount_set": {
                                    "shop_money": {"amount": "0.00", "currency_code": "USD"},
                                    "presentment_money": {"amount": "0.00", "currency_code": "USD"},
                                },
                                "variant_id": 40090597884093,
                                "variant_inventory_management": "shopify",
                                "variant_title": "ivory",
                                "vendor": "Becker - Moore",
                                "tax_lines": [],
                                "duties": [],
                                "discount_allocations": [
                                    {
                                        "amount": "1.77",
                                        "amount_set": {
                                            "shop_money": {"amount": "1.77", "currency_code": "USD"},
                                            "presentment_money": {"amount": "1.77", "currency_code": "USD"},
                                        },
                                        "discount_application_index": 0,
                                    }
                                ],
                            },
                        }
                    ],
                    "duties": [],
                }
            ],
            "shipping_address": None,
            "shipping_lines": [],
            "shop_url": "airbyte-integration-test",
        }
        for _ in range(self.count):
            yield sample_record
