/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.probably_core_stuff

import io.airbyte.cdk.load.command.DestinationStream
import java.time.Instant

data class DestinationInitialStatus<DestinationState>(
    val stream: DestinationStream,
    val initialRawTableStatus: InitialRawTableStatus?,
    val initialTempRawTableStatus: InitialRawTableStatus?,
    val initialFinalTableStatus: InitialFinalTableStatus?,
    val tempFinalTableGenerationId: Long?,
    // TODO are there any destinations that actually successfully use this?
    val destinationState: DestinationState,
)

data class InitialRawTableStatus(
    /**
     * Whether there were any records with null `_airbyte_loaded_at`, at the time that this status
     * was fetched.
     */
    val hasUnprocessedRecords: Boolean,
    /**
     * The highest timestamp such that all records in `SELECT * FROM raw_table WHERE
     * _airbyte_extracted_at <= ?` have a nonnull `_airbyte_loaded_at`.
     *
     * Destinations MAY use this value to only run T+D on records with `_airbyte_extracted_at > ?`
     * (note the strictly-greater comparison).
     */
    val maxProcessedTimestamp: Instant?,
)

data class InitialFinalTableStatus(
    /** An arbitrary generation ID from a record in the table, or null if the table is empty */
    val generationId: Long?,
    val schemaMismatch: Boolean,
) {
    val isEmpty = generationId == null
}
