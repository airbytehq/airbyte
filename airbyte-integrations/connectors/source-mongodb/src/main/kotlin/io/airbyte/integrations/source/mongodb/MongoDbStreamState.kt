/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons

/**
 * Serializable state for MongoDB stream reads.
 *
 * Tracks the `_id` checkpoint for resumable full refresh reads.
 * When a read is interrupted, the next read can resume from the last `_id` value.
 */
data class MongoDbStreamState(
    @JsonProperty("state_type")
    val stateType: String,

    @JsonProperty("id")
    val id: String? = null,
) {
    companion object {
        /** State indicating a snapshot has completed (no more data to read). */
        val snapshotCompleted: OpaqueStateValue =
            Jsons.valueToTree(mapOf("state_type" to "snapshot_completed"))

        /** Create an incomplete state checkpoint with the last _id value read. */
        fun snapshotCheckpoint(lastIdValue: String): OpaqueStateValue =
            Jsons.valueToTree(
                MongoDbStreamState(
                    stateType = "primary_key",
                    id = lastIdValue,
                )
            )

        /** Parse a saved state value back to [MongoDbStreamState]. */
        fun fromOpaqueStateValue(stateValue: JsonNode): MongoDbStreamState =
            Jsons.treeToValue(stateValue, MongoDbStreamState::class.java)
    }
}
