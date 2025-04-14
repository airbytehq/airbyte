package io.airbyte.cdk.load.orchestration.legacy_typing_deduping

import io.airbyte.cdk.load.orchestration.DestinationInitialStatus
import java.time.Instant

data class TypingDedupingDestinationInitialStatus(
    /**
     * Initial status of the final table, or null if the table doesn't exist yet.
     */
    val finalTableStatus: FinalTableInitialStatus?,
    val rawTableStatus: RawTableInitialStatus?,
    val tempRawTableStatus: RawTableInitialStatus?,
) : DestinationInitialStatus

data class FinalTableInitialStatus(
    val isSchemaMismatch: Boolean,
    val isEmpty: Boolean,
    /**
     * The generation ID of _any_ record from the final table, or `null` if the table is empty.
     */
    val finalTableGenerationId: Long?,
)

data class RawTableInitialStatus(
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
