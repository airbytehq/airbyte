/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.cdc

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import org.bson.BsonDocument

/**
 * State of the `Global` (change-stream) feed: the change-stream resume token and the
 * `schema_enforced` flag under which it was captured, so a resumed sync reads the correct shape.
 *
 * Two persisted shapes are understood, so an existing `source-mongodb-v2` connection resumes on v3
 * **without a reset or migration**:
 * - **Native (v3 writes this):** `{"resumeToken": {"_data": "<hex>"}, "schemaEnforced": true}`.
 * - **Legacy (v2 / Debezium):** `{"state": <Debezium offset map>, "schema_enforced": true}`, where
 * the offset map has one entry whose value is a JSON string `{"sec": ..., "ord": ...,
 * "resume_token": "<hex>"}`. Debezium stores the server's own resume token verbatim, so
 * `resume_token` is exactly the `_data` v3 hands to `resumeAfter()`.
 */
data class MongoDbCdcState(
    @JsonProperty("resumeToken") val resumeToken: JsonNode?,
    @JsonProperty("schemaEnforced") val schemaEnforced: Boolean,
) {
    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(this)

    /** The resume token as a [BsonDocument] the driver can resume from, or null on cold start. */
    fun resumeTokenBson(): BsonDocument? =
        resumeToken?.let { BsonDocument.parse(Jsons.writeValueAsString(it)) }

    companion object {
        private const val LEGACY_STATE = "state"
        private const val LEGACY_SCHEMA_ENFORCED = "schema_enforced"
        private const val LEGACY_RESUME_TOKEN = "resume_token"

        fun of(resumeToken: BsonDocument?, schemaEnforced: Boolean): MongoDbCdcState =
            MongoDbCdcState(
                resumeToken = resumeToken?.let { Jsons.readTree(it.toJson()) },
                schemaEnforced = schemaEnforced,
            )

        /** Parses either persisted shape; null when there is no state at all (first sync). */
        fun fromOpaqueStateValue(state: OpaqueStateValue?): MongoDbCdcState? =
            when {
                state == null -> null
                state.has(LEGACY_STATE) -> fromLegacy(state)
                else -> Jsons.treeToValue(state, MongoDbCdcState::class.java)
            }

        /**
         * Adapts a legacy v2 (Debezium) CDC state. A null `state` is what v2 persisted after a
         * full-refresh-only sync and means "no CDC position yet" (cold start). A non-null offset
         * map without a resume token is corrupt rather than empty, so it fails loudly instead of
         * silently cold-starting and replaying the oplog.
         */
        private fun fromLegacy(legacy: JsonNode): MongoDbCdcState {
            // v2 defaulted a missing flag to true (schema_enforced was added after the first
            // release).
            val schemaEnforced: Boolean = legacy[LEGACY_SCHEMA_ENFORCED]?.asBoolean() ?: true
            val offsets: JsonNode = legacy[LEGACY_STATE]
            if (offsets == null || offsets.isNull) {
                return MongoDbCdcState(resumeToken = null, schemaEnforced = schemaEnforced)
            }
            val resumeTokenData: String =
                offsets
                    .elements()
                    .asSequence()
                    .filter { it.isTextual }
                    .mapNotNull { runCatching { Jsons.readTree(it.asText()) }.getOrNull() }
                    .firstNotNullOfOrNull { it[LEGACY_RESUME_TOKEN]?.asText() }
                    ?: throw ConfigErrorException(
                        "The saved CDC state is a legacy source-mongodb-v2 Debezium offset without " +
                            "a resume token and cannot be resumed from. Please reset the connection.",
                    )
            return MongoDbCdcState(
                resumeToken = Jsons.objectNode().put("_data", resumeTokenData),
                schemaEnforced = schemaEnforced,
            )
        }
    }
}
