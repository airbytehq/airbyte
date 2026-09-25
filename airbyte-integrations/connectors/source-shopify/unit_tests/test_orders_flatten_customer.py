#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


from source_shopify.streams.streams import Orders


def test_produce_records_flattens_customer(auth_config):
    stream = Orders(auth_config)
    record = {
        "id": 1,
        "customer": {
            "id": 1,
            "email": "a@b.c",
            "total_spent": "1.50",
            "default_address": {"city": "Fair Lawn", "zip": "07410"},
        },
    }
    output = list(stream.produce_records([record]))[0]

    assert output["customer_id"] == 1
    assert output["customer_email"] == "a@b.c"
    assert "customer_total_spent" in output
    assert output["customer_default_address"] == {"city": "Fair Lawn", "zip": "07410"}
    assert output["customer"] == record["customer"]
    assert output["shop_url"] == auth_config["shop"]


def test_produce_records_null_customer_adds_no_customer_fields(auth_config):
    stream = Orders(auth_config)
    output = list(stream.produce_records([{"id": 1, "customer": None}]))[0]

    assert output["customer"] is None
    assert not any(key.startswith("customer_") for key in output)


def test_produce_records_missing_customer_adds_no_customer_fields(auth_config):
    stream = Orders(auth_config)
    output = list(stream.produce_records([{"id": 1}]))[0]

    assert "customer" not in output
    assert not any(key.startswith("customer_") for key in output)


def test_produce_records_single_dict_input_flattens_customer(auth_config):
    stream = Orders(auth_config)
    output = list(stream.produce_records({"id": 1, "customer": {"id": 7, "email": "a@b.c"}}))[0]

    assert output["customer_id"] == 7
    assert output["customer_email"] == "a@b.c"
    assert output["customer"] == {"id": 7, "email": "a@b.c"}


def test_orders_schema_has_flattened_customer_fields():
    schema = Orders(config={"authenticator": None, "shop": "test"}).get_json_schema()
    customer_properties = schema["properties"]["customer"]["properties"]
    for key, field_schema in customer_properties.items():
        flattened = schema["properties"][f"customer_{key}"]
        if key == "accepts_marketing_updated_at":
            # the nested field is exempt from the date-time annotation because typed destinations
            # store `customer` as a single JSON column; the flattened column is annotated
            assert flattened == field_schema | {"format": "date-time"}
        else:
            assert flattened == field_schema
