/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.TransientErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryUtilsExecuteBigQueryOperationTest {

    @Test
    fun `interrupted exception in cause chain becomes transient error`() {
        val interrupted = InterruptedException("thread interrupted")
        val nestedCause = IllegalStateException("nested", interrupted)
        val bigQueryException = BigQueryException(500, "operation failed", nestedCause)

        val thrown =
            assertThrows<TransientErrorException> {
                BigQueryUtils.executeBigQueryOperation<Nothing> { throw bigQueryException }
            }

        assertEquals(
            "The BigQuery operation was interrupted, likely because the sync was cancelled. This is transient and the next sync attempt should succeed.",
            thrown.message,
        )
        assertEquals(bigQueryException, thrown.cause)
        assertTrue(Thread.currentThread().isInterrupted)
        Thread.interrupted()
    }

    @Test
    fun `non-interrupted BigQuery exception is rethrown`() {
        val bigQueryException =
            BigQueryException(500, "operation failed", RuntimeException("cause"))

        val thrown =
            assertThrows<BigQueryException> {
                BigQueryUtils.executeBigQueryOperation<Nothing> { throw bigQueryException }
            }

        assertEquals(bigQueryException, thrown)
    }
}
