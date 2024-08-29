/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.time.Instant
import java.util.*

data class InitialRawTableStatus(
    val rawTableExists: Boolean,
    val hasUnprocessedRecords: Boolean,
    val maxProcessedTimestamp: Optional<Instant>
)
