/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.output.sockets.toProtobuf
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

/**
 * Every DynamoDB attribute type must be encodable on the protobuf data channel
 * (`DATA_CHANNEL_FORMAT=PROTOBUF`) and carry the same value as the JSONL channels. Fields are typed
 * ([DynamoDbFieldType.airbyteSchemaTypeOf]): scalars travel as typed protobuf values (a string, an
 * integer, a decimal in plain notation, a boolean, the base64 string of a binary), maps, lists and
 * sets as JSON text whose numbers must be plain (`100000`, never `1E+5`), a rule that holds for
 * every connector.
 */
class DynamoDbProtobufEncodingTest {

    /** One item with every attribute type, including numbers whose `toString()` is not plain. */
    private val item: String =
        """
        {"id": {"S": "1"}, "str": {"S": "hello"}, "int": {"N": "42"}, "neg": {"N": "-7"},
         "dec": {"N": "12.34"}, "exp": {"N": "1e5"}, "tiny": {"N": "-0.0000001"},
         "big": {"N": "123456789012345678901234567890"}, "beyond_long": {"N": "9223372036854775808"},
         "bin": {"B": "AQID"}, "flag": {"BOOL": true}, "nothing": {"NULL": true},
         "sset": {"SS": ["a", "b"]}, "nset": {"NS": ["1", "2.5", "1e3"]}, "bset": {"BS": ["AQID", "BAUG"]},
         "map": {"M": {"s": {"S": "x"}, "n": {"N": "1e5"},
                       "deep": {"M": {"l": {"L": [{"N": "-0.0000001"}, {"NULL": true}]}}}}},
         "list": {"L": [{"S": "s"}, {"N": "2.5"}, {"BOOL": false}, {"NULL": true}, {"M": {"k": {"N": "1e2"}}}]}}
        """

    private fun attributes(): Map<String, AttributeValue> =
        DynamoDbJson.itemFromDynamoDbJson(Jsons.readTree(item))

    /** The fields DISCOVER would derive from this item. */
    private fun fields(): List<EmittedField> =
        attributes().map { (name, value) -> EmittedField(name, DynamoDbFieldType.of(value)!!) }

    private fun codec(field: EmittedField): DynamoDbJsonNodeCodec =
        (field.type as DynamoDbFieldType).codec

    /** The payload [DynamoDbPartitionReader] builds for this item. */
    private fun payload(
        fields: List<EmittedField>,
        item: Map<String, AttributeValue>
    ): NativeRecordPayload =
        fields.associateTo(mutableMapOf<String, FieldValueEncoder<*>>()) { field ->
            field.id to
                FieldValueEncoder(item[field.id]?.let(DynamoDbJson::toRecordValue), codec(field))
        }

    /** Encodes a record with the CDK the way the protobuf socket consumer does. */
    private fun encode(
        fields: List<EmittedField>,
        payload: NativeRecordPayload
    ): AirbyteRecordMessageProtobuf {
        val builder: AirbyteRecordMessageProtobuf.Builder =
            AirbyteRecordMessageProtobuf.newBuilder()
        repeat(fields.size) { builder.addData(AirbyteValueProtobuf.newBuilder()) }
        return payload
            .toProtobuf(fields.toSet(), builder, AirbyteValueProtobuf.newBuilder())
            .build()
    }

    /** Protobuf data slot of each field: the CDK orders the fields alphabetically. */
    private fun slots(fields: List<EmittedField>): Map<String, Int> =
        fields.sortedBy { it.id }.mapIndexed { i, f -> f.id to i }.toMap()

    @Test
    fun testEveryAttributeTypeMatchesTheJsonChannel() {
        val fields: List<EmittedField> = fields()
        val payload: NativeRecordPayload = payload(fields, attributes())
        val record: AirbyteRecordMessageProtobuf = encode(fields, payload)
        Assertions.assertEquals(fields.size, record.dataCount)
        // What the STDIO / JSONL channels emit for the same payload.
        val expected: ObjectNode = payload.toJson()
        val actual: ObjectNode = Jsons.objectNode()
        for ((name, slot) in slots(fields)) {
            actual.set<JsonNode>(
                name,
                SpeedModeTestSupport.protobufValueToJson(record.getData(slot))
            )
        }
        Assertions.assertEquals(
            SpeedModeTestSupport.normalize(expected),
            SpeedModeTestSupport.normalize(actual),
        )
    }

    @Test
    fun testWireValueOfEveryAttributeType() {
        val fields: List<EmittedField> = fields()
        val record: AirbyteRecordMessageProtobuf = encode(fields, payload(fields, attributes()))
        val slots: Map<String, Int> = slots(fields)
        fun value(name: String): AirbyteValueProtobuf = record.getData(slots.getValue(name))
        fun case(name: String): AirbyteValueProtobuf.ValueCase = value(name).valueCase
        fun text(name: String): String? = SpeedModeTestSupport.wireText(value(name))
        // Scalars travel typed.
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.STRING, case("str"))
        Assertions.assertEquals("hello", text("str"))
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.INTEGER, case("int"))
        Assertions.assertEquals("42", text("int"))
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.INTEGER, case("neg"))
        Assertions.assertEquals("-7", text("neg"))
        // Decimals, and integers the sample did not type as such, are exact decimals in plain form.
        for ((name, plain) in
            mapOf(
                "dec" to "12.34",
                "exp" to "100000",
                "tiny" to "-0.0000001",
                "big" to "123456789012345678901234567890",
                "beyond_long" to "9223372036854775808",
            )) {
            Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.BIG_DECIMAL, case(name), name)
            Assertions.assertEquals(plain, text(name), name)
        }
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.BOOLEAN, case("flag"))
        Assertions.assertEquals("true", text("flag"))
        // A binary is its base64 string on the wire, as the CDK encodes BINARY fields.
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.STRING, case("bin"))
        Assertions.assertEquals("AQID", text("bin"))
        // Sets, lists and maps: JSON text with the same nested values, no scientific notation.
        for (name in listOf("sset", "nset", "bset", "map", "list")) {
            Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.JSON, case(name), name)
        }
        Assertions.assertEquals(Jsons.readTree("""["a","b"]"""), Jsons.readTree(text("sset")!!))
        Assertions.assertEquals(Jsons.readTree("""[1,2.5,1000]"""), Jsons.readTree(text("nset")!!))
        Assertions.assertEquals(
            Jsons.readTree("""["AQID","BAUG"]"""),
            Jsons.readTree(text("bset")!!),
        )
        Assertions.assertEquals(
            Jsons.readTree("""{"s":"x","n":100000,"deep":{"l":[-0.0000001,null]}}"""),
            Jsons.readTree(text("map")!!),
        )
        Assertions.assertEquals(
            Jsons.readTree("""["s",2.5,false,null,{"k":100}]"""),
            Jsons.readTree(text("list")!!),
        )
        for ((name, slot) in slots) {
            val wire: String = SpeedModeTestSupport.wireText(record.getData(slot)) ?: continue
            Assertions.assertFalse(
                SpeedModeTestSupport.SCIENTIFIC_NOTATION.containsMatchIn(wire),
                "$name is not plain on the wire: $wire",
            )
        }
        // A DynamoDB NULL is a protobuf null, like an attribute the item does not have.
        Assertions.assertNull(text("nothing"))
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.NULL, case("nothing"))
    }

    /**
     * `StdoutOutputConsumer` and `SocketJsonOutputConsumer` write record data through the CDK's
     * [Jsons] generator (`WRITE_BIGDECIMAL_AS_PLAIN`); the protobuf codec must carry the same
     * digits: an exact [BigDecimal] for a NUMBER field, an exact [BigInteger] for an INTEGER field,
     * plain JSON text for a nested number.
     */
    @Test
    fun testNumbersArePlainOnBothChannels() {
        val cases: Map<String, String> =
            mapOf(
                "42" to "42",
                "-7" to "-7",
                "12.34" to "12.34",
                "1.0" to "1.0",
                "1e5" to "100000",
                "1.5E3" to "1500",
                "-0.0000001" to "-0.0000001",
                "9223372036854775808" to "9223372036854775808",
                "123456789012345678901234567890" to "123456789012345678901234567890",
                "0.1234567890123456789012345678901234567" to
                    "0.1234567890123456789012345678901234567",
                "1E-130" to "0." + "0".repeat(129) + "1",
            )
        val number = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.NUMBER)
        val integer = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.INTEGER)
        for ((n, plain) in cases) {
            val node: JsonNode = DynamoDbJson.numberNode(n)
            Assertions.assertEquals(plain, Jsons.writeValueAsString(node), "JSONL channel for $n")
            Assertions.assertEquals(
                plain,
                (number.valueForProtobufEncoding(node) as BigDecimal).toPlainString(),
                "NUMBER field for $n",
            )
            val integral: Boolean = BigDecimal(plain).stripTrailingZeros().scale() <= 0
            Assertions.assertEquals(integral, integer.representable(node), "INTEGER field for $n")
            if (integral) {
                Assertions.assertEquals(
                    BigDecimal(plain).toBigIntegerExact(),
                    integer.valueForProtobufEncoding(node) as BigInteger,
                    "INTEGER field for $n",
                )
            }
        }
        // The same numbers nested in a map travel as one JSON text, plain as well.
        val map: AttributeValue =
            DynamoDbJson.fromDynamoDbJson(
                Jsons.readTree("""{"M": {"a": {"N": "1e5"}, "b": {"L": [{"N": "-0.0000001"}]}}}""")
            )
        Assertions.assertEquals(
            """{"a":100000,"b":[-0.0000001]}""",
            DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.JSONB)
                .valueForProtobufEncoding(DynamoDbJson.toRecordValue(map)!!),
        )
    }

    /**
     * DynamoDB is schemaless and the schema comes from a sample: a value can be of another type
     * than its field declares. The reader then sends a null with a change record on the protobuf
     * channel ([DynamoDbPartitionReader]); [DynamoDbJsonNodeCodec.representable] is the test.
     */
    @Test
    fun testMismatchedValuesAreNotRepresentable() {
        val text: JsonNode = Jsons.textNode("text")
        val one: JsonNode = DynamoDbJson.numberNode("1")
        val decimal: JsonNode = DynamoDbJson.numberNode("12.5")
        val bigIntegral: JsonNode = DynamoDbJson.numberNode("123456789012345678901234567890")
        val bytes: JsonNode = Jsons.binaryNode(byteArrayOf(1, 2, 3))
        val flag: JsonNode = Jsons.booleanNode(true)
        val map: JsonNode = Jsons.readTree("""{"a":1}""")

        val integer = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.INTEGER)
        Assertions.assertTrue(integer.representable(one))
        Assertions.assertTrue(integer.representable(bigIntegral))
        Assertions.assertEquals(
            BigInteger("123456789012345678901234567890"),
            integer.valueForProtobufEncoding(bigIntegral),
        )
        Assertions.assertFalse(integer.representable(decimal))
        Assertions.assertFalse(integer.representable(text))
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            integer.valueForProtobufEncoding(text)
        }

        val number = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.NUMBER)
        Assertions.assertTrue(number.representable(one))
        Assertions.assertTrue(number.representable(decimal))
        Assertions.assertFalse(number.representable(text))
        Assertions.assertFalse(number.representable(flag))

        val string = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.STRING)
        Assertions.assertTrue(string.representable(text))
        // A binary in a string field: its base64 text.
        Assertions.assertTrue(string.representable(bytes))
        Assertions.assertEquals("AQID", string.valueForProtobufEncoding(bytes))
        Assertions.assertFalse(string.representable(one))
        Assertions.assertFalse(string.representable(map))

        val binary = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.BINARY)
        Assertions.assertTrue(binary.representable(bytes))
        Assertions.assertArrayEquals(
            byteArrayOf(1, 2, 3),
            binary.valueForProtobufEncoding(bytes) as ByteArray,
        )
        // Base64 text is the form a binary takes once it has been through JSON.
        Assertions.assertTrue(binary.representable(Jsons.textNode("AQID")))
        Assertions.assertArrayEquals(
            byteArrayOf(1, 2, 3),
            binary.valueForProtobufEncoding(Jsons.textNode("AQID")) as ByteArray,
        )
        Assertions.assertFalse(binary.representable(Jsons.textNode("not base64!")))
        Assertions.assertFalse(binary.representable(one))

        val boolean = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.BOOLEAN)
        Assertions.assertTrue(boolean.representable(flag))
        Assertions.assertFalse(boolean.representable(Jsons.textNode("true")))

        val nul = DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.NULL)
        Assertions.assertTrue(nul.representable(NullNode.instance))
        Assertions.assertFalse(nul.representable(text))

        // JSONB and arrays hold anything.
        for (codec in
            listOf(
                DynamoDbJsonNodeCodec(LeafAirbyteSchemaType.JSONB),
                DynamoDbJsonNodeCodec(ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING)),
            )) {
            for (value in listOf(text, one, decimal, bytes, flag, map)) {
                Assertions.assertTrue(codec.representable(value), "$value in ${codec.schemaType}")
            }
            Assertions.assertEquals("""{"a":1}""", codec.valueForProtobufEncoding(map))
        }
        // Null is representable everywhere and travels as a protobuf null.
        for (codec in listOf(integer, number, string, binary, boolean, nul)) {
            Assertions.assertTrue(codec.representable(NullNode.instance))
            Assertions.assertNull(codec.valueForProtobufEncoding(NullNode.instance))
        }
    }

    /**
     * The protobuf socket consumer reuses one record builder per stream and `toProtobuf` only
     * writes the slots present in the payload: an attribute the item does not have must be in the
     * payload as an explicit null, or the slot keeps the previous item's value. (The JSONL
     * consumers reset every field from a template, so they do not depend on it.)
     */
    @Test
    fun testSparseItemsNeedExplicitNullsOnTheProtobufChannel() {
        val fields: List<EmittedField> =
            listOf("id", "only_a", "only_b").map {
                EmittedField(
                    it,
                    DynamoDbFieldType.fromJsonSchema(Jsons.readTree("""{"type":"string"}"""))
                )
            }
        val first: Map<String, AttributeValue> =
            mapOf("id" to AttributeValue.fromS("s1"), "only_a" to AttributeValue.fromS("A"))
        val second: Map<String, AttributeValue> =
            mapOf("id" to AttributeValue.fromS("s2"), "only_b" to AttributeValue.fromS("B"))
        val reused: AirbyteRecordMessageProtobuf.Builder = AirbyteRecordMessageProtobuf.newBuilder()
        repeat(fields.size) { reused.addData(AirbyteValueProtobuf.newBuilder()) }
        val valueBuilder: AirbyteValueProtobuf.Builder = AirbyteValueProtobuf.newBuilder()

        fun decode(record: AirbyteRecordMessageProtobuf): Map<String, JsonNode> =
            slots(fields).mapValues { (_, slot) ->
                SpeedModeTestSupport.protobufValueToJson(record.getData(slot))
            }

        // Present attributes only: the second record inherits `only_a` from the first.
        fun presentOnly(item: Map<String, AttributeValue>): NativeRecordPayload =
            fields
                .filter { it.id in item }
                .associateTo(mutableMapOf<String, FieldValueEncoder<*>>()) { field ->
                    field.id to
                        FieldValueEncoder(
                            DynamoDbJson.toRecordValue(item.getValue(field.id)),
                            codec(field)
                        )
                }
        presentOnly(first).toProtobuf(fields.toSet(), reused, valueBuilder)
        val stale: Map<String, JsonNode> =
            decode(presentOnly(second).toProtobuf(fields.toSet(), reused, valueBuilder).build())
        Assertions.assertEquals(Jsons.textNode("A"), stale["only_a"], "the CDK reuses the builder")

        // Every schema field, absent ones as null: what the partition reader emits.
        payload(fields, first).toProtobuf(fields.toSet(), reused, valueBuilder)
        val clean: Map<String, JsonNode> =
            decode(payload(fields, second).toProtobuf(fields.toSet(), reused, valueBuilder).build())
        Assertions.assertEquals(
            mapOf(
                "id" to Jsons.textNode("s2"),
                "only_a" to Jsons.nullNode(),
                "only_b" to Jsons.textNode("B"),
            ),
            clean,
        )
        Assertions.assertEquals(
            Jsons.readTree("""{"id":"s2","only_a":null,"only_b":"B"}"""),
            payload(fields, second).toJson(),
        )
    }

    @Test
    fun testMissingAndNullValuesAreProtobufNulls() {
        val field =
            EmittedField(
                "c",
                DynamoDbFieldType.fromJsonSchema(Jsons.readTree("""{"type":"string"}"""))
            )
        val nullTyped =
            EmittedField(
                "n",
                DynamoDbFieldType.fromJsonSchema(Jsons.readTree("""{"type":"null"}"""))
            )
        // Attribute absent from the item.
        val absent: AirbyteRecordMessageProtobuf =
            encode(listOf(field), payload(listOf(field), emptyMap()))
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.NULL, absent.getData(0).valueCase)
        // Attribute of type NULL.
        val nul: AirbyteRecordMessageProtobuf =
            encode(
                listOf(field, nullTyped),
                payload(
                    listOf(field, nullTyped),
                    mapOf("c" to AttributeValue.fromNul(true), "n" to AttributeValue.fromNul(true)),
                ),
            )
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.NULL, nul.getData(0).valueCase)
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.NULL, nul.getData(1).valueCase)
        Assertions.assertNull(SpeedModeTestSupport.decode(nul.getData(0)))
        Assertions.assertNull(codec(field).valueForProtobufEncoding(NullNode.instance))
    }
}
