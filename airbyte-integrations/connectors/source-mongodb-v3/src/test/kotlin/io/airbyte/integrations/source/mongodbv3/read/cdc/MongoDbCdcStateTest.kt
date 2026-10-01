/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import org.bson.BsonDocument
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * [MongoDbCdcState] must read both its own shape and the legacy `source-mongodb-v2` (Debezium)
 * shape, so existing connections resume on v3 without a reset.
 */
class MongoDbCdcStateTest {

    @Test
    fun testNativeShapeRoundTrips() {
        val state = MongoDbCdcState.of(BsonDocument.parse("""{"_data": "$TOKEN"}"""), true)
        val parsed = MongoDbCdcState.fromOpaqueStateValue(state.toOpaqueStateValue())
        Assertions.assertEquals(state, parsed)
        Assertions.assertEquals(TOKEN, parsed!!.resumeTokenBson()!!.getString("_data").value)
    }

    @Test
    fun testLegacyDebeziumShapeYieldsTheSameResumeToken() {
        // Exactly what v2's MongoDbDebeziumStateUtil.formatState persists in `shared_state`:
        // a one-entry offset map whose key and value are both serialized JSON strings.
        val legacy =
            Jsons.readTree(
                """
                {
                  "state": {
                    "[\"source-mongodb-v2\",{\"server_id\":\"cluster0.abcd1.mongodb.net\"}]":
                      "{\"sec\":1727740800,\"ord\":1,\"resume_token\":\"$TOKEN\"}"
                  },
                  "schema_enforced": false
                }
                """,
            )
        val parsed = MongoDbCdcState.fromOpaqueStateValue(legacy)!!
        Assertions.assertEquals(TOKEN, parsed.resumeTokenBson()!!.getString("_data").value)
        Assertions.assertFalse(parsed.schemaEnforced)
    }

    @Test
    fun testLegacyNullStateIsAColdStart() {
        // v2 persisted {"state": null, ...} after a full-refresh-only sync.
        val parsed =
            MongoDbCdcState.fromOpaqueStateValue(
                Jsons.readTree("""{"state": null, "schema_enforced": true}"""),
            )!!
        Assertions.assertNull(parsed.resumeTokenBson())
        Assertions.assertTrue(parsed.schemaEnforced)
    }

    @Test
    fun testLegacyMissingSchemaEnforcedDefaultsToTrue() {
        val parsed = MongoDbCdcState.fromOpaqueStateValue(Jsons.readTree("""{"state": null}"""))!!
        Assertions.assertTrue(parsed.schemaEnforced)
    }

    @Test
    fun testLegacyOffsetWithoutTokenFailsLoudly() {
        val corrupt =
            Jsons.readTree(
                """{"state": {"[\"x\",{}]": "{\"sec\":1,\"ord\":1}"}, "schema_enforced": true}""",
            )
        Assertions.assertThrows(ConfigErrorException::class.java) {
            MongoDbCdcState.fromOpaqueStateValue(corrupt)
        }
    }

    @Test
    fun testNoStateIsNull() {
        Assertions.assertNull(MongoDbCdcState.fromOpaqueStateValue(null))
    }

    companion object {
        /** A real-looking `_data` (timestamp 1727740800, inc 1, change-stream version 1). */
        const val TOKEN = "826703D5800000000129295A1004"
    }
}
