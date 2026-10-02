/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read

import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbFieldType
import io.airbyte.integrations.source.mongodbv3.read.snapshot.MongoDbIdType
import io.airbyte.integrations.source.mongodbv3.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.integrations.source.mongodbv3.read.snapshot.MongoDbStreamStateValue
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
    fun testRegexWithoutOptionsIsTheBarePattern() {
        // v2: "(options)pattern" only when options are present, otherwise just the pattern.
        val node = json(Document("_id", 1).append("re", BsonRegularExpression("abc")))
        Assertions.assertEquals("abc", node["re"].asText())
    }

    @Test
    fun testNonArrayValueInArrayFieldIsWrapped() {
        // Schema says `tags` is an array, but this document holds a scalar: wrap it (as v2 did) so
        // the destination does not null the structural mismatch.
        val converter =
            MongoDbRecordConverter(
                schemaEnforced = true,
                schemaFieldTypes =
                    mapOf("_id" to MongoDbFieldType.NUMBER, "tags" to MongoDbFieldType.ARRAY),
            )
        val node =
            converter.toPayloadWithId(Document("_id", 1).append("tags", "solo")).first.toJson()
        Assertions.assertTrue(node["tags"].isArray)
        Assertions.assertEquals(listOf("solo"), node["tags"].map { it.asText() })

        // A real array is left alone; an absent field stays null (there is nothing to wrap)...
        val real =
            converter.toPayloadWithId(Document("_id", 1).append("tags", listOf("a"))).first.toJson()
        Assertions.assertEquals(listOf("a"), real["tags"].map { it.asText() })
        val absent = converter.toPayloadWithId(Document("_id", 1)).first.toJson()
        Assertions.assertTrue(absent["tags"].isNull)
        // ...but a field *present* with a BSON null is a value, and v2 wrapped it too: [null].
        val presentNull =
            converter.toPayloadWithId(Document("_id", 1).append("tags", null)).first.toJson()
        Assertions.assertTrue(presentNull["tags"].isArray)
        Assertions.assertEquals(1, presentNull["tags"].size())
        Assertions.assertTrue(presentNull["tags"][0].isNull)
    }

    @Test
    fun testAibyteTransformSuffixStringifiesTheField() {
        // v2's escape hatch: a user adds `<field>_aibyte_transform` (string) to the catalog and the
        // field's value is emitted JSON-stringified under it, with the original field nulled.
        val converter =
            MongoDbRecordConverter(
                schemaEnforced = true,
                schemaFieldTypes =
                    mapOf(
                        "_id" to MongoDbFieldType.NUMBER,
                        "addr" to MongoDbFieldType.OBJECT,
                        "addr_aibyte_transform" to MongoDbFieldType.STRING,
                        "name" to MongoDbFieldType.STRING,
                        "name_aibyte_transform" to MongoDbFieldType.STRING,
                    ),
            )
        val node =
            converter
                .toPayloadWithId(
                    Document("_id", 1)
                        .append("addr", Document("city", "Paris").append("zip", 75001))
                        .append("name", "alice"),
                )
                .first
                .toJson()
        // Objects become compact JSON; strings are emitted as-is (asText, not re-quoted).
        Assertions.assertEquals(
            """{"city":"Paris","zip":75001}""",
            node["addr_aibyte_transform"].asText(),
        )
        Assertions.assertEquals("alice", node["name_aibyte_transform"].asText())
        Assertions.assertTrue(node["addr"].isNull)
        Assertions.assertTrue(node["name"].isNull)

        // An absent source field yields a null transform.
        val absent = converter.toPayloadWithId(Document("_id", 1)).first.toJson()
        Assertions.assertTrue(absent["addr_aibyte_transform"].isNull)
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
    fun testDocumentIdRoundTripsAsExtendedJson() {
        // v2 2.1.0: an `_id` that is itself a document is stored as extended JSON (lossless BSON
        // types) and parsed back for the `_id > lastSeen` resume filter.
        val id = Document("tenant", "acme").append("seq", 9007199254740993L)
        val state = MongoDbStreamStateValue.fromLastId(id, MongoDbSnapshotStatus.IN_PROGRESS)
        Assertions.assertEquals(MongoDbIdType.OBJECT, state.idType)
        Assertions.assertTrue(state.id!!.contains("\"\$numberLong\""), state.id)

        val resumed = MongoDbStreamStateValue.fromOpaqueStateValue(state.toOpaqueStateValue())
        val value = resumed.resumeIdValue() as org.bson.BsonDocument
        Assertions.assertEquals("acme", value.getString("tenant").value)
        Assertions.assertEquals(9007199254740993L, value.getInt64("seq").value)
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
