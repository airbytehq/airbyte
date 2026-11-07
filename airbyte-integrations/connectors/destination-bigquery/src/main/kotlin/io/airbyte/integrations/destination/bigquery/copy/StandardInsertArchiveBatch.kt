/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

interface StandardInsertArchiveBatch : AutoCloseable {
    fun append(bytes: ByteArray)

    /** Stop accepting bytes and start final upload work without waiting for BigQuery's load job. */
    fun seal() = Unit

    suspend fun complete(loadedRecordCount: Long)
}
