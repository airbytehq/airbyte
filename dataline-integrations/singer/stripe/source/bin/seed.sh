#!/usr/bin/env bash

set -e

[ -z "$STRIPE_KEY" ] && { echo "Need to set STRIPE_KEY"; exit 1; }

curl https://api.stripe.com/v1/customers \
  -u $STRIPE_KEY: \
  -d description="Customer 1" \
  -d email="customer1@test.com" \
  -d phone="111-111-1111"

curl https://api.stripe.com/v1/customers \
  -u $STRIPE_KEY: \
  -d description="Customer 2" \
  -d email="customer2@test.com" \
  -d phone="222-222-2222"

curl https://api.stripe.com/v1/customers \
  -u $STRIPE_KEY: \
  -d description="Customer 3" \
  -d email="customer3@test.com" \
  -d phone="333-333-3333"

curl https://api.stripe.com/v1/customers \
  -u $STRIPE_KEY: \
  -d description="Customer 4" \
  -d email="customer4@test.com" \
  -d phone="444-444-4444" \
  -d name="Name Four"
