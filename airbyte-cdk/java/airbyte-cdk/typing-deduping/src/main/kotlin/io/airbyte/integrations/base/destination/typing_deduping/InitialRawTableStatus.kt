/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.time.Instant
import java.util.*

data class InitialRawTableStatus(
    val rawTableExists: Boolean,
    /**
     * Whether there were any records with null `_airbyte_loaded_at`, at the time that this status
     * was fetched.
     */
    val hasUnprocessedRecords: Boolean,
    // TODO Make maxProcessedTimestamp just `Instant?` instead of Optional
    /**
     * The highest timestamp such that all records in `SELECT * FROM raw_table WHERE
     * _airbyte_extracted_at <= ?` have a nonnull `_airbyte_loaded_at`.
     *
     * Destinations MAY use this value to only run T+D on records with `_airbyte_extracted_at > ?`
     * (note the strictly-greater comparison).
     */
    val maxProcessedTimestamp: Optional<Instant>
)
