#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
#
# REQUIREMENTS:
# 1. Run poetry install to instal lal lthe dependiencies
# 2. Create ../secrets/config.json with your API key for (normally starts with sk_)
# {
#   "client_secret": "<sk_test_xxxx>",
#    "account_id": "<ACCOUNT ID>",
#   ...
#    "api_key": "YOUR API KEY",
#  }
# HOW TO USE:
# python stripe_payments_gen.py --successful <#> --general_fail <#>  --no_funds_fail <#>
# example: python stripe_payments_gen.py --successful 10 --general_fail 12  --no_funds_fail 8
# The above exmaple will generate 10 successful calls, 12 general_failures and 8 no_funds_fail errors.
# The scripts shuffles the errors so they are sent arbitrary, so if you send 2 successful and 1 fail, the script may send them
# in different order: successful, failed, successful or failed, successful, successful
# These are predefined errors from  https://docs.stripe.com/testing
import argparse
import json
import random

import stripe


# Initialize Stripe API key
def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


json_secrets = read_json("../secrets/config.json")
stripe.api_key = json_secrets["api_key"]


def create_payment_intent(customer, amount, currency, payment_method_id, description, automatic_payment_methods):
    try:
        # Assuming payment_method_id is a pre-created PaymentMethod ID for the test card
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer,
            payment_method=payment_method_id,
            confirm=True,
            description=description,
            automatic_payment_methods=automatic_payment_methods,
        )
        return {"status": "succeeded", "intent": intent}
    except stripe.error.CardError as e:
        # Handle declined card error
        return {"status": "failed", "reason": e.user_message}


# Mock functions to simulate payment intent creation for different scenarios
def successful_payment():
    return create_payment_intent(
        customer="cus_PhC1WLeG23Y3c6",
        amount=2000,
        currency="usd",
        payment_method_id="pm_card_mx",  # Replace with any other PaymentMethod ID created for the test card
        description="Successful payment",
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
    )


def failed_general():
    return create_payment_intent(
        customer="cus_PhB5WHzDqnUeM6",
        amount=2000,
        currency="usd",
        payment_method_id="pm_card_visa_chargeDeclined",  # Replace with any other PaymentMethod ID created for the test card
        description="Failed general",
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
    )


def failed_no_funds():
    return create_payment_intent(
        customer="cus_PhCDqAuh1VqJWO",
        amount=2000,
        currency="usd",
        payment_method_id="pm_card_visa_chargeDeclinedInsufficientFunds",  # Replace with any other PaymentMethod ID created for the test card
        description="Failed no funds",
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
    )


# Mock functions to simulate payment intent creation for different scenarios
def always_blocked():
    return create_payment_intent(
        customer="cus_PhFrj7WCSRZM0Z",
        amount=2000,
        currency="usd",
        payment_method_id="pm_card_radarBlock",  # Replace with any other PaymentMethod ID created for the test card
        description="Blocked payment",
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
    )


# Parsing script arguments
parser = argparse.ArgumentParser(description="Generate Stripe payment intents.")
parser.add_argument("--successful", type=int, help="Number of successful payments you want to generate")
parser.add_argument("--general_fail", type=int, help="Number of general failures you want to generate")
parser.add_argument("--no_funds_fail", type=int, help="Number of no funds failures you want to generate")
parser.add_argument("--blocked_payment", type=int, help="Number of blocked attempt failures you want to generate")
args = parser.parse_args()
# Creating a shuffled list of payment intent types
payment_types = (
    ["successful"] * args.successful
    + ["general_fail"] * args.general_fail
    + ["no_funds_fail"] * args.no_funds_fail
    + ["blocked_payment"] * args.blocked_payment
)
random.shuffle(payment_types)
# Initialize a dictionary to store responses
responses = {}
# Iterating through shuffled payment types and calling respective methods
for idx, payment_type in enumerate(payment_types, start=1):
    if payment_type == "successful":
        response = successful_payment()
    elif payment_type == "general_fail":
        response = failed_general()
    elif payment_type == "general_fail":
        response = failed_no_funds()
    else:
        response = always_blocked()

    # Storing response status
    responses[idx] = {"type": payment_type, "status": response["status"]}
# Printing call statuses
for idx, info in responses.items():
    print(f"Call {idx} ({info['type']}): {info['status']}")
