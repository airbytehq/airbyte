/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.TransientErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryUtilsExecuteBigQueryOperationTest {

    @Test
    fun `successful operation returns result`() {
        val result = BigQueryUtils.executeBigQueryOperation { "success" }
        assertEquals("success", result)
    }

    @Test
    fun `BigQueryException wrapping InterruptedException throws TransientErrorException`() {
        val interruptedException = InterruptedException("thread interrupted")
        val bigQueryException = BigQueryException(0, "interrupted", interruptedException)

        val thrown =
            assertThrows<TransientErrorException> {
                BigQueryUtils.executeBigQueryOperation { throw bigQueryException }
            }

        assertEquals("BigQuery API call interrupted.", thrown.message)
        assertEquals(bigQueryException, thrown.cause)
        assertTrue(Thread.currentThread().isInterrupted)
        // Clear the interrupted status for other tests
        Thread.interrupted()
    }

    @Test
    fun `BigQueryException wrapping InterruptedException restores interrupted status`() {
        assertFalse(Thread.currentThread().isInterrupted)

        val interruptedException = InterruptedException("thread interrupted")
        val bigQueryException = BigQueryException(0, "interrupted", interruptedException)

        assertThrows<TransientErrorException> {
            BigQueryUtils.executeBigQueryOperation { throw bigQueryException }
        }

        assertTrue(Thread.currentThread().isInterrupted)
        // Clear the interrupted status for other tests
        Thread.interrupted()
    }

    @Test
    fun `BigQueryException without InterruptedException cause is rethrown as-is`() {
        val bigQueryException = BigQueryException(404, "not found")

        val thrown =
            assertThrows<BigQueryException> {
                BigQueryUtils.executeBigQueryOperation { throw bigQueryException }
            }

        assertEquals(bigQueryException, thrown)
    }

    @Test
    fun `BigQueryException with non-InterruptedException cause is rethrown as-is`() {
        val ioException = java.io.IOException("network error")
        val bigQueryException = BigQueryException(500, "server error", ioException)

        val thrown =
            assertThrows<BigQueryException> {
                BigQueryUtils.executeBigQueryOperation { throw bigQueryException }
            }

        assertEquals(bigQueryException, thrown)
    }

    @Test
    fun `null result from operation is returned`() {
        val result: String? = BigQueryUtils.executeBigQueryOperation { null }
        assertEquals(null, result)
    }
}
