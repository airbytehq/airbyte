#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping, Optional


class B2BEnricher:
    """
    Utility class to enrich customer and order records with B2B-specific data.
    This class helps identify B2B customers and orders based on various signals
    and adds relevant B2B metadata to the records.
    """

    def __init__(self, config: Mapping[str, Any]):
        self.config = config
        self.company_cache: Dict[int, Dict[str, Any]] = {}
        self.company_location_cache: Dict[int, Dict[str, Any]] = {}

    def populate_company_cache(self, companies_stream):
        """
        Populate the company cache from the companies stream for B2B enrichment.
        This should be called during the sync to build a mapping of company data.
        """
        try:
            for company in companies_stream.read_records(sync_mode="full_refresh"):
                if company.get("id"):
                    self.company_cache[company["id"]] = company
        except Exception:
            # If companies stream fails or is not available, continue without B2B enrichment
            pass

    def populate_company_location_cache(self, company_locations_stream):
        """
        Populate the company location cache from the company locations stream for B2B enrichment.
        """
        try:
            for location in company_locations_stream.read_records(sync_mode="full_refresh"):
                if location.get("id"):
                    self.company_location_cache[location["id"]] = location
        except Exception:
            # If company locations stream fails or is not available, continue without B2B enrichment
            pass

    def detect_b2b_customer_signals(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect B2B signals in customer data based on various indicators.
        Returns a dictionary with B2B-related fields.
        """
        b2b_data = {
            "is_b2b_customer": False,
            "b2b_customer_type": None,
            "company_id": None,
            "company_location_id": None,
            "b2b_company_name": None,
            "b2b_payment_terms": None,
            "b2b_tax_id": None,
        }

        # Check for B2B indicators in tags
        tags = customer.get("tags", "")
        if tags:
            tags_lower = tags.lower()
            if any(tag in tags_lower for tag in ["b2b", "wholesale", "business", "company", "trade"]):
                b2b_data["is_b2b_customer"] = True
                b2b_data["b2b_customer_type"] = "business"

        # Check for company name in default address
        default_address = customer.get("default_address", {})
        if default_address and default_address.get("company"):
            b2b_data["is_b2b_customer"] = True
            b2b_data["b2b_company_name"] = default_address["company"]
            if not b2b_data["b2b_customer_type"]:
                b2b_data["b2b_customer_type"] = "business"

        # Check if customer has high order count or spending (potential wholesale indicator)
        orders_count = customer.get("orders_count", 0)
        total_spent = float(customer.get("total_spent", 0) or 0)
        
        if orders_count > 50 or total_spent > 10000:  # Configurable thresholds
            if not b2b_data["is_b2b_customer"]:
                b2b_data["is_b2b_customer"] = True
                b2b_data["b2b_customer_type"] = "high_volume"

        # Check if customer is tax exempt (common for B2B)
        if customer.get("tax_exempt"):
            b2b_data["is_b2b_customer"] = True
            if not b2b_data["b2b_customer_type"]:
                b2b_data["b2b_customer_type"] = "tax_exempt"

        return b2b_data

    def detect_b2b_order_signals(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect B2B signals in order data and enrich with B2B metadata.
        Returns a dictionary with B2B-related fields.
        """
        b2b_data = {
            "is_b2b_order": False,
            "b2b_company_id": None,
            "b2b_company_location_id": None,
            "b2b_company_name": None,
            "b2b_payment_terms": None,
            "b2b_purchase_order_number": None,
            "b2b_price_list_id": None,
            "b2b_customer_type": None,
        }

        # Check for company name in billing/shipping address
        billing_address = order.get("billing_address", {})
        shipping_address = order.get("shipping_address", {})
        
        company_name = None
        if billing_address and billing_address.get("company"):
            company_name = billing_address["company"]
        elif shipping_address and shipping_address.get("company"):
            company_name = shipping_address["company"]

        if company_name:
            b2b_data["is_b2b_order"] = True
            b2b_data["b2b_company_name"] = company_name
            b2b_data["b2b_customer_type"] = "business"

        # Check for purchase order number in note or line item properties
        note = order.get("note", "")
        if note:
            # Look for PO number patterns in notes
            if any(pattern in note.lower() for pattern in ["po:", "po#", "purchase order", "p.o."]):
                b2b_data["is_b2b_order"] = True
                # Extract potential PO number (simple regex-like extraction)
                import re
                po_match = re.search(r'(?:po[:\s#]?|purchase\s+order[:\s#]?|p\.o\.?[:\s#]?)\s*([a-zA-Z0-9\-]+)', note.lower())
                if po_match:
                    b2b_data["b2b_purchase_order_number"] = po_match.group(1)

        # Check for high order value (potential wholesale)
        total_price = float(order.get("total_price", 0) or 0)
        if total_price > 5000:  # Configurable threshold
            if not b2b_data["is_b2b_order"]:
                b2b_data["is_b2b_order"] = True
                b2b_data["b2b_customer_type"] = "high_value"

        # Check line items for bulk quantities
        line_items = order.get("line_items", [])
        if line_items:
            total_quantity = sum(int(item.get("quantity", 0)) for item in line_items)
            if total_quantity > 50:  # Configurable threshold
                b2b_data["is_b2b_order"] = True
                if not b2b_data["b2b_customer_type"]:
                    b2b_data["b2b_customer_type"] = "bulk"

        # Check for tax exemption
        if order.get("taxes_included") is False and order.get("total_tax", 0) == 0:
            b2b_data["is_b2b_order"] = True
            if not b2b_data["b2b_customer_type"]:
                b2b_data["b2b_customer_type"] = "tax_exempt"

        return b2b_data

    def enrich_customer_record(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a customer record with B2B data.
        """
        b2b_data = self.detect_b2b_customer_signals(customer)
        
        # Add B2B fields to customer record
        customer.update(b2b_data)
        
        return customer

    def enrich_order_record(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich an order record with B2B data.
        """
        b2b_data = self.detect_b2b_order_signals(order)
        
        # Add B2B fields to order record
        order.update(b2b_data)
        
        return order