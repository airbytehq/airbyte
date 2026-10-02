/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.cdc

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import java.util.Base64
import org.bson.BsonDocument
import org.bson.BsonString
import org.bson.RawBsonDocument

/**
 * State of the `Global` (change-stream) feed: the resume token and the `schema_enforced` flag it
 * was captured under. Two persisted shapes are read, only the first is written:
 * - **Native:** `{"resumeToken": {"_data": "<hex>"}, "schemaEnforced": true}`.
 * - **Debezium offset:** `{"state": <offset map>, "schema_enforced": true}`, where the offset map
 * has one entry whose value is a JSON string `{"sec": ..., "ord": ..., "resume_token": "<token>"}`
 * and the token is either the hex `_data` string or the base64-encoded BSON of the token document.
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
        private const val DEBEZIUM_STATE = "state"
        private const val DEBEZIUM_SCHEMA_ENFORCED = "schema_enforced"
        private const val DEBEZIUM_RESUME_TOKEN = "resume_token"

        fun of(resumeToken: BsonDocument?, schemaEnforced: Boolean): MongoDbCdcState =
            MongoDbCdcState(
                resumeToken = resumeToken?.let { Jsons.readTree(it.toJson()) },
                schemaEnforced = schemaEnforced,
            )

        /** Parses either persisted shape; null when there is no state at all (first sync). */
        fun fromOpaqueStateValue(state: OpaqueStateValue?): MongoDbCdcState? =
            when {
                state == null -> null
                state.has(DEBEZIUM_STATE) -> fromDebeziumOffset(state)
                else -> Jsons.treeToValue(state, MongoDbCdcState::class.java)
            }

        /**
         * Reads the Debezium-offset shape. A null `state` means no CDC position yet (cold start); a
         * non-null offset map without a resume token is corrupt, so it fails loudly rather than
         * silently cold-starting and replaying the oplog. A missing `schema_enforced` means true.
         */
        private fun fromDebeziumOffset(persisted: JsonNode): MongoDbCdcState {
            val schemaEnforced: Boolean = persisted[DEBEZIUM_SCHEMA_ENFORCED]?.asBoolean() ?: true
            val offsets: JsonNode = persisted[DEBEZIUM_STATE]
            if (offsets == null || offsets.isNull) {
                return MongoDbCdcState(resumeToken = null, schemaEnforced = schemaEnforced)
            }
            val resumeTokenData: String =
                offsets
                    .elements()
                    .asSequence()
                    .filter { it.isTextual }
                    .mapNotNull { runCatching { Jsons.readTree(it.asText()) }.getOrNull() }
                    .firstNotNullOfOrNull { it[DEBEZIUM_RESUME_TOKEN]?.asText() }
                    ?: throw ConfigErrorException(
                        "The saved CDC state is a Debezium offset without " +
                            "a resume token and cannot be resumed from. Please reset the connection.",
                    )
            return of(resumeTokenFromOffsetValue(resumeTokenData), schemaEnforced)
        }

        /**
         * The resume token in a Debezium offset: the hex `_data` string (Debezium 2.x) or the
         * base64-encoded BSON of the whole token document (Debezium 3.x).
         */
        private fun resumeTokenFromOffsetValue(value: String): BsonDocument =
            if (HEX_RESUME_TOKEN_DATA.matches(value)) {
                BsonDocument("_data", BsonString(value))
            } else {
                RawBsonDocument(Base64.getDecoder().decode(value))
            }

        private val HEX_RESUME_TOKEN_DATA = Regex("^[0-9A-Fa-f]+$")
    }
}
