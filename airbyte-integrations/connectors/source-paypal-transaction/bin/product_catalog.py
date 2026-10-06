# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

#
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
# To create a new product:
#    python product_catalog.py --action create --description "This is a test product" --category TRAVEL
# To update an existing product:
#    python product_catalog.py --action update --product_id PRODUCT_ID --update_payload '[{"op": "replace", "path": "/description", "value": "My Update. Does it changes it?"}]'
# The CATEGORY must be one of the listed in this page: https://developer.paypal.com/docs/api/catalog-products/v1/#products_create
# NOTE: This is version one, it conly creates 1 product at a time. This has not been parametrized
# TODO: Generate N products in one run.

import argparse
import base64
import json
import random
import string

import requests


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def get_paypal_token(client_id, secret_id):
    """Get a bearer token from PayPal."""
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{secret_id}".encode()).decode(),
    }
    payload = {"grant_type": "client_credentials"}
    response = requests.post(url=url, data=payload, headers=headers)
    return response.json().get("access_token")


def create_paypal_product(access_token, description="Cotton XL", category="clothing"):
    """Create a product in PayPal."""
    url = "https://api-m.sandbox.paypal.com/v1/catalogs/products"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    payload = {
        "name": "Pines-T-Shirt-" + generate_random_string(5),
        "type": "PHYSICAL",
        "id": generate_random_string(10),
        "description": description,
        "category": category,
        "image_url": "https://example.com/gallary/images/" + generate_random_string(10) + ".jpg",
        "home_url": "https://example.com/catalog/" + generate_random_string(10) + ".jpg",
    }
    response = requests.post(url=url, json=payload, headers=headers)
    return response.json()


def update_paypal_product(access_token, product_id, updates):
    """Update a product in PayPal."""
    url = f"https://api-m.sandbox.paypal.com/v1/catalogs/products/{product_id}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.patch(url=url, json=updates, headers=headers)
    if response.status_code == 204:
        print(f"Update Successful. Response {response.status_code}. This succesful repsonse has no response body")
        return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


# Parse command line arguments
parser = argparse.ArgumentParser(description="Create or Update a PayPal Product.")
parser.add_argument("--action", choices=["create", "update"], required=True, help="Action to perform: create or update")
parser.add_argument("--description", help="Product description for create action", required=True)
parser.add_argument("--category", help="Product category for create action", required=True)
parser.add_argument("--product_id", help="Product ID for update action", required=True)
parser.add_argument("--update_payload", help="Operation for update action", required=True)

args = parser.parse_args()

# Common setup
CREDS = read_json("../secrets/config.json")
client_id = CREDS.get("client_id")
secret_id = CREDS.get("client_secret")
access_token = get_paypal_token(client_id, secret_id)

# Perform action based on arguments
if args.action == "create":
    product = create_paypal_product(access_token, args.description, args.category)
    print("Created product:", product)
elif args.action == "update" and args.product_id and args.update_payload:
    try:
        # updates = [{"op": "replace", "path": "/description", "value": "My Update. Does it changes it?"}]
        operations = json.loads(args.update_payload)
        product = update_paypal_product(access_token, args.product_id, operations)
        print("Updated product:", product)
    except json.JSONDecodeError:
        print(f"Invalid JSON in update payload")
else:
    print("Invalid arguments")
