#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from pytest import fixture


@fixture
def config_pass():
    return {"api_key": "test-token", "start_date": "2023-01-25T00:00:00Z"}


@fixture
def subscriptions_url():
    return "https://api.billwithorb.com/v1/subscriptions"


@fixture
def mock_subscriptions_response():
    return {
  "data": [
    {
      "metadata": {},
      "id": "string",
      "customer": {
        "metadata": {},
        "id": "string",
        "external_customer_id": "string",
        "name": "string",
        "email": "string",
        "timezone": "string",
        "payment_provider_id": "string",
        "payment_provider": "quickbooks",
        "created_at": "2024-06-21T22:27:22.230Z",
        "shipping_address": {
          "line1": "string",
          "line2": "string",
          "city": "string",
          "state": "string",
          "postal_code": "string",
          "country": "string"
        },
        "billing_address": {
          "line1": "string",
          "line2": "string",
          "city": "string",
          "state": "string",
          "postal_code": "string",
          "country": "string"
        },
        "balance": "string",
        "currency": "string",
        "tax_id": {
          "country": "AD",
          "type": "ad_nrt",
          "value": "string"
        },
        "auto_collection": True,
        "email_delivery": True,
        "additional_emails": [
          "string"
        ],
        "portal_url": "string",
        "accounting_sync_configuration": {
          "excluded": True,
          "accounting_providers": [
            {
              "provider_type": "quickbooks",
              "external_provider_id": "string"
            }
          ]
        },
        "reporting_configuration": {
          "exempt": True
        }
      },
      "plan": {
        "metadata": {},
        "id": "string",
        "name": "string",
        "description": "string",
        "maximum_amount": "string",
        "minimum_amount": "string",
        "created_at": "2024-06-21T22:27:22.233Z",
        "status": "active",
        "maximum": {
          "maximum_amount": "string",
          "applies_to_price_ids": [
            "string"
          ]
        },
        "minimum": {
          "minimum_amount": "string",
          "applies_to_price_ids": [
            "string"
          ]
        },
        "discount": {
          "discount_type": "percentage",
          "applies_to_price_ids": [
            "h74gfhdjvn7ujokd",
            "7hfgtgjnbvc3ujkl"
          ],
          "reason": "string",
          "percentage_discount": 0.15
        },
        "product": {
          "created_at": "2024-06-21T22:27:22.234Z",
          "id": "string",
          "name": "string"
        },
        "version": 0,
        "trial_config": {
          "trial_period": 0,
          "trial_period_unit": "days"
        },
        "plan_phases": [
          {
            "id": "string",
            "description": "string",
            "duration": 0,
            "duration_unit": "daily",
            "name": "string",
            "order": 0,
            "minimum": {
              "minimum_amount": "string",
              "applies_to_price_ids": [
                "string"
              ]
            },
            "maximum": {
              "maximum_amount": "string",
              "applies_to_price_ids": [
                "string"
              ]
            },
            "maximum_amount": "string",
            "minimum_amount": "string",
            "discount": {
              "discount_type": "percentage",
              "applies_to_price_ids": [
                "h74gfhdjvn7ujokd",
                "7hfgtgjnbvc3ujkl"
              ],
              "reason": "string",
              "percentage_discount": 0.15
            }
          }
        ],
        "base_plan": {
          "id": "m2t5akQeh2obwxeU",
          "external_plan_id": "m2t5akQeh2obwxeU",
          "name": "Example plan"
        },
        "base_plan_id": "string",
        "external_plan_id": "string",
        "currency": "string",
        "invoicing_currency": "string",
        "net_terms": 0,
        "default_invoice_memo": "string",
        "prices": [
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {},
          {}
        ]
      },
      "start_date": "2024-06-21T22:27:22.237Z",
      "end_date": "2024-06-21T22:27:22.237Z",
      "created_at": "2024-06-21T22:27:22.237Z",
      "current_billing_period_start_date": "2024-06-21T22:27:22.237Z",
      "current_billing_period_end_date": "2024-06-21T22:27:22.237Z",
      "status": "active",
      "trial_info": {
        "end_date": "2024-06-21T22:27:22.237Z"
      },
      "active_plan_phase_order": 0,
      "fixed_fee_quantity_schedule": [
        {
          "price_id": "string",
          "start_date": "2024-06-21T22:27:22.237Z",
          "end_date": "2024-06-21T22:27:22.237Z",
          "quantity": 0
        }
      ],
      "default_invoice_memo": "string",
      "auto_collection": True,
      "net_terms": 0,
      "redeemed_coupon": {
        "coupon_id": "string",
        "start_date": "2024-06-21T22:27:22.237Z",
        "end_date": "2024-06-21T22:27:22.237Z"
      },
      "billing_cycle_day": 0,
      "invoicing_threshold": "string",
      "price_intervals": [
        {
          "id": "string",
          "start_date": "2024-06-21T22:27:22.245Z",
          "end_date": "2024-06-21T22:27:22.245Z",
          "price": {
            "id": "string",
            "name": "string",
            "external_price_id": "string",
            "price_type": "usage_price",
            "model_type": "unit",
            "created_at": "2024-06-21T22:27:22.245Z",
            "cadence": "one_time",
            "billable_metric": {
              "id": "string"
            },
            "fixed_price_quantity": 0,
            "plan_phase_order": 0,
            "currency": "string",
            "conversion_rate": 0,
            "item": {
              "id": "string",
              "name": "string"
            },
            "credit_allocation": {
              "currency": "string",
              "allows_rollover": True
            },
            "discount": {
              "discount_type": "percentage",
              "applies_to_price_ids": [
                "h74gfhdjvn7ujokd",
                "7hfgtgjnbvc3ujkl"
              ],
              "reason": "string",
              "percentage_discount": 0.15
            },
            "minimum": {
              "minimum_amount": "string",
              "applies_to_price_ids": [
                "string"
              ]
            },
            "minimum_amount": "string",
            "maximum": {
              "maximum_amount": "string",
              "applies_to_price_ids": [
                "string"
              ]
            },
            "maximum_amount": "string",
            "unit_config": {
              "unit_amount": "string"
            }
          },
          "billing_cycle_day": 0,
          "fixed_fee_quantity_transitions": [
            {
              "price_id": "string",
              "effective_date": "2024-06-21T22:27:22.246Z",
              "quantity": 0
            }
          ],
          "current_billing_period_start_date": "2024-06-21T22:27:22.246Z",
          "current_billing_period_end_date": "2024-06-21T22:27:22.246Z"
        }
      ],
      "adjustment_intervals": [
        {
          "id": "string",
          "adjustment": {
            "applies_to_price_ids": [
              "string"
            ],
            "reason": "string",
            "adjustment_type": "amount_discount",
            "amount_discount": "string"
          },
          "start_date": "2024-06-21T22:27:22.246Z",
          "end_date": "2024-06-21T22:27:22.246Z",
          "applies_to_price_interval_ids": [
            "string"
          ]
        }
      ],
      "discount_intervals": [
        {},
        {},
        {}
      ],
      "minimum_intervals": [
        {
          "start_date": "2024-06-21T22:27:22.246Z",
          "end_date": "2024-06-21T22:27:22.246Z",
          "applies_to_price_ids": [
            "string"
          ],
          "applies_to_price_interval_ids": [
            "string"
          ],
          "minimum_amount": "string"
        }
      ],
      "maximum_intervals": [
        {
          "start_date": "2024-06-21T22:27:22.246Z",
          "end_date": "2024-06-21T22:27:22.246Z",
          "applies_to_price_ids": [
            "string"
          ],
          "applies_to_price_interval_ids": [
            "string"
          ],
          "maximum_amount": "string"
        }
      ]
    }
  ],
  "pagination_metadata": {
    "has_more": False,
  }
}
