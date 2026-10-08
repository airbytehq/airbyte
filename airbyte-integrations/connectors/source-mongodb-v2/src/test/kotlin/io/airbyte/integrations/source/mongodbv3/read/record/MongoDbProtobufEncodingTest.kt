/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.record

import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toProtobuf
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbFieldType
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import org.bson.Document
import org.bson.types.Decimal128
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Tests the socket/speed (protobuf) encoding path: the per-type codecs' [valueForProtobufEncoding]
 * coercion and an end-to-end `NativeRecordPayload.toProtobuf` for a schema-aware payload, including
 * a value whose BSON type does not match its declared schema type (nulled on protobuf).
 */
class MongoDbProtobufEncodingTest {

    @Test
    fun testCodecCoercionForProtobuf() {
        Assertions.assertEquals("hi", MongoStringValueCodec.valueForProtobufEncoding(text("hi")))
        Assertions.assertEquals("30", MongoStringValueCodec.valueForProtobufEncoding(int(30)))
        Assertions.assertNull(MongoStringValueCodec.valueForProtobufEncoding(Jsons.nullNode()))

        Assertions.assertEquals(
            BigDecimal("12.34"),
            MongoNumberValueCodec.valueForProtobufEncoding(Jsons.numberNode(BigDecimal("12.34"))),
        )
        // A non-number value for a NUMBER field is nulled on the protobuf channel.
        Assertions.assertNull(MongoNumberValueCodec.valueForProtobufEncoding(text("nope")))

        Assertions.assertEquals(
            true,
            MongoBooleanValueCodec.valueForProtobufEncoding(Jsons.booleanNode(true)),
        )
        Assertions.assertNull(MongoBooleanValueCodec.valueForProtobufEncoding(text("true")))

        val obj = Jsons.objectNode().put("x", 1)
        Assertions.assertEquals(
            """{"x":1}""",
            MongoJsonbValueCodec.valueForProtobufEncoding(obj),
        )
        Assertions.assertNull(MongoNullValueCodec.valueForProtobufEncoding(text("x")))

        // encode() is the identity on every codec (JSONL channel keeps the raw node).
        Assertions.assertEquals(text("hi"), MongoStringValueCodec.encode(text("hi")))
    }

    @Test
    fun testPayloadEncodesToTypedProtobuf() {
        val schema: Set<DataOrMetaField> =
            setOf(
                EmittedField("b", MongoDbFieldType.BOOLEAN),
                EmittedField("n", MongoDbFieldType.NUMBER),
                EmittedField("obj", MongoDbFieldType.OBJECT),
                EmittedField("s", MongoDbFieldType.STRING),
            )
        val converter =
            MongoDbRecordConverter(
                schemaEnforced = true,
                schemaFieldTypes =
                    mapOf(
                        "b" to MongoDbFieldType.BOOLEAN,
                        "n" to MongoDbFieldType.NUMBER,
                        "obj" to MongoDbFieldType.OBJECT,
                        "s" to MongoDbFieldType.STRING,
                    ),
            )
        val document =
            Document("_id", 1)
                .append("s", "hi")
                .append("n", Decimal128(BigDecimal("12.34")))
                .append("b", true)
                .append("obj", Document("x", 1))
        val record: AirbyteRecordMessageProtobuf =
            encode(converter.toPayloadWithId(document).first, schema)

        // Fields are encoded positionally in sorted-id order: b, n, obj, s.
        Assertions.assertTrue(record.getData(0).getBoolean())
        Assertions.assertEquals("12.34", record.getData(1).getBigDecimal())
        Assertions.assertTrue(record.getData(2).hasJson())
        Assertions.assertEquals("hi", record.getData(3).getString())
    }

    @Test
    fun testTypeMismatchIsNulledOnProtobuf() {
        val schema: Set<DataOrMetaField> = setOf(EmittedField("n", MongoDbFieldType.NUMBER))
        val converter = MongoDbRecordConverter(true, mapOf("n" to MongoDbFieldType.NUMBER))
        // `n` is discovered as NUMBER but this document holds a string.
        val document = Document("_id", 1).append("n", "not-a-number")
        val record = encode(converter.toPayloadWithId(document).first, schema)
        Assertions.assertTrue(record.getData(0).hasNull())
    }

    /**
     * Mirrors the CDK proto consumer: pre-fill a slot per schema field, then overwrite by index.
     */
    private fun encode(
        payload: NativeRecordPayload,
        schema: Set<DataOrMetaField>,
    ): AirbyteRecordMessageProtobuf {
        val builder = AirbyteRecordMessageProtobuf.newBuilder()
        schema
            .sortedBy { it.id }
            .forEach { builder.addData(AirbyteValueProtobuf.getDefaultInstance()) }
        payload.toProtobuf(schema, builder, AirbyteValueProtobuf.newBuilder())
        return builder.build()
    }

    private fun text(value: String) = Jsons.textNode(value)

    private fun int(value: Int) = Jsons.numberNode(value)
}
