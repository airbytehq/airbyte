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
# To update an existing dispute:
#    python disputes_generator.py update DISPUTE_ID ''[{"op": "replace", "path": "/reason", "value": "The new reason"}]'
# To update a dispute status
# python update_dispute.py require-evidence DISPUTE_ID SELLER_EVIDENCE

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


def update_dispute(token, dispute_id, updates):
    """Update a PayPal dispute."""
    url = f"https://api-m.paypal.com/v1/customer/disputes/{dispute_id}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.patch(url, headers=headers, json=updates)
    print("RESPONSE: ", response.text)
    return response.json()


def require_evidence(token, dispute_id, action):
    """Require evidence for a PayPal dispute."""
    url = f"https://api-m.paypal.com/v1/customer/disputes/{dispute_id}/require-evidence"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"action": action}
    response = requests.post(url, headers=headers, json=payload)
    print("RESPONSE: ", response.text)
    return response.json()


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def main():

    operation = sys.argv[1]

    CREDS = read_json("../secrets/config.json")
    client_id = CREDS.get("client_id")
    secret_id = CREDS.get("client_secret")
    token = get_paypal_token(client_id, secret_id)

    if operation == "update":
        dispute_id = sys.argv[2]
        updates = json.loads(sys.argv[3])  # Expecting JSON string as the third argument
        update_response = update_dispute(token, dispute_id, updates)
        print("Update Response:", update_response)

    elif sys.argv[1] == "require-evidence":
        dispute_id = sys.argv[2]
        action = sys.argv[3]  # Either 'BUYER_EVIDENCE' or 'SELLER_EVIDENCE'
        evidence_response = require_evidence(token, dispute_id, action)
        print("Evidence Requirement Response:", evidence_response)
    else:
        print("Invalid command. Use 'create', 'update', or 'require-evidence'.")


if __name__ == "__main__":
    main()
