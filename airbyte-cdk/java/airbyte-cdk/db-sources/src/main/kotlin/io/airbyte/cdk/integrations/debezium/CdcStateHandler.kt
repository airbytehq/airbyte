/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage
import io.airbyte.protocol.models.v0.AirbyteMessage

/**
 * This interface is used to allow connectors to save the offset and schema history in the manner
 * which suits them. Also, it adds some utils to verify CDC event status.
 */
interface CdcStateHandler {
    fun saveState(
        offset: Map<String, String>,
        dbHistory: AirbyteSchemaHistoryStorage.SchemaHistory<String>?
    ): AirbyteMessage?

    fun saveStateAfterCompletionOfSnapshotOfNewStreams(): AirbyteMessage?

    fun compressSchemaHistoryForState(): Boolean {
        return false
    }

    val isCdcCheckpointEnabled: Boolean
        /**
         * This function is used as feature flag for sending state messages as checkpoints in CDC
         * syncs.
         *
         * @return Returns `true` if checkpoint state messages are enabled for CDC syncs. Otherwise,
         * it returns `false`
         */
        get() = false
}
