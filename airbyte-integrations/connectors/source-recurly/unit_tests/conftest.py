#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from pytest import fixture


@fixture
def config_pass():
    return {
        "api_key": "abcd1234"
    }


@fixture
def incremental_config_pass():
    return {
        "api_key": "abcd1234",
        "begin_time": "2024-01-10T00:00:00Z",
        "end_time": "2024-07-01T23:59:59Z"
    }


@fixture
def accounts_url():
    return "https://v3.recurly.com/accounts"


@fixture
def account_coupon_redemptions_url():
    return "https://v3.recurly.com/accounts/abc/coupon_redemptions"


@fixture
def account_notes_url():
    return "https://v3.recurly.com/accounts/abc/notes"


@fixture
def coupons_url():
    return "https://v3.recurly.com/coupons"


@fixture
def mock_accounts_response():
    return {
        "data": [
            {"address": {"street1": "", "street2": "", "city": "", "region": "", "postal_code": "", "country": "", "phone": ""},
             "bill_to": "self",
             "billing_info": {"id": "abcdef", "object": "billing_info", "account_id": "abc", "primary_payment_method": True,
                              "backup_payment_method": False, "first_name": "test_user", "last_name": "", "company": "",
                              "address": {"street1": "lorem ipsum", "street2": "", "city": "lorem ipsum", "region": "lorem ipsum",
                                          "postal_code": "85475", "country": "US", "phone": ""}, "vat_number": "", "valid": True,
                              "payment_method": {"object": "credit_card", "card_type": "Visa", "first_six": "400000", "last_four": "2024",
                                                 "cc_bin_country": None, "exp_month": 11, "exp_year": 2020,
                                                 "card_network_preference": None}, "created_at": "2024-04-20T15:52:10Z",
                              "updated_at": "2024-04-20T15:52:10Z", "updated_by": {"ip": None, "country": None}, "fraud": None},
             "cc_emails": "", "code": "test-account1", "company": "", "created_at": "2024-04-20T03:42:49Z", "custom_fields": [],
             "deleted_at": None, "dunning_campaign_id": None, "email": "", "exemption_certificate": None, "external_accounts": [],
             "first_name": "test_user", "has_active_subscription": False, "has_canceled_subscription": False,
             "has_future_subscription": False,
             "has_live_subscription": False, "has_past_due_invoice": False, "has_paused_subscription": False, "id": "abc",
             "last_name": "", "object": "account", "parent_account_id": None, "preferred_locale": "", "preferred_time_zone": None,
             "shipping_addresses": [{"object": "shipping_address", "first_name": "Test", "last_name": "Name", "company": "", "phone": "",
                                     "street1": "first street", "street2": "", "city": "Montana City", "region": "", "postal_code": "58745",
                                     "country": "US", "nickname": "Test Name", "email": "", "vat_number": "", "id": "nwnsbcqp9u6c",
                                     "account_id": "abc", "created_at": "2024-04-20T15:15:04Z",
                                     "updated_at": "2024-04-20T15:15:04Z"}], "state": "active", "tax_exempt": False,
             "updated_at": "2024-04-20T15:52:10Z", "username": "test_user", "vat_number": "", "invoice_template_id": None,
             "override_business_entity_id": None}
        ],
        "has_more": False,
    }


@fixture
def mock_account_coupon_redemptions_response():
    return {
        "data": [
            {"id": "abcde", "object": "coupon_redemption",
             "account": {"id": "abc", "object": "account", "code": "test-account-2", "email": "", "first_name": "test",
                         "last_name": "user", "company": "", "parent_account_id": None, "bill_to": "self", "dunning_campaign_id": None},
             "subscription_id": None,
             "coupon": {"id": "abcdef", "object": "coupon", "code": "aaja1xpwrotu", "name": "Integration Coupon test number 1",
                        "state": "redeemable", "max_redemptions": None, "max_redemptions_per_account": None, "duration": "forever",
                        "temporal_unit": None, "temporal_amount": None, "applies_to_all_plans": True, "applies_to_all_items": False,
                        "applies_to_non_plan_charges": False, "redemption_resource": "Account",
                        "discount": {"type": "percent", "percent": 97}, "coupon_type": "single_code", "hosted_page_description": None,
                        "invoice_description": None, "unique_coupon_codes_count": 0, "unique_code_template": None,
                        "unique_coupon_code": None, "plans": None, "items": None, "redeem_by": None, "created_at": "2024-04-24T12:14:40Z",
                        "updated_at": "2024-04-23T02:51:38Z", "expired_at": None}, "state": "inactive", "currency": "USD",
             "discounted": 0.0, "created_at": "2024-04-23T02:51:32Z", "updated_at": "2024-04-23T02:51:39Z",
             "removed_at": "2024-04-23T02:51:39Z"}
        ],
        "has_more": False,
    }


@fixture
def mock_account_notes_response():
    return {
        "data": [
            {"id": "abc", "object": "account_note", "account_id": "abc",
             "user": {"id": "abcde", "object": "user", "email": "integration-test@airbyte.io", "first_name": "Team",
                      "last_name": "Airbyte", "time_zone": None, "created_at": "2024-04-21T04:05:42Z", "deleted_at": None},
             "message": "This is a second test note because two notes is better than one.", "created_at": "2024-04-21T20:42:25Z"}
        ],
        "has_more": False,
    }


@fixture
def mock_coupons_response():
    return {
        "data": [
            {"id": "efg", "object": "coupon", "code": "81818asdasd", "name": "third coupon", "state": "redeemable",
             "max_redemptions": None, "max_redemptions_per_account": None, "duration": "forever", "temporal_unit": None,
             "temporal_amount": None, "applies_to_all_plans": True, "applies_to_all_items": False, "applies_to_non_plan_charges": False,
             "redemption_resource": "Account", "discount": {"type": "percent", "percent": 12}, "coupon_type": "single_code",
             "hosted_page_description": None, "invoice_description": None, "unique_coupon_codes_count": 0, "unique_code_template": None,
             "unique_coupon_code": None, "plans": None, "items": None, "redeem_by": None, "created_at": "2024-04-24T11:55:23Z",
             "updated_at": "2024-04-24T11:55:23Z", "expired_at": None}
        ],
        "has_more": False,
    }
