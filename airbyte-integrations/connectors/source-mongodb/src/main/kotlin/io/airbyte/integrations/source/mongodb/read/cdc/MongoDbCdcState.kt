/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import com.fasterxml.jackson.annotation.JsonFormat
import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.read.MongoDbStateMigration
import java.time.Instant
import java.util.Base64
import org.bson.BsonDocument
import org.bson.BsonString
import org.bson.RawBsonDocument

/**
 * `Global` (change-stream) feed state: the resume token, the `schema_enforced` it was captured
 * under and the token's oplog time, written as `{"resumeToken": {"_data": ..}, "schemaEnforced":
 * .., "cdcSyncedUntil": "2026-..Z"}`. A state migrated from the legacy connector also carries its
 * Debezium offset verbatim and forever (`{"state": {<key>: "{\"sec\":..,\"ord\":..,
 * \"resume_token\":..}"}, "schema_enforced": ..}`): [resumeToken] is created from it on the first
 * read and is the only position this connector reads or updates afterwards, while a downgrade to
 * 2.x resumes from the legacy variables, i.e. from the position saved before the upgrade.
 */
data class MongoDbCdcState(
    @JsonProperty("resumeToken") val resumeToken: JsonNode?,
    /** Null when the persisted state carries no flag: the configuration's value applies. */
    @JsonProperty("schemaEnforced") val schemaEnforced: Boolean?,
    /**
     * The oplog time (seconds) of [resumeToken]: the `_ab_cdc_cursor` of the snapshot rows read
     * under it. Every event a later sync replays is strictly after the token, so those rows always
     * lose to the changes that supersede them, whichever node served the snapshot. The snapshot
     * readers take it from the `Global` feed's checkpoint, which precedes them; null for a migrated
     * Debezium offset (its first checkpoint sets it).
     */
    @JsonProperty("cdcSyncedUntil")
    @JsonFormat(shape = JsonFormat.Shape.STRING)
    val cdcSyncedUntil: Instant? = null,
    /** The legacy Debezium offset map, carried as it was migrated; never updated. */
    @JsonProperty(LEGACY_STATE)
    @JsonInclude(JsonInclude.Include.NON_NULL)
    val legacyState: JsonNode? = null,
    /** The legacy `schema_enforced` flag, carried as it was migrated; never updated. */
    @JsonProperty(LEGACY_SCHEMA_ENFORCED)
    @JsonInclude(JsonInclude.Include.NON_NULL)
    val legacySchemaEnforced: JsonNode? = null,
) {
    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(this)

    /** The resume token as a [BsonDocument] the driver can resume from, or null on cold start. */
    fun resumeTokenBson(): BsonDocument? =
        resumeToken
            ?.takeUnless { it.isNull }
            ?.let { BsonDocument.parse(Jsons.writeValueAsString(it)) }

    companion object {
        const val LEGACY_STATE = "state"
        const val LEGACY_SCHEMA_ENFORCED = "schema_enforced"
        private const val RESUME_TOKEN = "resumeToken"
        private const val DEBEZIUM_RESUME_TOKEN = "resume_token"

        /**
         * A checkpoint for [resumeToken]; [prior], the state the read started from, lends its
         * legacy variables so they are carried unchanged (none after a reset, or on a connection
         * that never ran the legacy connector).
         */
        fun of(
            resumeToken: BsonDocument?,
            schemaEnforced: Boolean,
            cdcSyncedUntil: Instant?,
            prior: MongoDbCdcState? = null,
        ): MongoDbCdcState =
            MongoDbCdcState(
                resumeToken = resumeToken?.let { Jsons.readTree(it.toJson()) },
                schemaEnforced = schemaEnforced,
                cdcSyncedUntil = cdcSyncedUntil,
                legacyState = prior?.legacyState,
                legacySchemaEnforced = prior?.legacySchemaEnforced,
            )

        /**
         * Parses a persisted state; null when there is none at all (first sync, or the empty object
         * the legacy connector wrote after a full-refresh-only sync). A `resumeToken` is used as
         * is; without one, a legacy `state` is migrated into it (a full-refresh-only sync of a
         * migrated connection writes `resumeToken: null` beside the carried legacy variables).
         */
        fun fromOpaqueStateValue(state: OpaqueStateValue?): MongoDbCdcState? =
            when {
                state == null || state.isNull || (state.isObject && state.isEmpty) -> null
                state[RESUME_TOKEN]?.isNull == false ->
                    Jsons.treeToValue(state, MongoDbCdcState::class.java)
                state.has(LEGACY_STATE) -> fromDebeziumOffset(state)
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
            val legacySchemaEnforced: JsonNode? = persisted[LEGACY_SCHEMA_ENFORCED]
            val nativeSchemaEnforced: JsonNode? = persisted["schemaEnforced"]
            val schemaEnforced: Boolean =
                when {
                    nativeSchemaEnforced?.isBoolean == true -> nativeSchemaEnforced.asBoolean()
                    legacySchemaEnforced?.isBoolean == true -> legacySchemaEnforced.asBoolean()
                    else -> true
                }
            val offsets: JsonNode = persisted[LEGACY_STATE]
            if (offsets.isNull) {
                return MongoDbCdcState(
                    resumeToken = null,
                    schemaEnforced = schemaEnforced,
                    legacySchemaEnforced = legacySchemaEnforced,
                )
            }
            MongoDbStateMigration.require(offsets.isObject && offsets.size() >= 1) {
                "'$LEGACY_STATE' must be a non-empty offset map, got $offsets"
            }
            val tokens: Set<String> =
                offsets
                    .elements()
                    .asSequence()
                    .map { offsetValue: JsonNode ->
                        MongoDbStateMigration.require(offsetValue.isTextual) {
                            "the offset value must be a JSON string, got $offsetValue"
                        }
                        val offset: JsonNode = runCatching {
                            Jsons.readTree(offsetValue.asText())
                        }
                            .getOrElse {
                                MongoDbStateMigration.failure(
                                    "the offset value is not valid JSON: ${offsetValue.asText()}",
                                    it,
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
                "'$LEGACY_STATE' holds ${tokens.size} different resume tokens (one per shard, " +
                    "from a per-replica-set configuration); they cannot resume a cluster-wide " +
                    "change stream"
            }
            return MongoDbCdcState(
                resumeToken = Jsons.readTree(migrateDebeziumResumeToken(tokens.single()).toJson()),
                schemaEnforced = schemaEnforced,
                legacyState = offsets,
                legacySchemaEnforced = legacySchemaEnforced,
            )
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
                            it,
                        )
                    }
            }

        private val HEX_RESUME_TOKEN_DATA = Regex("^[0-9A-Fa-f]+$")
    }
}
