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
# python product_catalog.py
# NOTE: This is version one, it conly creates 1 product at a time. This has not been parametrized
# TODO: Generate N products in one run.

import requests
import random
import string
import base64
import json

def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())

def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def get_paypal_token(client_id, secret_id):
    """Get a bearer token from PayPal."""
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{secret_id}".encode()).decode()
    }
    payload = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url=url, data=payload, headers=headers)
    return response.json().get('access_token')

def create_paypal_product(access_token):
    """Create a product in PayPal."""
    url = "https://api-m.sandbox.paypal.com/v1/catalogs/products"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "name": "Pines-T-Shirt-" + generate_random_string(5),
        "type": "PHYSICAL",
        "id": generate_random_string(10),
        "description": "Cotton XL",
        "category": "CLOTHING",
        "image_url": "https://example.com/gallary/images/" + generate_random_string(10) + ".jpg",
        "home_url": "https://example.com/catalog/" + generate_random_string(10) + ".jpg"
    }
    response = requests.post(url=url, json=payload, headers=headers)
    return response.json()
# Replace with your actual client_id and secret_id from PayPal

CREDS = read_json("../secrets/config.json")

client_id = CREDS.get("client_id")
secret_id = CREDS.get("client_secret")

# Get the access token
access_token = get_paypal_token(client_id, secret_id)
# Create a product using the access token

product = create_paypal_product(access_token)
print(product)

