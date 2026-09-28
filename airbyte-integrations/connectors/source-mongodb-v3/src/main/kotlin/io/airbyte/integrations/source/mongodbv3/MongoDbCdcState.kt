/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import org.bson.BsonDocument

/**
 * State of the `Global` (change-stream) feed. Holds the change-stream resume token and the
 * `schema_enforced` flag under which it was captured, so a resumed sync reads the correct shape.
 *
 * This is a **native** shape, not the legacy Debezium offset: `source-mongodb-v3` reads the change
 * stream with the MongoDB driver's `watch()` rather than Debezium, so existing v2 CDC connections
 * cannot resume from their persisted offset and must be reset. Snapshot (`MongoDbStreamStateValue`)
 * state stays legacy-compatible; only the CDC offset format differs.
 */
data class MongoDbCdcState(
    val resumeToken: JsonNode?,
    val schemaEnforced: Boolean,
) {
    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(this)

    /** The resume token as a [BsonDocument] the driver can resume from, or null on cold start. */
    fun resumeTokenBson(): BsonDocument? =
        resumeToken?.let { BsonDocument.parse(Jsons.writeValueAsString(it)) }

    companion object {
        fun fromOpaqueStateValue(state: OpaqueStateValue?): MongoDbCdcState? =
            state?.let { Jsons.treeToValue(it, MongoDbCdcState::class.java) }

        fun of(resumeToken: BsonDocument?, schemaEnforced: Boolean): MongoDbCdcState =
            MongoDbCdcState(
                resumeToken = resumeToken?.let { Jsons.readTree(it.toJson()) },
                schemaEnforced = schemaEnforced,
            )
    }
}
