#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_kyve.util import CustomResourceSchemaLoader


def test_custom_loader():
    custom_loader = CustomResourceSchemaLoader("source_kyve")
    schema = custom_loader.get_schema("evm/block")

    assert schema == {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "additionalProperties": True,
        "properties": {
            "_difficulty": {
                "properties": {
                    "hex": {"type": ["null", "string"]},
                    "type": {"type": ["null", "string"]},
                },
                "required": ["hex", "type"],
                "type": ["null", "object"],
            },
            "difficulty": {"type": ["null", "integer"]},
            "extraData": {"type": ["null", "string"]},
            "gasLimit": {
                "properties": {
                    "hex": {"type": ["null", "string"]},
                    "type": {"type": ["null", "string"]},
                },
                "required": ["hex", "type"],
                "type": ["null", "object"],
            },
            "gasUsed": {
                "properties": {
                    "hex": {"type": ["null", "string"]},
                    "type": {"type": ["null", "string"]},
                },
                "required": ["hex", "type"],
                "type": ["null", "object"],
            },
            "hash": {"type": ["null", "string"]},
            "miner": {"type": ["null", "string"]},
            "number": {"type": ["null", "integer"]},
            "parentHash": {"type": ["null", "string"]},
            "timestamp": {"type": ["null", "integer"]},
            "transactions": {
                "items": {
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "additionalProperties": True,
                    "properties": {
                        "accessList": {"type": "null"},
                        "blockHash": {"type": ["null", "string"]},
                        "blockNumber": {"type": ["null", "integer"]},
                        "chainId": {"type": ["null", "integer"]},
                        "creates": {"type": ["null", "string"]},
                        "data": {"type": ["null", "string"]},
                        "from": {"type": ["null", "string"]},
                        "gasLimit": {
                            "properties": {
                                "hex": {"type": ["null", "string"]},
                                "type": {"type": ["null", "string"]},
                            },
                            "required": ["hex", "type"],
                            "type": ["null", "object"],
                        },
                        "gasPrice": {
                            "properties": {
                                "hex": {"type": ["null", "string"]},
                                "type": {"type": ["null", "string"]},
                            },
                            "required": ["hex", "type"],
                            "type": ["null", "object"],
                        },
                        "hash": {"type": ["null", "string"]},
                        "nonce": {"type": ["null", "integer"]},
                        "r": {"type": ["null", "string"]},
                        "raw": {"type": ["null", "string"]},
                        "s": {"type": ["null", "string"]},
                        "to": {"type": ["string", "null"]},
                        "transactionIndex": {"type": ["null", "integer"]},
                        "type": {"type": ["null", "integer"]},
                        "v": {"type": ["null", "integer"]},
                        "value": {
                            "properties": {
                                "hex": {"type": ["null", "string"]},
                                "type": {"type": ["null", "string"]},
                            },
                            "required": ["hex", "type"],
                            "type": ["null", "object"],
                        },
                    },
                    "required": [
                        "r",
                        "s",
                        "v",
                        "to",
                        "data",
                        "from",
                        "hash",
                        "type",
                        "nonce",
                        "value",
                        "chainId",
                        "creates",
                        "gasLimit",
                        "gasPrice",
                        "blockHash",
                        "accessList",
                        "blockNumber",
                        "transactionIndex",
                    ],
                    "type": "object",
                },
                "type": ["null", "array"],
            },
        },
        "required": [
            "hash",
            "miner",
            "number",
            "gasUsed",
            "gasLimit",
            "extraData",
            "timestamp",
            "difficulty",
            "parentHash",
            "_difficulty",
            "transactions",
        ],
        "type": "object",
    }
