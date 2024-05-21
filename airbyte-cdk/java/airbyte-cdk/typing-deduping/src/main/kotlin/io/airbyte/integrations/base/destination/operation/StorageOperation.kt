/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.time.Instant
import java.util.Optional

interface StorageOperation<Data> {
    /*
     *  ==================== Staging or Raw table Operations ================================
     */

    /**
     * Prepare staging area which cloud be creating any object storage, temp tables or file storage
     */
    fun prepareStage(streamId: StreamId, destinationSyncMode: DestinationSyncMode)

    /** Delete previously staged data, using deterministic information from streamId. */
    fun cleanupStage(streamId: StreamId)

    /** Write data to stage. */
    fun writeToStage(streamId: StreamId, data: Data)

    /*
     *  ==================== Final Table Operations ================================
     */

    /** Create final table extracted from [StreamId] */
    fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean)

    /** Reset the final table using a temp table or ALTER existing table's columns. */
    fun softResetFinalTable(streamConfig: StreamConfig)

    /**
     * Attempt to atomically swap the final table (name and namespace extracted from [StreamId]).
     * This could be destination specific, INSERT INTO..SELECT * and DROP TABLE OR CREATE OR REPLACE
     * ... SELECT *, DROP TABLE
     */
    fun overwriteFinalTable(streamConfig: StreamConfig, tmpTableSuffix: String)

    /**
     */
    fun typeAndDedupe(
        streamConfig: StreamConfig,
        maxProcessedTimestamp: Optional<Instant>,
        finalTableSuffix: String
    )
}
