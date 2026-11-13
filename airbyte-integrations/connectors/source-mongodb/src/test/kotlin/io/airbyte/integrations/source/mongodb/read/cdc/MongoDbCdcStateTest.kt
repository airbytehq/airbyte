/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import java.time.Instant
import org.bson.BsonDocument
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * [MongoDbCdcState] must read both its own shape and the legacy `source-mongodb-v2` (Debezium)
 * shape, so existing connections resume on v3 with no clear or refresh.
 */
class MongoDbCdcStateTest {

    @Test
    fun testNativeShapeRoundTrips() {
        val state =
            MongoDbCdcState.of(
                BsonDocument.parse("""{"_data": "$TOKEN"}"""),
                true,
                Instant.parse("2026-10-18T10:00:00Z"),
            )
        val json = state.toOpaqueStateValue()
        Assertions.assertEquals("2026-10-18T10:00:00Z", json["cdcSyncedUntil"].asText())
        val parsed = MongoDbCdcState.fromOpaqueStateValue(json)
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
        Assertions.assertEquals(false, parsed.schemaEnforced)
        // The legacy variables ride along unchanged, so a downgrade resumes from them.
        Assertions.assertEquals(legacy["state"], parsed.legacyState)
        Assertions.assertEquals(legacy["schema_enforced"], parsed.legacySchemaEnforced)
    }

    /**
     * A checkpoint written from a migrated state keeps the legacy `state` and `schema_enforced`
     * byte-for-byte while `resumeToken` moves on; a state that never had them gets none; a reset
     * (no prior state) drops them.
     */
    @Test
    fun testLegacyVariablesAreCarriedVerbatimAndNeverUpdated() {
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
        val prior = MongoDbCdcState.fromOpaqueStateValue(legacy)!!
        val newToken = BsonDocument.parse("""{"_data": "$NEWER_TOKEN"}""")
        val checkpoint =
            MongoDbCdcState.of(newToken, false, Instant.parse("2026-10-20T00:00:00Z"), prior)
                .toOpaqueStateValue()
        Assertions.assertEquals(legacy["state"], checkpoint["state"])
        Assertions.assertEquals(legacy["schema_enforced"], checkpoint["schema_enforced"])
        Assertions.assertEquals(NEWER_TOKEN, checkpoint["resumeToken"]["_data"].asText())
        // Read back: the native token wins over the (older) legacy one.
        val reread = MongoDbCdcState.fromOpaqueStateValue(checkpoint)!!
        Assertions.assertEquals(NEWER_TOKEN, reread.resumeTokenBson()!!.getString("_data").value)
        Assertions.assertEquals(legacy["state"], reread.legacyState)

        val fresh = MongoDbCdcState.of(newToken, true, null).toOpaqueStateValue()
        Assertions.assertFalse(fresh.has("state"), fresh.toString())
        Assertions.assertFalse(fresh.has("schema_enforced"), fresh.toString())
    }

    /** A full-refresh-only sync of a migrated connection: `resumeToken: null` beside the legacy. */
    @Test
    fun testNullResumeTokenFallsBackToTheCarriedLegacyState() {
        val persisted =
            Jsons.readTree(
                """
                {
                  "resumeToken": null,
                  "schemaEnforced": true,
                  "state": {
                    "[\"source-mongodb-v2\",{\"server_id\":\"x\"}]":
                      "{\"sec\":1727740800,\"ord\":1,\"resume_token\":\"$TOKEN\"}"
                  },
                  "schema_enforced": true
                }
                """,
            )
        val parsed = MongoDbCdcState.fromOpaqueStateValue(persisted)!!
        Assertions.assertEquals(TOKEN, parsed.resumeTokenBson()!!.getString("_data").value)
        Assertions.assertEquals(persisted["state"], parsed.legacyState)
    }

    @Test
    fun testLegacyDebezium3Base64TokenYieldsTheSameResumeToken() {
        // v2 2.1.0 (Debezium 3.x) stores the base64-encoded BSON of the whole token document in
        // `resume_token` instead of the hex `_data` string. Both must decode to the same token.
        val tokenDocument = BsonDocument.parse("""{"_data": "$TOKEN"}""")
        val base64 =
            java.util.Base64.getEncoder()
                .encodeToString(
                    org.bson
                        .RawBsonDocument(tokenDocument, org.bson.codecs.BsonDocumentCodec())
                        .byteBuffer
                        .array(),
                )
        val legacy =
            Jsons.readTree(
                """
                {
                  "state": {
                    "[\"source-mongodb-v2\",{\"server_id\":\"x\"}]":
                      "{\"sec\":1727740800,\"ord\":1,\"resume_token\":\"$base64\"}"
                  },
                  "schema_enforced": true
                }
                """,
            )
        val parsed = MongoDbCdcState.fromOpaqueStateValue(legacy)!!
        Assertions.assertEquals(TOKEN, parsed.resumeTokenBson()!!.getString("_data").value)
    }

    @Test
    fun testLegacyNullStateIsAColdStart() {
        // v2 persisted {"state": null, ...} after a full-refresh-only sync.
        val parsed =
            MongoDbCdcState.fromOpaqueStateValue(
                Jsons.readTree("""{"state": null, "schema_enforced": true}"""),
            )!!
        Assertions.assertNull(parsed.resumeTokenBson())
        Assertions.assertEquals(true, parsed.schemaEnforced)
    }

    /** The legacy connector read a missing `schema_enforced` as true. */
    @Test
    fun testLegacyMissingSchemaEnforcedDefaultsToTrue() {
        val parsed = MongoDbCdcState.fromOpaqueStateValue(Jsons.readTree("""{"state": null}"""))!!
        Assertions.assertEquals(true, parsed.schemaEnforced)
        Assertions.assertNull(parsed.resumeTokenBson())
    }

    /** `{}` is what the legacy connector wrote after its first full-refresh-only sync. */
    @Test
    fun testEmptyObjectIsNoState() {
        Assertions.assertNull(MongoDbCdcState.fromOpaqueStateValue(Jsons.readTree("{}")))
        Assertions.assertNull(MongoDbCdcState.fromOpaqueStateValue(Jsons.readTree("null")))
    }

    /** A native state without the flag (hand-edited or older) leaves it to the configuration. */
    @Test
    fun testNativeShapeWithoutSchemaEnforcedIsNull() {
        val parsed =
            MongoDbCdcState.fromOpaqueStateValue(
                Jsons.readTree("""{"resumeToken": {"_data": "$TOKEN"}}"""),
            )!!
        Assertions.assertNull(parsed.schemaEnforced)
        Assertions.assertEquals(TOKEN, parsed.resumeTokenBson()!!.getString("_data").value)
    }

    /** Per-replica-set offsets: accepted when every entry holds the same token, else rejected. */
    @Test
    fun testMultiEntryOffsets() {
        fun entry(key: String, token: String) =
            "\"$key\": \"{\\\"sec\\\":1,\\\"ord\\\":1,\\\"resume_token\\\":\\\"$token\\\"}\""
        val same =
            Jsons.readTree(
                """{"state": {${entry("rs0", TOKEN)}, ${entry("rs1", TOKEN)}}, "schema_enforced": true}""",
            )
        Assertions.assertEquals(
            TOKEN,
            MongoDbCdcState.fromOpaqueStateValue(same)!!.resumeTokenBson()!!.getString("_data")
                .value,
        )
        val different =
            Jsons.readTree(
                """{"state": {${entry("rs0", TOKEN)}, ${entry("rs1", OTHER_TOKEN)}}, "schema_enforced": true}""",
            )
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MongoDbCdcState.fromOpaqueStateValue(different)
            }
        Assertions.assertTrue(e.message!!.contains("one per shard"), e.message)
    }

    @Test
    fun testMigrationFailsOnEveryUnexpectedShape() {
        // Each expected key is checked; nothing is assumed, and nothing silently cold-starts.
        val cases =
            listOf(
                // state is not an offset map
                """{"state": "not-a-map", "schema_enforced": true}""",
                """{"state": {}, "schema_enforced": true}""",
                """{"state": {"a": "{}", "b": "{}"}, "schema_enforced": true}""",
                // the offset value is not a JSON string / not valid JSON
                """{"state": {"k": 42}, "schema_enforced": true}""",
                """{"state": {"k": "not json"}, "schema_enforced": true}""",
                // the offset has no textual resume_token
                """{"state": {"k": "{\"sec\":1,\"ord\":1}"}, "schema_enforced": true}""",
                """{"state": {"k": "{\"resume_token\":7}"}, "schema_enforced": true}""",
                // the token is neither hex nor base64 BSON
                """{"state": {"k": "{\"resume_token\":\"not*valid\"}"}, "schema_enforced": true}""",
            )
        for (case in cases) {
            val e =
                Assertions.assertThrows(
                    ConfigErrorException::class.java,
                    { MongoDbCdcState.fromOpaqueStateValue(Jsons.readTree(case)) },
                    case,
                )
            Assertions.assertTrue(
                e.message!!.startsWith(
                    "Failed to migrate to the new connector version state protocol",
                ),
                e.message,
            )
        }
    }

    @Test
    fun testNoStateIsNull() {
        Assertions.assertNull(MongoDbCdcState.fromOpaqueStateValue(null))
    }

    companion object {
        /** A real-looking `_data` (timestamp 1727740800, inc 1, change-stream version 1). */
        const val TOKEN = "826703D5800000000129295A1004"
        const val NEWER_TOKEN = "8268000000000000000129295A1004"
        /** Same shape, a later timestamp. */
        const val OTHER_TOKEN = "826703D5810000000129295A1004"
    }
}
