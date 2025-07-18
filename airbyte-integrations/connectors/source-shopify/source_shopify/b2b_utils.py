#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping

__all__ = ["B2BEnricher"]


class B2BEnricher:
    """
    Utility class to enrich customer and order records with B2B-specific data.
    Uses Shopify's direct B2B relationships via companyContactProfiles and order B2B fields.
    """

    def __init__(self, config: Mapping[str, Any]):
        self.config = config

    def detect_b2b_customer(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect B2B customer using Shopify's direct companyContactProfiles relationship.
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
            "is_main_contact": None,
        }

        # Check for direct company relationship via companyContactProfiles
        company_contact_profiles = customer.get("companyContactProfiles", [])
        if company_contact_profiles:
            b2b_data["is_b2b_customer"] = True
            b2b_data["b2b_customer_type"] = "business"
            
            # Get the first (primary) company contact profile
            primary_contact = company_contact_profiles[0]
            b2b_data["is_main_contact"] = primary_contact.get("isMainContact", False)
            
            # Extract company information
            company = primary_contact.get("company", {})
            if company:
                b2b_data["company_id"] = company.get("id")
                b2b_data["b2b_company_name"] = company.get("name")
            
            # Extract role and location information if available
            role_assignments = primary_contact.get("roleAssignments", [])
            if role_assignments:
                # Get company location from role assignment
                location = role_assignments[0].get("location", {})
                if location:
                    b2b_data["company_location_id"] = location.get("id")

        return b2b_data

    def detect_b2b_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect B2B order using Shopify's direct B2B fields and customer relationship.
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

        # Check for direct B2B fields in order
        po_number = order.get("poNumber")
        payment_terms = order.get("paymentTerms")
        purchasing_entity = order.get("purchasingEntity")

        # If order has B2B-specific fields, it's a B2B order
        # Note: purchasingEntity presence (even if empty) indicates B2B context
        if po_number or payment_terms or purchasing_entity is not None:
            b2b_data["is_b2b_order"] = True
            b2b_data["b2b_purchase_order_number"] = po_number
            b2b_data["b2b_payment_terms"] = payment_terms
            b2b_data["b2b_customer_type"] = "business"

        # Extract company information from purchasing entity if available
        if purchasing_entity:
            # purchasing_entity is a union type that could contain company info
            if isinstance(purchasing_entity, dict):
                company = purchasing_entity.get("company")
                if company:
                    b2b_data["b2b_company_id"] = company.get("id")
                    b2b_data["b2b_company_name"] = company.get("name")
                
                location = purchasing_entity.get("location")
                if location:
                    b2b_data["b2b_company_location_id"] = location.get("id")

        return b2b_data

    def enrich_customer_record(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a customer record with B2B data using direct Shopify relationships.
        """
        b2b_data = self.detect_b2b_customer(customer)
        
        # Add B2B fields to customer record
        customer.update(b2b_data)
        
        return customer

    def enrich_order_record(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich an order record with B2B data using direct Shopify B2B fields.
        """
        b2b_data = self.detect_b2b_order(order)
        
        # Add B2B fields to order record
        order.update(b2b_data)
        
        return order