/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbIdType
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import org.bson.BsonBinarySubType
import org.bson.BsonTimestamp
import org.bson.types.Binary
import org.bson.types.ObjectId
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

/**
 * The state the legacy connector persisted, as golden files: the Debezium offset map in the shape
 * `MongoDbDebeziumStateUtil.formatState` wrote it, with the resume token as the hex `_data`
 * (Debezium 2.x, versions ≤ 2.0.x) and as the base64 BSON Debezium 3.x rewrote it to (versions ≥
 * 2.1.0) — the base64 value was produced by Debezium 3.6.2's own `ResumeTokens.toBase64`. Both must
 * yield the same token, and every legacy stream checkpoint must come back as it was.
 */
class MongoDbLegacyStateFixturesTest {

    @ParameterizedTest(name = "{0}")
    @ValueSource(
        strings =
            [
                "legacy-state/v2-2.0-debezium2-hex-token.json",
                "legacy-state/v2-2.1-debezium3-base64-token.json",
            ],
    )
    fun testLegacyStateFixtureIsReadAsIs(resource: String) {
        val message: AirbyteStateMessage =
            Jsons.readValue(ResourceUtils.readResource(resource), AirbyteStateMessage::class.java)

        val cdc: MongoDbCdcState =
            checkNotNull(MongoDbCdcState.fromOpaqueStateValue(message.global.sharedState))
        val token = checkNotNull(cdc.resumeTokenBson())
        Assertions.assertEquals(TOKEN_DATA, token.getString("_data").value)
        Assertions.assertEquals(
            BsonTimestamp(1_690_221_043, 1),
            MongoDbResumeTokens.timestamp(token),
        )
        Assertions.assertEquals(true, cdc.schemaEnforced)
        // Written back, the fixture's own variables are still there, unchanged, for a downgrade.
        val checkpoint = MongoDbCdcState.of(token, true, null, prior = cdc).toOpaqueStateValue()
        Assertions.assertEquals(message.global.sharedState["state"], checkpoint["state"])
        Assertions.assertEquals(
            message.global.sharedState["schema_enforced"],
            checkpoint["schema_enforced"],
        )

        val streams: Map<String, MongoDbStreamStateValue> =
            message.global.streamStates.associate {
                it.streamDescriptor.name to
                    MongoDbStreamStateValue.fromOpaqueStateValue(it.streamState)
            }
        streams.getValue("in_progress").let {
            Assertions.assertEquals(MongoDbSnapshotStatus.IN_PROGRESS, it.status)
            Assertions.assertEquals(ObjectId("650000000000000000000002"), it.resumeIdValue())
        }
        streams.getValue("complete").let {
            Assertions.assertEquals(MongoDbSnapshotStatus.COMPLETE, it.status)
            Assertions.assertEquals(42, it.resumeIdValue())
        }
        streams.getValue("uuid_keyed").let {
            Assertions.assertEquals(MongoDbIdType.BINARY, it.idType)
            val binary = it.resumeIdValue() as Binary
            Assertions.assertEquals(BsonBinarySubType.UUID_STANDARD.value, binary.type)
            Assertions.assertEquals(16, binary.data.size)
        }
        streams.getValue("full_refresh").let {
            Assertions.assertEquals(MongoDbSnapshotStatus.FULL_REFRESH, it.status)
            Assertions.assertEquals("k-10", it.resumeIdValue())
        }
    }

    companion object {
        const val TOKEN_DATA = "8264BEB9F3000000012B0229296E04"
    }
}
