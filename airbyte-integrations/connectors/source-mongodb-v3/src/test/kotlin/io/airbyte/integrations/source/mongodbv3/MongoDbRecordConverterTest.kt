/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.util.Date
import java.util.UUID
import org.bson.BsonBinarySubType
import org.bson.BsonRegularExpression
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.types.Binary
import org.bson.types.Code
import org.bson.types.CodeWithScope
import org.bson.types.Decimal128
import org.bson.types.MaxKey
import org.bson.types.MinKey
import org.bson.types.ObjectId
import org.bson.types.Symbol
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Verifies the documented BSON -> JSON conversions and the legacy state `_id` encoding. */
class MongoDbRecordConverterTest {

    private val converter = MongoDbRecordConverter(schemaEnforced = true)

    private fun json(document: Document) = converter.toPayloadWithId(document).first.toJson()

    @Test
    fun testScalarConversions() {
        val node =
            json(
                Document("_id", ObjectId("650000000000000000000001"))
                    .append("s", "hi")
                    .append("i", 7)
                    .append("l", 9007199254740993L)
                    .append("d", 1.5)
                    .append("dec", Decimal128(BigDecimal("12.34")))
                    .append("b", true)
                    .append("n", null),
            )
        Assertions.assertEquals("650000000000000000000001", node["_id"].asText())
        Assertions.assertEquals("hi", node["s"].asText())
        Assertions.assertEquals(7, node["i"].asInt())
        Assertions.assertEquals(9007199254740993L, node["l"].asLong())
        Assertions.assertEquals(1.5, node["d"].asDouble())
        Assertions.assertEquals(BigDecimal("12.34"), node["dec"].decimalValue())
        Assertions.assertTrue(node["b"].asBoolean())
        Assertions.assertTrue(node["n"].isNull)
    }

    @Test
    fun testDateAlwaysKeepsMilliseconds() {
        // 1704067200000 = 2024-01-01T00:00:00.000Z; Instant.toString() would drop the .000.
        val node = json(Document("_id", 1).append("created", Date(1704067200000L)))
        Assertions.assertEquals("2024-01-01T00:00:00.000Z", node["created"].asText())
    }

    @Test
    fun testSpecialTypeConversions() {
        val node =
            json(
                Document("_id", 1)
                    .append("bin", Binary(byteArrayOf(1, 2, 3)))
                    .append("re", BsonRegularExpression("abc", "i"))
                    .append("code", Code("function(){}"))
                    .append("codews", CodeWithScope("function(){}", Document("x", 1)))
                    .append("sym", Symbol("s"))
                    .append("ts", BsonTimestamp(1700000000, 1)),
            )
        Assertions.assertEquals("AQID", node["bin"].asText())
        Assertions.assertEquals("(i)abc", node["re"].asText())
        Assertions.assertEquals("function(){}", node["code"].asText())
        Assertions.assertEquals("function(){}", node["codews"]["code"].asText())
        Assertions.assertEquals(1, node["codews"]["scope"]["x"].asInt())
        Assertions.assertEquals("s", node["sym"].asText())
        Assertions.assertTrue(node["ts"].isTextual)
    }

    @Test
    fun testMinAndMaxKeyAreOmitted() {
        val node = json(Document("_id", 1).append("lo", MinKey()).append("hi", MaxKey()))
        Assertions.assertFalse(node.has("lo"))
        Assertions.assertFalse(node.has("hi"))
    }

    @Test
    fun testNestedDocumentAndArray() {
        val node =
            json(
                Document("_id", 1)
                    .append("addr", Document("city", "Paris"))
                    .append("tags", listOf("a", "b")),
            )
        Assertions.assertEquals("Paris", node["addr"]["city"].asText())
        Assertions.assertEquals(listOf("a", "b"), node["tags"].map { it.asText() })
    }

    @Test
    fun testSchemalessEmitsIdAndDataObject() {
        val schemaless = MongoDbRecordConverter(schemaEnforced = false)
        val payload: NativeRecordPayload =
            schemaless.toPayloadWithId(Document("_id", "k1").append("v", 2)).first
        val node = payload.toJson()
        Assertions.assertEquals("k1", node["_id"].asText())
        Assertions.assertEquals(2, node["data"]["v"].asInt())
    }

    @Test
    fun testStateValueIdTypes() {
        Assertions.assertEquals(
            MongoDbIdType.OBJECT_ID,
            MongoDbStreamStateValue.fromLastId(
                    ObjectId("650000000000000000000001"),
                    MongoDbSnapshotStatus.COMPLETE,
                )
                .idType,
        )
        Assertions.assertEquals(
            MongoDbIdType.INT,
            MongoDbStreamStateValue.fromLastId(5, MongoDbSnapshotStatus.FULL_REFRESH).idType,
        )
        Assertions.assertEquals(
            MongoDbIdType.LONG,
            MongoDbStreamStateValue.fromLastId(5L, MongoDbSnapshotStatus.FULL_REFRESH).idType,
        )
        Assertions.assertEquals(
            MongoDbIdType.STRING,
            MongoDbStreamStateValue.fromLastId("k", MongoDbSnapshotStatus.FULL_REFRESH).idType,
        )
    }

    @Test
    fun testBinaryIdUuidVsBase64() {
        val uuid = UUID.fromString("123e4567-e89b-12d3-a456-426614174000")
        val bytes =
            java.nio.ByteBuffer.allocate(16)
                .putLong(uuid.mostSignificantBits)
                .putLong(uuid.leastSignificantBits)
                .array()
        val uuidState =
            MongoDbStreamStateValue.fromLastId(
                Binary(BsonBinarySubType.UUID_STANDARD, bytes),
                MongoDbSnapshotStatus.COMPLETE,
            )
        Assertions.assertEquals(uuid.toString(), uuidState.id)
        Assertions.assertEquals(MongoDbIdType.BINARY, uuidState.idType)

        val genericState =
            MongoDbStreamStateValue.fromLastId(
                Binary(byteArrayOf(1, 2, 3)),
                MongoDbSnapshotStatus.COMPLETE,
            )
        Assertions.assertEquals("AQID", genericState.id)
    }

    @Test
    fun testStateValueRoundTrip() {
        val value =
            MongoDbStreamStateValue("abc", MongoDbSnapshotStatus.IN_PROGRESS, MongoDbIdType.STRING)
        val parsed = MongoDbStreamStateValue.fromOpaqueStateValue(value.toOpaqueStateValue())
        Assertions.assertEquals(value, parsed)
        // The serialized shape matches the legacy keys.
        val node = value.toOpaqueStateValue()
        Assertions.assertEquals(
            setOf("id", "status", "idType", "binarySubType"),
            node.fieldNames().asSequence().toSet(),
        )
        Assertions.assertEquals(
            Jsons.readTree(
                """{"id":"abc","status":"IN_PROGRESS","idType":"STRING","binarySubType":0}"""
            ),
            node
        )
    }
}
