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

# HOW TO USE:
# To create a new payment: python script_name.py create
# To update an existing product:
#    python script_name.py update PAYMENT_ID '[{"op": "replace", "path": "/transactions/0/amount", "value": {"total": "50.00", "currency": "USD"}}]'
#
# NOTE: This is version does not work for CREATE PAYMENT as the HEADER requires data I can't get
#
# You may need to add a security context, but you need the proper set of permissions in your account to be able to send this context
# security_context = '{"actor":{"account_number":"<ACCOUNT_ID>","party_id":"<PARTY_ID>","auth_claims":["AUTHORIZATION_CODE"],"auth_state":"ANONYMOUS","client_id":"zf3..4BQ0T9aw-ngFr9dm....Zx9D-Lf4"},"auth_token":"<YOUR_TOKEN>","auth_token_type":"ACCESS_TOKEN","last_validated":1393560555,"scopes":["https://api-m.sandbox.paypal.com/v1/payments/.*","https://api-m.sandbox.paypal.com/v1/vault/credit-card/.*","openid","https://uri.paypal.com/services/payments/futurepayments","https://api-m.sandbox.paypal.com/v1/vault/credit-card","https://api-m.sandbox.paypal.com/v1/payments/.*"],"subjects":[{"subject":{"account_number":"<ACCOUNT_ID>","party_id":"<PARTY_ID>","auth_claims":["PASSWORD"],"auth_state":"LOGGEDIN"}}]}'


import base64
import json
import sys

import requests


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


def create_payment(token, security_context):
    """Create a PayPal payment."""
    url = "https://api-m.paypal.com/v1/payments/payment"
    headers = {
        "Content-Type": "application/json",
        # "Authorization": f"Bearer {token}",
        "X-PAYPAL-SECURITY-CONTEXT": security_context,
    }
    payload = {
        "intent": "sale",
        "transactions": [
            {
                "amount": {"total": "30.00", "currency": "USD", "details": {"subtotal": "30.00"}},
                "description": "This is a test - Pines test.",
                "item_list": {
                    "items": [{"name": "My item", "sku": "123445667", "price": "15.00", "currency": "USD", "quantity": 2}],
                },
            }
        ],
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {"return_url": "https://example.com/return", "cancel_url": "https://example.com/cancel"},
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def update_payment(token, payment_id, updates):
    """Update a PayPal payment."""
    url = f"https://api-m.paypal.com/v1/payments/payment/{payment_id}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.patch(url, headers=headers, json=updates)
    return response.json()


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def main():

    CREDS = read_json("../secrets/config.json")
    client_id = CREDS.get("client_id")
    secret_id = CREDS.get("client_secret")
    token = get_paypal_token(client_id, secret_id)

    if sys.argv[1] == "create":
        payment = create_payment(token, security_context)
        print("Created Payment:", payment)

    elif sys.argv[1] == "update":
        payment_id = sys.argv[2]
        updates = json.loads(sys.argv[3])  # Expecting JSON string as the third argument
        update_response = update_payment(token, payment_id, updates)
        print("Update Response:", update_response)

    else:
        print("Invalid command. Use 'create' or 'update'.")


if __name__ == "__main__":
    main()
