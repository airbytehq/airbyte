#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_shopify.b2b_utils import B2BEnricher


class TestB2BEnricher:
    def test_detect_b2b_customer_with_company_contact_profiles(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "email": "buyer@company.com",
            "companyContactProfiles": [
                {
                    "isMainContact": True,
                    "company": {
                        "id": "gid://shopify/Company/456",
                        "name": "Acme Corporation"
                    },
                    "roleAssignments": [
                        {
                            "location": {
                                "id": "gid://shopify/CompanyLocation/789"
                            }
                        }
                    ]
                }
            ]
        }
        
        b2b_data = enricher.detect_b2b_customer(customer)
        
        assert b2b_data["is_b2b_customer"] is True
        assert b2b_data["b2b_customer_type"] == "business"
        assert b2b_data["company_id"] == "gid://shopify/Company/456"
        assert b2b_data["b2b_company_name"] == "Acme Corporation"
        assert b2b_data["company_location_id"] == "gid://shopify/CompanyLocation/789"
        assert b2b_data["is_main_contact"] is True

    def test_detect_b2b_customer_not_main_contact(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "companyContactProfiles": [
                {
                    "isMainContact": False,
                    "company": {
                        "id": "gid://shopify/Company/456",
                        "name": "Business Inc"
                    }
                }
            ]
        }
        
        b2b_data = enricher.detect_b2b_customer(customer)
        
        assert b2b_data["is_b2b_customer"] is True
        assert b2b_data["is_main_contact"] is False
        assert b2b_data["b2b_company_name"] == "Business Inc"

    def test_detect_b2b_order_with_po_number(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "poNumber": "PO-12345",
            "paymentTerms": "Net 30",
            "total_price": "2500.00"
        }
        
        b2b_data = enricher.detect_b2b_order(order)
        
        assert b2b_data["is_b2b_order"] is True
        assert b2b_data["b2b_purchase_order_number"] == "PO-12345"
        assert b2b_data["b2b_payment_terms"] == "Net 30"
        assert b2b_data["b2b_customer_type"] == "business"

    def test_detect_b2b_order_with_purchasing_entity(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "purchasingEntity": {
                "company": {
                    "id": "gid://shopify/Company/789",
                    "name": "Enterprise Corp"
                },
                "location": {
                    "id": "gid://shopify/CompanyLocation/101"
                }
            }
        }
        
        b2b_data = enricher.detect_b2b_order(order)
        
        assert b2b_data["is_b2b_order"] is True
        assert b2b_data["b2b_company_id"] == "gid://shopify/Company/789"
        assert b2b_data["b2b_company_name"] == "Enterprise Corp"
        assert b2b_data["b2b_company_location_id"] == "gid://shopify/CompanyLocation/101"

    def test_detect_b2b_order_with_payment_terms_only(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "paymentTerms": "Net 15",
            "total_price": "1500.00"
        }
        
        b2b_data = enricher.detect_b2b_order(order)
        
        assert b2b_data["is_b2b_order"] is True
        assert b2b_data["b2b_payment_terms"] == "Net 15"
        assert b2b_data["b2b_customer_type"] == "business"

    def test_enrich_customer_record_with_company_profile(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "email": "buyer@company.com",
            "companyContactProfiles": [
                {
                    "isMainContact": True,
                    "company": {
                        "id": "gid://shopify/Company/456",
                        "name": "Test Company"
                    }
                }
            ]
        }
        
        enriched_customer = enricher.enrich_customer_record(customer)
        
        assert enriched_customer["is_b2b_customer"] is True
        assert enriched_customer["b2b_company_name"] == "Test Company"
        assert enriched_customer["email"] == "buyer@company.com"  # Original fields preserved

    def test_enrich_order_record_with_b2b_fields(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "customer_id": 123,
            "poNumber": "B2B-789",
            "paymentTerms": "Net 45"
        }
        
        enriched_order = enricher.enrich_order_record(order)
        
        assert enriched_order["is_b2b_order"] is True
        assert enriched_order["b2b_purchase_order_number"] == "B2B-789"
        assert enriched_order["b2b_payment_terms"] == "Net 45"
        assert enriched_order["customer_id"] == 123  # Original fields preserved

    def test_no_b2b_signals_customer(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "email": "john@personal.com",
            "orders_count": 2,
            "total_spent": "150.00"
        }
        
        b2b_data = enricher.detect_b2b_customer(customer)
        
        assert b2b_data["is_b2b_customer"] is False
        assert b2b_data["b2b_customer_type"] is None
        assert b2b_data["company_id"] is None

    def test_no_b2b_signals_order(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "total_price": "75.00",
            "customer_id": 123
        }
        
        b2b_data = enricher.detect_b2b_order(order)
        
        assert b2b_data["is_b2b_order"] is False
        assert b2b_data["b2b_customer_type"] is None
        assert b2b_data["b2b_purchase_order_number"] is None

    def test_customer_with_empty_company_contact_profiles(self):
        config = {}
        enricher = B2BEnricher(config)
        
        customer = {
            "id": 123,
            "companyContactProfiles": []
        }
        
        b2b_data = enricher.detect_b2b_customer(customer)
        
        assert b2b_data["is_b2b_customer"] is False

    def test_order_with_empty_purchasing_entity(self):
        config = {}
        enricher = B2BEnricher(config)
        
        order = {
            "id": 456,
            "purchasingEntity": {}
        }
        
        b2b_data = enricher.detect_b2b_order(order)
        
        assert b2b_data["is_b2b_order"] is True  # Still B2B because purchasing_entity exists
        assert b2b_data["b2b_company_id"] is None