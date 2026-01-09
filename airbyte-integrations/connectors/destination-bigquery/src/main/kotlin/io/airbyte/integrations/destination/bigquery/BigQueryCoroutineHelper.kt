/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Helper function for executing blocking BigQuery SDK calls within a coroutine context.
 *
 * This function addresses the issue where BigQuery SDK's blocking calls (like `getTable()`,
 * `query()`) use `AbstractFuture.get()` internally, which throws `InterruptedException` when the
 * thread is interrupted. When running in a coroutine context, if the coroutine is cancelled (e.g.,
 * due to timeout or parent scope cancellation), the thread may be interrupted, causing the BigQuery
 * SDK to throw `BigQueryException` with `InterruptedException` as the cause.
 *
 * This helper:
 * 1. Ensures the blocking call runs on `Dispatchers.IO` (appropriate for blocking I/O operations)
 * 2. Converts `BigQueryException` caused by `InterruptedException` to `CancellationException`,
 * ```
 *    allowing proper coroutine cancellation handling
 * ```
 * 3. Also handles direct `InterruptedException` for cases like `Thread.sleep()` in polling loops
 *
 * Usage:
 * ```kotlin
 * val table = bigQueryCall { bigquery.getTable(tableId) }
 * ```
 *
 * @param block The blocking BigQuery SDK call to execute
 * @return The result of the BigQuery call
 * @throws CancellationException if the call was interrupted due to coroutine cancellation
 * @throws BigQueryException for other BigQuery-related errors
 */
internal suspend fun <T> bigQueryCall(block: () -> T): T =
    withContext(Dispatchers.IO) {
        try {
            block()
        } catch (e: InterruptedException) {
            // Direct InterruptedException (e.g., from Thread.sleep in polling loops)
            // Restore the interrupt status before converting to CancellationException
            Thread.currentThread().interrupt()
            throw CancellationException("Interrupted during BigQuery call", e)
        } catch (e: BigQueryException) {
            // BigQuery SDK wraps InterruptedException in BigQueryException
            if (e.cause is InterruptedException) {
                // Restore the interrupt status before converting to CancellationException
                Thread.currentThread().interrupt()
                throw CancellationException("BigQuery call was interrupted", e)
            }
            throw e
        }
    }
