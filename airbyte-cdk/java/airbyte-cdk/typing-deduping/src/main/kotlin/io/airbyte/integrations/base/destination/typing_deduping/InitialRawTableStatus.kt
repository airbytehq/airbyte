/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.time.Instant
import java.util.*

class InitialRawTableStatus(
    rawTableExists: Boolean,
    hasUnprocessedRecords: Boolean,
    maxProcessedTimestamp: Optional<Instant>
) {
    val rawTableExists: Boolean
    val hasUnprocessedRecords: Boolean
    val maxProcessedTimestamp: Optional<Instant>

    init {
        this.rawTableExists = rawTableExists
        this.hasUnprocessedRecords = hasUnprocessedRecords
        this.maxProcessedTimestamp = maxProcessedTimestamp
    }
}
