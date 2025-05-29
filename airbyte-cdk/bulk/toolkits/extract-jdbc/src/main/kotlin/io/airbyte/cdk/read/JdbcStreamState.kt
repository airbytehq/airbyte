/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode

/**
 * Encapsulates database-specific transient state for a particular [stream].
 *
 * Implementations should be thread-safe.
 */
interface JdbcStreamState<A : JdbcSharedState> {

    val stream: Stream

    /** The transient state shared by all partitions. Includes global resources. */
    val sharedState: A

    /** Value to use as upper bound for the cursor column. */
    var cursorUpperBound: JsonNode?

    /** Value to use for JDBC fetchSize, if specified. */
    var fetchSize: Int?

    /** Same as [fetchSize], but falls back to a default value. */
    val fetchSizeOrDefault: Int

    /** Value to use for the LIMIT clause in resumable reads, if applicable. */
    val limit: Long

    /** Adjusts the [limit] value up or down. */
    fun updateLimitState(fn: (LimitState) -> LimitState)

    /** Resets the transient state to its initial setting. */
    fun reset()
}
