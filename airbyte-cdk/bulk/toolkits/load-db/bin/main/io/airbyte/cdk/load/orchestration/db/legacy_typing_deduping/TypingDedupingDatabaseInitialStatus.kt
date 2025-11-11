/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatus
import java.time.Instant

data class TypingDedupingDatabaseInitialStatus(
    /** Initial status of the final table, or null if the table doesn't exist yet. */
    val finalTableStatus: FinalTableInitialStatus?,
    val rawTableStatus: RawTableInitialStatus?,
    val tempRawTableStatus: RawTableInitialStatus?,
) : DatabaseInitialStatus

data class FinalTableInitialStatus(
    val isSchemaMismatch: Boolean,
    val isEmpty: Boolean,
    /** The generation ID of _any_ record from the final table, or `null` if the table is empty. */
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
) {
    companion object {
        /**
         * If the raw table doesn't exist, we'll obviously need to create it. After creating a raw
         * table, this is its default state (i.e. it has no records, so there are by definition no
         * unprocessed records, and no processed records).
         */
        val emptyTableStatus = RawTableInitialStatus(false, maxProcessedTimestamp = null)
    }
}

/**
 * Many callers need to do a `create table if not exists`. This is a utility method to update the
 * initial status accordingly - i.e. if the table already existed, retain its status; otherwise, use
 * the empty table status.
 */
fun RawTableInitialStatus?.reify() = this ?: RawTableInitialStatus.emptyTableStatus
