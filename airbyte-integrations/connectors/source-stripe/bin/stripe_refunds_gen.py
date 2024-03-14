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
# python stripe_refunds_gen.py --action create --amount <AMOUNT>
# The above example will generate a new successful payment intent and then use the payment_intent id to
# generate a refund. The response with the refund id (re_XXX) and the payment Intnet for reference (pi_xxxx)
# Then you cna generate an update if you want
# python stripe_refunds_gen.py --action update --refund_id <REFUND ID> --metadata '{"key":"value"}'
# Example: python stripe_refunds_gen.py --action update --refund_id re_3Ou200D04sfdfewzk0ED2cWWb --metadata '{"amount":"500"}'
# It will return de refund id: Refund updated: re_XXXXX
# These are predefined errors from  https://docs.stripe.com/testing

import argparse
import json

import stripe


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


json_secrets = read_json("../secrets/config.json")

stripe.api_key = json_secrets["api_key"]


def create_payment_intent(amount):
    """Create a successful payment intent and return its ID."""
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        payment_method_types=["card"],
        confirm=True,
        payment_method="pm_card_visa",  # This is a test card id in https://docs.stripe.com/testing
    )
    return payment_intent.id


def create_refund(payment_intent_id, amount):
    """Create a refund for a given PaymentIntent and amount."""
    refund = stripe.Refund.create(payment_intent=payment_intent_id, amount=amount)
    return refund


def update_refund(refund_id, metadata):
    """Update a refund with additional metadata."""
    updated_refund = stripe.Refund.modify(refund_id, metadata=metadata)
    return updated_refund


def main():
    parser = argparse.ArgumentParser(description="Stripe Refund Creation and Update Tool")
    parser.add_argument("--action", choices=["create", "update"], required=True, help="Specify whether to create or update a refund")
    parser.add_argument("--amount", type=int, help="Refund amount in cents (only required for create)")
    parser.add_argument("--refund_id", type=str, help="Refund ID for updating (required for update)")
    parser.add_argument("--metadata", type=json.loads, help="Metadata for refund update as a JSON string (required for update)")

    args = parser.parse_args()

    if args.action == "create":
        payment_intent_id = create_payment_intent(args.amount)
        refund = create_refund(payment_intent_id, args.amount)
        print(f"Refund created: {refund.id}, payment_intent: {refund.payment_intent}")

    elif args.action == "update":
        updated_refund = update_refund(args.refund_id, args.metadata)
        print(f"Refund updated: {updated_refund.id}")


if __name__ == "__main__":
    main()
