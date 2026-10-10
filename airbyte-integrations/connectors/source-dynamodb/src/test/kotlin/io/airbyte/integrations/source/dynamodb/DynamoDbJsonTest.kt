/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

class DynamoDbJsonTest {

    /** Item 1 of the `all_types` parity table, in DynamoDB JSON. */
    private val allTypesItem: String =
        """
        {"id": {"S": "1"}, "str": {"S": "hello"}, "int": {"N": "42"}, "dec": {"N": "12.34"},
         "big": {"N": "123456789012345678901234567890"}, "neg": {"N": "-7"}, "bin": {"B": "AQID"},
         "sset": {"SS": ["a", "b"]}, "nset": {"NS": ["1", "2.5", "-3"]}, "bset": {"BS": ["AQID", "BAUG"]},
         "flag": {"BOOL": true}, "nothing": {"NULL": true},
         "map": {"M": {"s": {"S": "x"}, "n_int": {"N": "1"}, "n_dec": {"N": "1.5"}, "b": {"B": "AQ=="},
                       "bool": {"BOOL": false}, "nul": {"NULL": true}, "ss": {"SS": ["m"]}, "ns": {"NS": ["1"]},
                       "bs": {"BS": ["AQ=="]}, "nested_map": {"M": {"deep": {"S": "y"}}},
                       "nested_list": {"L": [{"S": "z"}, {"N": "9"}]}}},
         "list": {"L": [{"S": "s"}, {"N": "1"}, {"N": "2.5"}, {"BOOL": true}, {"NULL": true},
                        {"M": {"k": {"S": "v"}}}, {"L": [{"S": "inner"}]}]},
         "flexible": {"S": "text"}}
        """

    /**
     * The record the legacy connector emitted for that item, except `big`: the legacy connector
     * parsed every `N` that is not a `long` as a `double`, which turned
     * `123456789012345678901234567890` into `1.2345678901234568E29`; this connector keeps the exact
     * value.
     */
    private val expectedRecord: String =
        """
        {"id": "1", "str": "hello", "int": 42, "dec": 12.34, "big": 123456789012345678901234567890,
         "neg": -7, "bin": "AQID", "sset": ["a", "b"], "nset": [1, 2.5, -3], "bset": ["AQID", "BAUG"],
         "flag": true, "nothing": null,
         "map": {"s": "x", "n_int": 1, "n_dec": 1.5, "b": "AQ==", "bool": false, "nul": null, "ss": ["m"],
                 "ns": [1], "bs": ["AQ=="], "nested_map": {"deep": "y"}, "nested_list": ["z", 9]},
         "list": ["s", 1, 2.5, true, null, {"k": "v"}, ["inner"]],
         "flexible": "text"}
        """

    @Test
    fun testRecordValues() {
        val item: Map<String, AttributeValue> =
            DynamoDbJson.itemFromDynamoDbJson(Jsons.readTree(allTypesItem))
        val record: JsonNode =
            Jsons.objectNode().apply {
                for ((name, value) in item) {
                    set<JsonNode>(name, DynamoDbJson.toRecordValue(value))
                }
            }
        // Serialize and parse again: BinaryNode equals its base64 TextNode only as text.
        Assertions.assertEquals(
            Jsons.readTree(expectedRecord),
            Jsons.readTree(Jsons.writeValueAsString(record)),
        )
    }

    @Test
    fun testNumbers() {
        Assertions.assertEquals("42", DynamoDbJson.numberNode("42").toString())
        Assertions.assertTrue(DynamoDbJson.numberNode("42").isLong)
        Assertions.assertEquals("-7", DynamoDbJson.numberNode("-7").toString())
        Assertions.assertEquals(
            "9223372036854775807",
            DynamoDbJson.numberNode("9223372036854775807").toString()
        )
        // Beyond a long: exact, not a double.
        Assertions.assertEquals(
            "9223372036854775808",
            DynamoDbJson.numberNode("9223372036854775808").toString(),
        )
        Assertions.assertEquals("12.34", DynamoDbJson.numberNode("12.34").toString())
        Assertions.assertEquals("1.0", DynamoDbJson.numberNode("1.0").toString())
        Assertions.assertEquals(
            "0.1234567890123456789012345678901234567",
            DynamoDbJson.numberNode("0.1234567890123456789012345678901234567").toString(),
        )
    }

    /** Key attributes (S, N, B) and every other type survive a state round trip unchanged. */
    @Test
    fun testDynamoDbJsonRoundTrip() {
        val item: Map<String, AttributeValue> =
            DynamoDbJson.itemFromDynamoDbJson(Jsons.readTree(allTypesItem))
        val json: JsonNode = DynamoDbJson.itemToDynamoDbJson(item)
        Assertions.assertEquals(Jsons.readTree(allTypesItem), Jsons.readTree(json.toString()))
        Assertions.assertEquals(
            item,
            DynamoDbJson.itemFromDynamoDbJson(Jsons.readTree(json.toString())),
        )
    }

    @Test
    fun testKeyWithBinaryAttribute() {
        val key: Map<String, AttributeValue> =
            DynamoDbJson.itemFromDynamoDbJson(Jsons.readTree("""{"id": {"B": "AQID"}}"""))
        Assertions.assertArrayEquals(byteArrayOf(1, 2, 3), key["id"]!!.b().asByteArray())
        Assertions.assertEquals(
            """{"id":{"B":"AQID"}}""",
            DynamoDbJson.itemToDynamoDbJson(key).toString(),
        )
    }
}
