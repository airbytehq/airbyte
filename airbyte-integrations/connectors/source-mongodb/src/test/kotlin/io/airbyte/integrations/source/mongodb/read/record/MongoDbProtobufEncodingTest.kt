/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toProtobuf
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.discover.MongoDbFieldType
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
        Assertions.assertEquals("30", MongoStringValueCodec.valueForProtobufEncoding(num(30)))
        Assertions.assertEquals(
            "12.34",
            MongoStringValueCodec.valueForProtobufEncoding(num(BigDecimal("12.34"))),
        )
        // A document in a `string` field is its JSON on both channels.
        Assertions.assertEquals(
            """{"x":1}""",
            MongoStringValueCodec.valueForProtobufEncoding(OBJECT),
        )
        Assertions.assertNull(MongoStringValueCodec.valueForProtobufEncoding(MongoDbValue.Null))

        Assertions.assertEquals(
            BigDecimal("12.34"),
            MongoNumberValueCodec.valueForProtobufEncoding(num(BigDecimal("12.34"))),
        )
        Assertions.assertEquals(
            BigDecimal("30"),
            MongoNumberValueCodec.valueForProtobufEncoding(num(30)),
        )
        Assertions.assertEquals(
            BigDecimal("1.5"),
            MongoNumberValueCodec.valueForProtobufEncoding(num(1.5)),
        )
        // A non-number value for a NUMBER field is nulled on the protobuf channel.
        Assertions.assertNull(MongoNumberValueCodec.valueForProtobufEncoding(text("nope")))

        Assertions.assertEquals(
            true,
            MongoBooleanValueCodec.valueForProtobufEncoding(MongoDbValue.Bool(true)),
        )
        Assertions.assertNull(MongoBooleanValueCodec.valueForProtobufEncoding(text("true")))

        Assertions.assertEquals(
            """{"x":1}""",
            MongoJsonbValueCodec.valueForProtobufEncoding(OBJECT),
        )
        // A scalar in a `object` field is its JSON text, as the legacy connector sent it.
        Assertions.assertEquals("\"hi\"", MongoJsonbValueCodec.valueForProtobufEncoding(text("hi")))
        Assertions.assertNull(MongoJsonbValueCodec.valueForProtobufEncoding(MongoDbValue.Null))
        Assertions.assertNull(MongoNullValueCodec.valueForProtobufEncoding(text("x")))

        // The JSON channel takes every value as it is; a document as a raw JSON text node.
        Assertions.assertEquals(Jsons.textNode("hi"), MongoStringValueCodec.encode(text("hi")))
        Assertions.assertEquals(
            Jsons.readTree("""{"x":1}"""),
            Jsons.readTree(Jsons.writeValueAsString(MongoJsonbValueCodec.encode(OBJECT))),
        )
    }

    /** The codecs' `decode` is the inverse of `encode` on the JSON channel. */
    @Test
    fun testCodecDecodeInvertsEncode() {
        for (value in
            listOf(
                text("hi"),
                num(30),
                num(9_007_199_254_740_993L),
                num(1.5),
                num(BigDecimal("12.34")),
                MongoDbValue.Bool(true),
                MongoDbValue.Null,
                OBJECT,
                MongoDbValue.Json("[1,2]", isArray = true),
            )) {
            val roundTripped: MongoDbValue =
                MongoStringValueCodec.decode(
                    Jsons.readTree(Jsons.writeValueAsString(MongoStringValueCodec.encode(value))),
                )
            Assertions.assertEquals(value.toJsonText(), roundTripped.toJsonText())
            Assertions.assertEquals(value::class, roundTripped::class)
        }
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
            encode(converter.toPayload(document.toBsonDocument()), schema)

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
        val record = encode(converter.toPayload(document.toBsonDocument()), schema)
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

    private fun text(value: String) = MongoDbValue.Text(value)

    private fun num(value: Number) = MongoDbValue.Num(value)

    companion object {
        val OBJECT = MongoDbValue.Json("""{"x":1}""", isArray = false)
    }
}
