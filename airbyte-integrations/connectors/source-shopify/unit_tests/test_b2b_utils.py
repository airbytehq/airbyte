#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_shopify.b2b_utils import B2BEnricher


class TestB2BEnricher:
    def test_detect_b2b_customer_with_tags(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "tags": "wholesale, b2b-customer",
            "orders_count": 5,
            "total_spent": "1000.00"
        }
        
        b2b_data = enricher.detect_b2b_customer_signals(customer)
        
        assert b2b_data["is_b2b_customer"] is True
        assert b2b_data["b2b_customer_type"] == "business"

    def test_detect_b2b_customer_with_company_address(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "default_address": {
                "company": "Acme Corp",
                "address1": "123 Business St"
            },
            "orders_count": 5,
            "total_spent": "1000.00"
        }
        
        b2b_data = enricher.detect_b2b_customer_signals(customer)
        
        assert b2b_data["is_b2b_customer"] is True
        assert b2b_data["b2b_company_name"] == "Acme Corp"
        assert b2b_data["b2b_customer_type"] == "business"

    def test_detect_b2b_customer_high_volume(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "orders_count": 75,
            "total_spent": "15000.00"
        }
        
        b2b_data = enricher.detect_b2b_customer_signals(customer)
        
        assert b2b_data["is_b2b_customer"] is True
        assert b2b_data["b2b_customer_type"] == "high_volume"

    def test_detect_b2b_customer_tax_exempt(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "tax_exempt": True,
            "orders_count": 5,
            "total_spent": "1000.00"
        }
        
        b2b_data = enricher.detect_b2b_customer_signals(customer)
        
        assert b2b_data["is_b2b_customer"] is True
        assert b2b_data["b2b_customer_type"] == "tax_exempt"

    def test_detect_b2b_order_with_company_address(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "billing_address": {
                "company": "Wholesale Inc",
                "address1": "456 Commerce Ave"
            },
            "total_price": "2500.00"
        }
        
        b2b_data = enricher.detect_b2b_order_signals(order)
        
        assert b2b_data["is_b2b_order"] is True
        assert b2b_data["b2b_company_name"] == "Wholesale Inc"
        assert b2b_data["b2b_customer_type"] == "business"

    def test_detect_b2b_order_with_purchase_order(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "note": "Purchase Order: PO-12345",
            "total_price": "1500.00"
        }
        
        b2b_data = enricher.detect_b2b_order_signals(order)
        
        assert b2b_data["is_b2b_order"] is True
        assert b2b_data["b2b_purchase_order_number"] == "po-12345"

    def test_detect_b2b_order_high_value(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "total_price": "7500.00"
        }
        
        b2b_data = enricher.detect_b2b_order_signals(order)
        
        assert b2b_data["is_b2b_order"] is True
        assert b2b_data["b2b_customer_type"] == "high_value"

    def test_detect_b2b_order_bulk_quantities(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "line_items": [
                {"quantity": 30},
                {"quantity": 25}
            ],
            "total_price": "1500.00"
        }
        
        b2b_data = enricher.detect_b2b_order_signals(order)
        
        assert b2b_data["is_b2b_order"] is True
        assert b2b_data["b2b_customer_type"] == "bulk"

    def test_enrich_customer_record(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "email": "buyer@company.com",
            "tags": "wholesale",
            "orders_count": 10,
            "total_spent": "5000.00"
        }
        
        enriched_customer = enricher.enrich_customer_record(customer)
        
        assert enriched_customer["is_b2b_customer"] is True
        assert enriched_customer["b2b_customer_type"] == "business"
        assert enriched_customer["email"] == "buyer@company.com"  # Original fields preserved

    def test_enrich_order_record(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "customer_id": 123,
            "billing_address": {
                "company": "Enterprise Solutions"
            },
            "total_price": "3000.00"
        }
        
        enriched_order = enricher.enrich_order_record(order)
        
        assert enriched_order["is_b2b_order"] is True
        assert enriched_order["b2b_company_name"] == "Enterprise Solutions"
        assert enriched_order["customer_id"] == 123  # Original fields preserved

    def test_no_b2b_signals_customer(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "orders_count": 2,
            "total_spent": "150.00"
        }
        
        b2b_data = enricher.detect_b2b_customer_signals(customer)
        
        assert b2b_data["is_b2b_customer"] is False
        assert b2b_data["b2b_customer_type"] is None

    def test_no_b2b_signals_order(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "total_price": "75.00",
            "line_items": [{"quantity": 1}]
        }
        
        b2b_data = enricher.detect_b2b_order_signals(order)
        
        assert b2b_data["is_b2b_order"] is False
        assert b2b_data["b2b_customer_type"] is None