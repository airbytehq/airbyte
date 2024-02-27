# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

# REQUIREMENTS:
# 1. Put your sandbox credentials in ../secrets/config.json (Create them if it doesn't exist).
# Use the following body (change all the values):
# {
#    "client_id": "YOUT_CLIENT_ID",
#    "client_secret": "YOUR_SECRET_CLIENT_ID",
#    "start_date": "2021-06-01T00:00:00Z",
#    "end_date":   "2024-06-10T00:00:00Z",
#    "is_sandbox": true
#  }
# How to Use:
# To Create a Draft Invoice:
# Execute the script with create_draft to generate a new invoice draft.
# The script automatically sets the invoice and due dates based on the current date and a 30-day term.
#     python invoices.py create_draft
# To Send a Draft Invoice:
# Use send_draft action along with the required --invoice_id parameter, and optional parameters for email subject, note, and additional recipients.
#     python invoices.py send_draft --invoice_id "INV2-XXXX-XXXX-XXXX-XXXX" --subject "Your Invoice Subject" --note "Your custom note" --additional_recipients example@email.com

import argparse
import base64
import json
import random
import string
from datetime import datetime, timedelta

import requests


# Function to generate a random alphanumeric string
def generate_random_string(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


# Function to get a PayPal OAuth token
def get_paypal_token(client_id, secret_id):
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{secret_id}".encode()).decode(),
    }
    payload = {"grant_type": "client_credentials"}
    response = requests.post(url=url, data=payload, headers=headers)
    return response.json().get("access_token")


# Function to create a draft invoice
def create_draft_invoice(access_token, invoice_date, term_type, due_date):
    url = "https://api-m.sandbox.paypal.com/v2/invoicing/invoices"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    data = {
        "detail": {
            "invoice_number": generate_random_string(8),
            "invoice_date": invoice_date,
            "payment_term": {"term_type": term_type, "due_date": due_date},
            "currency_code": "USD",
            "reference": "<The reference data. Includes a post office (PO) number.>",
            "note": "<A note to the invoice recipient. Also appears on the invoice notification email.>",
            "terms_and_conditions": "<The general terms of the invoice. Can include return or cancellation policy and other terms and conditions.>",
            "memo": "<A private bookkeeping note for merchant.>",
        },
        "invoicer": {
            "name": {"given_name": "David", "surname": "Larusso"},
            "address": {
                "address_line_1": "123 Townsend St",
                "address_line_2": "Floor 6",
                "admin_area_2": "San Francisco",
                "admin_area_1": "CA",
                "postal_code": "94107",
                "country_code": "US",
            },
            "phones": [{"country_code": "001", "national_number": "4085551234", "phone_type": "MOBILE"}],
            "website": "www.example.com",
            "tax_id": "XX-XXXXXXX",
            "logo_url": "https://example.com/logo.png",
            "additional_notes": "<Any additional information. Includes business hours.>",
        },
        "primary_recipients": [
            {
                "billing_info": {
                    "name": {"given_name": "Stephanie", "surname": "Meyers"},
                    "address": {
                        "address_line_1": "1234 Main Street",
                        "admin_area_2": "Anytown",
                        "admin_area_1": "CA",
                        "postal_code": "98765",
                        "country_code": "US",
                    },
                    "email_address": "foobuyer@example.com",
                    "phones": [{"country_code": "001", "national_number": "4884551234", "phone_type": "HOME"}],
                    "additional_info_value": "add-info",
                },
                "shipping_info": {
                    "name": {"given_name": "Stephanie", "surname": "Meyers"},
                    "address": {
                        "address_line_1": "1234 Main Street",
                        "admin_area_2": "Anytown",
                        "admin_area_1": "CA",
                        "postal_code": "98765",
                        "country_code": "US",
                    },
                },
            }
        ],
        "items": [
            {
                "name": "Yoga Mat",
                "description": "Elastic mat to practice yoga.",
                "quantity": "1",
                "unit_amount": {"currency_code": "USD", "value": "50.00"},
                "tax": {"name": "Sales Tax", "percent": "7.25"},
                "discount": {"percent": "5"},
                "unit_of_measure": "QUANTITY",
            },
            {
                "name": "Yoga t-shirt",
                "quantity": "1",
                "unit_amount": {"currency_code": "USD", "value": "10.00"},
                "tax": {"name": "Sales Tax", "percent": "7.25"},
                "discount": {"amount": {"currency_code": "USD", "value": "5.00"}},
                "unit_of_measure": "QUANTITY",
            },
        ],
        "configuration": {
            "partial_payment": {"allow_partial_payment": True, "minimum_amount_due": {"currency_code": "USD", "value": "20.00"}},
            "allow_tip": True,
            "tax_calculated_after_discount": True,
            "tax_inclusive": False,
        },
        "amount": {
            "breakdown": {
                "custom": {"label": "Packing Charges", "amount": {"currency_code": "USD", "value": "10.00"}},
                "shipping": {"amount": {"currency_code": "USD", "value": "10.00"}, "tax": {"name": "Sales Tax", "percent": "7.25"}},
                "discount": {"invoice_discount": {"percent": "5"}},
            }
        },
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Function to send an existing draft invoice
def send_draft_invoice(access_token, invoice_id, subject, note, additional_recipients):
    url = f"https://api-m.sandbox.paypal.com/v2/invoicing/invoices/{invoice_id}/send"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    data = {
        "subject": subject,
        "note": note,
        "send_to_recipient": True,
        "additional_recipients": additional_recipients,
        "send_to_invoicer": False,
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Main function
def main():
    parser = argparse.ArgumentParser(description="PayPal Invoice Actions")
    parser.add_argument("action", help="Action to perform: create_draft or send_draft")
    parser.add_argument("--invoice_id", help="Invoice ID (required for send_draft)")
    parser.add_argument("--subject", help="Subject for the invoice email")
    parser.add_argument("--note", help="Note for the invoice email")
    parser.add_argument("--additional_recipients", nargs="*", help="Additional recipients for the invoice email")
    args = parser.parse_args()

    CREDS = read_json("../secrets/config.json")

    client_id = CREDS.get("client_id")
    secret_id = CREDS.get("client_secret")
    access_token = get_paypal_token(client_id, secret_id)

    if args.action == "create_draft":
        invoice_date = datetime.now().strftime("%Y-%m-%d")
        term_type = "NET_30"
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        result = create_draft_invoice(access_token, invoice_date, term_type, due_date)
        print("Draft Invoice Created:", result)
    elif args.action == "send_draft":
        if not args.invoice_id:
            print("Invoice ID is required for sending a draft invoice.")
            return
        result = send_draft_invoice(access_token, args.invoice_id, args.subject, args.note, args.additional_recipients)
        print("Draft Invoice Sent:", result)
    else:
        print("Invalid action specified")


if __name__ == "__main__":
    main()
