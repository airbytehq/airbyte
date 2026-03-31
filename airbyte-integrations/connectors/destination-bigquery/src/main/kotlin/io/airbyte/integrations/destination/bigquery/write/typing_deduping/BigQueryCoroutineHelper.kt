/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping

import com.google.cloud.bigquery.BigQueryException
import java.util.concurrent.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Wraps a blocking BigQuery SDK call so it runs on [Dispatchers.IO] and converts
 * [InterruptedException] (direct or wrapped in [BigQueryException]) into [CancellationException]
 * for proper coroutine cancellation propagation.
 *
 * BigQuery SDK methods like `bigquery.getTable()` and `bigquery.query()` internally call
 * `AbstractFuture.get()`, which throws [InterruptedException] when the thread is interrupted. When
 * these calls happen inside a coroutine, a parent-scope cancellation can interrupt the thread,
 * causing a [BigQueryException] that wraps an [InterruptedException]. Without this helper the
 * exception is treated as a hard failure instead of a cancellation.
 */
suspend fun <T> bigQueryCall(block: () -> T): T =
    withContext(Dispatchers.IO) {
        try {
            block()
        } catch (e: BigQueryException) {
            if (e.cause is InterruptedException) {
                Thread.currentThread().interrupt()
                throw CancellationException(
                    "BigQuery operation cancelled due to coroutine cancellation.",
                    e,
                )
            }
            throw e
        } catch (e: InterruptedException) {
            Thread.currentThread().interrupt()
            throw CancellationException(
                "BigQuery operation cancelled due to coroutine cancellation.",
                e,
            )
        }
    }
