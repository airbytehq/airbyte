#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pendulum
from destination_heap_analytics.utils import parse_aap_json, parse_aup_json, parse_event_json, parse_property_json

user = {
    "blocked": False,
    "created_at": "2022-10-21T04:08:58.994Z",
    "email": "beryl_becker95@yahoo.com",
    "email_verified": False,
    "family_name": "Blanda",
    "given_name": "Bradly",
    "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
}


class TestParsePropertyJson:
    data = {
        "user_id": "4ce74b28-bc00-4bbf-8a01-712dae975291",
        "connection": "Username-Password-Authentication",
        "provider": "auth0",
        "isSocial": False,
    }

    def test_parse_all_properties(self):
        columns = "*".split(",")
        assert parse_property_json(data=self.data, property_columns=columns) == self.data

    def test_parse_selective_properties(self):
        columns = "user_id,provider,isSocial".split(",")
        assert parse_property_json(data=self.data, property_columns=columns) == {
            "user_id": "4ce74b28-bc00-4bbf-8a01-712dae975291",
            "provider": "auth0",
            "isSocial": False,
        }

    def test_parse_missing_properties(self):
        columns = "uSeR_iD,identity_provider,isAuthenticated".split(",")
        assert parse_property_json(data=self.data, property_columns=columns) == {}


class TestParseEventJson:
    def test_parse_all_properties(self):
        columns = "*".split(",")
        assert parse_event_json(
            data=user, property_columns=columns, event_column="family_name", identity_column="email", timestamp_column="created_at"
        ) == {
            "event": "Blanda",
            "identity": "beryl_becker95@yahoo.com",
            "properties": {
                "blocked": False,
                "created_at": "2022-10-21T04:08:58.994Z",
                "email": "beryl_becker95@yahoo.com",
                "email_verified": False,
                "family_name": "Blanda",
                "given_name": "Bradly",
                "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            },
            "timestamp": "2022-10-21T04:08:58.994Z",
        }

    def test_parse_selective_properties(self):
        columns = "blocked,email,created_at,user_id".split(",")
        assert parse_event_json(
            data=user, property_columns=columns, event_column="family_name", identity_column="email", timestamp_column="created_at"
        ) == {
            "event": "Blanda",
            "identity": "beryl_becker95@yahoo.com",
            "properties": {
                "blocked": False,
                "created_at": "2022-10-21T04:08:58.994Z",
                "email": "beryl_becker95@yahoo.com",
                "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            },
            "timestamp": "2022-10-21T04:08:58.994Z",
        }

    def test_parse_missing_properties(self):
        columns = "uSeR_iD,identity_provider,isAuthenticated".split(",")
        assert parse_event_json(
            data=user, property_columns=columns, event_column="family_name", identity_column="email", timestamp_column="created_at"
        ) == {
            "event": "Blanda",
            "identity": "beryl_becker95@yahoo.com",
            "properties": {},
            "timestamp": "2022-10-21T04:08:58.994Z",
        }

    def test_parse_missing_identity(self):
        columns = "*".split(",")
        assert (
            parse_event_json(
                data=user, property_columns=columns, event_column="family_name", identity_column="UsEr_id", timestamp_column="created_at"
            )
            is None
        )

    def test_parse_missing_event(self):
        columns = "*".split(",")
        assert (
            parse_event_json(
                data=user, property_columns=columns, event_column="order_name", identity_column="email", timestamp_column="created_at"
            )
            is None
        )

    def test_parse_missing_timestamp(self):
        known = pendulum.datetime(2023, 5, 21, 12)
        pendulum.set_test_now(known)
        columns = "*".split(",")
        assert parse_event_json(
            data=user, property_columns=columns, event_column="family_name", identity_column="email", timestamp_column="updated_at"
        ) == {
            "event": "Blanda",
            "identity": "beryl_becker95@yahoo.com",
            "properties": {
                "blocked": False,
                "created_at": "2022-10-21T04:08:58.994Z",
                "email": "beryl_becker95@yahoo.com",
                "email_verified": False,
                "family_name": "Blanda",
                "given_name": "Bradly",
                "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            },
            "timestamp": "2023-05-21T12:00:00Z",
        }
        pendulum.set_test_now()


class TestParseAupJson:
    def test_parse_all_properties(self):
        columns = "*".split(",")
        assert parse_aup_json(data=user, property_columns=columns, identity_column="user_id",) == {
            "identity": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            "properties": {
                "blocked": False,
                "created_at": "2022-10-21T04:08:58.994Z",
                "email": "beryl_becker95@yahoo.com",
                "email_verified": False,
                "family_name": "Blanda",
                "given_name": "Bradly",
                "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            },
        }

    def test_parse_selective_properties(self):
        columns = "blocked,email,created_at,user_id".split(",")
        assert parse_aup_json(data=user, property_columns=columns, identity_column="user_id",) == {
            "identity": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            "properties": {
                "blocked": False,
                "created_at": "2022-10-21T04:08:58.994Z",
                "email": "beryl_becker95@yahoo.com",
                "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            },
        }

    def test_parse_missing_properties(self):
        columns = "uSeR_iD,identity_provider,isAuthenticated".split(",")
        assert parse_aup_json(data=user, property_columns=columns, identity_column="user_id",) == {
            "identity": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            "properties": {},
        }

    def test_parse_missing_account_id(self):
        columns = "*".split(",")
        assert (
            parse_aup_json(
                data=user,
                property_columns=columns,
                identity_column="UsEr_id",
            )
            is None
        )


class TestParseAapJson:
    def test_parse_all_properties(self):
        columns = "*".split(",")
        assert parse_aap_json(data=user, property_columns=columns, account_id_column="user_id",) == {
            "account_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            "properties": {
                "blocked": False,
                "created_at": "2022-10-21T04:08:58.994Z",
                "email": "beryl_becker95@yahoo.com",
                "email_verified": False,
                "family_name": "Blanda",
                "given_name": "Bradly",
                "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            },
        }

    def test_parse_selective_properties(self):
        columns = "blocked,email,created_at,user_id".split(",")
        assert parse_aap_json(data=user, property_columns=columns, account_id_column="user_id",) == {
            "account_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            "properties": {
                "blocked": False,
                "created_at": "2022-10-21T04:08:58.994Z",
                "email": "beryl_becker95@yahoo.com",
                "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            },
        }

    def test_parse_missing_properties(self):
        columns = "uSeR_iD,identity_provider,isAuthenticated".split(",")
        assert parse_aap_json(data=user, property_columns=columns, account_id_column="user_id",) == {
            "account_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
            "properties": {},
        }

    def test_parse_missing_account_id(self):
        columns = "*".split(",")
        assert (
            parse_aap_json(
                data=user,
                property_columns=columns,
                account_id_column="UsEr_id",
            )
            is None
        )
