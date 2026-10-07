/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.snapshot

import io.airbyte.cdk.util.Jsons
import java.nio.ByteBuffer
import java.util.Date
import java.util.UUID
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.types.Binary
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

/**
 * A checkpointed `_id` must come back as the same native BSON value after the JSON round trip, for
 * every supported `_id` type, so the resume filter compares like with like.
 */
class MongoDbStreamStateValueTest {

    @ParameterizedTest(name = "{1} {2}")
    @MethodSource("ids")
    fun testIdRoundTrip(lastId: Any, idType: MongoDbIdType, idText: String) {
        val checkpoint: MongoDbStreamStateValue =
            MongoDbStreamStateValue.fromLastId(lastId, MongoDbSnapshotStatus.IN_PROGRESS)
        Assertions.assertEquals(idType, checkpoint.idType)
        Assertions.assertEquals(idText, checkpoint.id)
        val json = checkpoint.toOpaqueStateValue()
        Assertions.assertEquals(STATE_KEYS, json.fieldNames().asSequence().toSet())
        val restored: MongoDbStreamStateValue = MongoDbStreamStateValue.fromOpaqueStateValue(json)
        Assertions.assertEquals(checkpoint, restored)
        Assertions.assertEquals(lastId, restored.resumeIdValue())
    }

    @Test
    fun testDocumentIdRoundTrip() {
        val lastId = Document("tenant", "acme").append("seq", 2L)
        val checkpoint: MongoDbStreamStateValue =
            MongoDbStreamStateValue.fromLastId(lastId, MongoDbSnapshotStatus.IN_PROGRESS)
        Assertions.assertEquals(MongoDbIdType.OBJECT, checkpoint.idType)
        Assertions.assertEquals(
            """{"tenant": "acme", "seq": {"${'$'}numberLong": "2"}}""",
            checkpoint.id
        )
        val restored: MongoDbStreamStateValue =
            MongoDbStreamStateValue.fromOpaqueStateValue(checkpoint.toOpaqueStateValue())
        Assertions.assertEquals(lastId.toBsonDocument(), restored.resumeIdValue() as BsonDocument)
    }

    @Test
    fun testNoIdMeansNoResumeFilter() {
        val checkpoint: MongoDbStreamStateValue =
            MongoDbStreamStateValue.fromLastId(null, MongoDbSnapshotStatus.FULL_REFRESH)
        Assertions.assertNull(checkpoint.id)
        Assertions.assertNull(checkpoint.resumeIdValue())
    }

    /** An `_id` type with no dedicated encoding resumes from its text; never a failure. */
    @Test
    fun testOtherIdTypeFallsBackToText() {
        val checkpoint: MongoDbStreamStateValue =
            MongoDbStreamStateValue.fromLastId(true, MongoDbSnapshotStatus.IN_PROGRESS)
        Assertions.assertEquals(MongoDbIdType.STRING, checkpoint.idType)
        Assertions.assertEquals("true", checkpoint.id)
    }

    /** The persisted shape of `source-mongodb-v2`, key names included. */
    @Test
    fun testLegacyStateShape() {
        val legacy =
            Jsons.readTree(
                """{"id":"650000000000000000000001","status":"IN_PROGRESS","idType":"OBJECT_ID","binarySubType":0}"""
            )
        val restored: MongoDbStreamStateValue = MongoDbStreamStateValue.fromOpaqueStateValue(legacy)
        Assertions.assertEquals(ObjectId("650000000000000000000001"), restored.resumeIdValue())
        Assertions.assertEquals(MongoDbSnapshotStatus.IN_PROGRESS, restored.status)
    }

    companion object {
        val STATE_KEYS: Set<String> = setOf("id", "status", "idType", "binarySubType")

        private val uuid: UUID = UUID.fromString("12345678-1234-5678-1234-567812345678")
        private val uuidBytes: ByteArray =
            ByteBuffer.allocate(16)
                .putLong(uuid.mostSignificantBits)
                .putLong(uuid.leastSignificantBits)
                .array()

        @JvmStatic
        fun ids(): List<Arguments> =
            listOf(
                Arguments.of(
                    ObjectId("650000000000000000000001"),
                    MongoDbIdType.OBJECT_ID,
                    "650000000000000000000001",
                ),
                Arguments.of(7, MongoDbIdType.INT, "7"),
                Arguments.of(7L, MongoDbIdType.LONG, "7"),
                Arguments.of("k", MongoDbIdType.STRING, "k"),
                Arguments.of(Binary(0, byteArrayOf(1, 2)), MongoDbIdType.BINARY, "AQI="),
                Arguments.of(Binary(4, uuidBytes), MongoDbIdType.BINARY, uuid.toString()),
                Arguments.of(1.5, MongoDbIdType.DOUBLE, "1.5"),
                Arguments.of(1e300, MongoDbIdType.DOUBLE, "1.0E300"),
                Arguments.of(-0.0, MongoDbIdType.DOUBLE, "-0.0"),
                Arguments.of(Double.NaN, MongoDbIdType.DOUBLE, "NaN"),
                Arguments.of(Double.POSITIVE_INFINITY, MongoDbIdType.DOUBLE, "Infinity"),
                Arguments.of(Decimal128.parse("12.340"), MongoDbIdType.DECIMAL, "12.340"),
                Arguments.of(Decimal128.parse("1E+6000"), MongoDbIdType.DECIMAL, "1E+6000"),
                Arguments.of(Decimal128.NaN, MongoDbIdType.DECIMAL, "NaN"),
                Arguments.of(Decimal128.NEGATIVE_INFINITY, MongoDbIdType.DECIMAL, "-Infinity"),
                Arguments.of(Date(1_700_000_000_123L), MongoDbIdType.DATE, "1700000000123"),
                Arguments.of(Date(-86_400_000L), MongoDbIdType.DATE, "-86400000"),
                Arguments.of(
                    BsonTimestamp(1_700_000_000, 2),
                    MongoDbIdType.TIMESTAMP,
                    BsonTimestamp(1_700_000_000, 2).value.toString(),
                ),
            )
    }
}
