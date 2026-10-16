/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.read.MongoDbStateMigration
import java.util.Base64
import org.bson.BsonDocument
import org.bson.BsonString
import org.bson.RawBsonDocument

/**
 * `Global` (change-stream) feed state: the resume token and the `schema_enforced` it was captured
 * under. Written as `{"resumeToken": {"_data": ..}, "schemaEnforced": ..}`; also read from the
 * Debezium offset shape `{"state": {<key>: "{\"sec\":..,\"ord\":..,\"resume_token\":..}"},
 * "schema_enforced": ..}`.
 */
data class MongoDbCdcState(
    @JsonProperty("resumeToken") val resumeToken: JsonNode?,
    /** Null when the persisted state carries no flag: the configuration's value applies. */
    @JsonProperty("schemaEnforced") val schemaEnforced: Boolean?,
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

        /**
         * Parses either persisted shape; null when there is no state at all (first sync, or the
         * empty object the legacy connector wrote after a full-refresh-only sync).
         */
        fun fromOpaqueStateValue(state: OpaqueStateValue?): MongoDbCdcState? =
            when {
                state == null || state.isNull || (state.isObject && state.isEmpty) -> null
                state.has(DEBEZIUM_STATE) -> fromDebeziumOffset(state)
                else -> Jsons.treeToValue(state, MongoDbCdcState::class.java)
            }

        /**
         * Migrates the Debezium-offset shape, checking every expected key; a mismatch fails the
         * sync rather than cold-starting (which would replay the oplog). A JSON-null `state` means
         * no position yet (persisted after a full-refresh-only sync) and cold-starts. A missing
         * `schema_enforced` means `true`, as the legacy connector read it. Debezium keyed offsets
         * per replica set: one entry per shard in its old `replica_set` connection mode. Such
         * per-shard tokens cannot resume a cluster-wide stream, so several entries are accepted
         * only when they carry the same token.
         */
        private fun fromDebeziumOffset(persisted: JsonNode): MongoDbCdcState {
            val schemaEnforcedNode: JsonNode? = persisted[DEBEZIUM_SCHEMA_ENFORCED]
            val schemaEnforced: Boolean =
                if (schemaEnforcedNode?.isBoolean == true) schemaEnforcedNode.asBoolean() else true
            val offsets: JsonNode = persisted[DEBEZIUM_STATE]
            if (offsets.isNull) {
                return MongoDbCdcState(resumeToken = null, schemaEnforced = schemaEnforced)
            }
            MongoDbStateMigration.require(offsets.isObject && offsets.size() >= 1) {
                "'$DEBEZIUM_STATE' must be a non-empty offset map, got $offsets"
            }
            val tokens: Set<String> =
                offsets
                    .elements()
                    .asSequence()
                    .map { offsetValue: JsonNode ->
                        MongoDbStateMigration.require(offsetValue.isTextual) {
                            "the offset value must be a JSON string, got $offsetValue"
                        }
                        val offset: JsonNode =
                            runCatching { Jsons.readTree(offsetValue.asText()) }
                                .getOrElse {
                                    MongoDbStateMigration.failure(
                                        "the offset value is not valid JSON: ${offsetValue.asText()}",
                                        it
                                    )
                                }
                        val token: JsonNode? = offset[DEBEZIUM_RESUME_TOKEN]
                        MongoDbStateMigration.require(token?.isTextual == true) {
                            "the offset has no textual '$DEBEZIUM_RESUME_TOKEN', got $offset"
                        }
                        token!!.asText()
                    }
                    .toSet()
            MongoDbStateMigration.require(tokens.size == 1) {
                "'$DEBEZIUM_STATE' holds ${tokens.size} different resume tokens (one per shard, " +
                    "from a per-replica-set configuration); they cannot resume a cluster-wide " +
                    "change stream"
            }
            return of(migrateDebeziumResumeToken(tokens.single()), schemaEnforced)
        }

        /** The offset's token: hex `_data` (Debezium 2.x) or base64 BSON document (3.x). */
        private fun migrateDebeziumResumeToken(value: String): BsonDocument =
            if (HEX_RESUME_TOKEN_DATA.matches(value)) {
                BsonDocument("_data", BsonString(value))
            } else {
                runCatching {
                        RawBsonDocument(Base64.getDecoder().decode(value)).also { it.toJson() }
                    }
                    .getOrElse {
                        MongoDbStateMigration.failure(
                            "'$DEBEZIUM_RESUME_TOKEN' is neither hex nor base64 BSON: $value",
                            it
                        )
                    }
            }

        private val HEX_RESUME_TOKEN_DATA = Regex("^[0-9A-Fa-f]+$")
    }
}
