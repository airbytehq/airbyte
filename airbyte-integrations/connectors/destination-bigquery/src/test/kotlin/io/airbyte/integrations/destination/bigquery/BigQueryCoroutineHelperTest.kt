/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.bigQueryCall
import java.util.concurrent.CancellationException
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryCoroutineHelperTest {

    @Test
    fun `bigQueryCall returns result on success`() = runBlocking {
        val result = bigQueryCall { "hello" }
        assertEquals("hello", result)
    }

    @Test
    fun `bigQueryCall returns null on success`() = runBlocking {
        val result = bigQueryCall<String?> { null }
        assertEquals(null, result)
    }

    @Test
    fun `bigQueryCall converts BigQueryException wrapping InterruptedException to CancellationException`() {
        val cause = InterruptedException("thread interrupted")
        val bqException = BigQueryException(0, "wrapped", cause)

        val thrown =
            assertThrows<CancellationException> {
                runBlocking { bigQueryCall { throw bqException } }
            }

        assertEquals("BigQuery operation cancelled due to coroutine cancellation.", thrown.message)
        assertInstanceOf(BigQueryException::class.java, thrown.cause)
        assertTrue(Thread.interrupted()) // clears the interrupt flag set by the handler
    }

    @Test
    fun `bigQueryCall converts direct InterruptedException to CancellationException`() {
        val ie = InterruptedException("directly interrupted")

        val thrown =
            assertThrows<CancellationException> { runBlocking { bigQueryCall { throw ie } } }

        assertEquals("BigQuery operation cancelled due to coroutine cancellation.", thrown.message)
        assertInstanceOf(InterruptedException::class.java, thrown.cause)
        assertTrue(Thread.interrupted()) // clears the interrupt flag
    }

    @Test
    fun `bigQueryCall rethrows BigQueryException without InterruptedException cause`() {
        val bqException = BigQueryException(404, "not found")

        val thrown =
            assertThrows<BigQueryException> { runBlocking { bigQueryCall { throw bqException } } }

        assertEquals("not found", thrown.message)
    }

    @Test
    fun `bigQueryCall rethrows other exceptions unchanged`() {
        val runtimeException = RuntimeException("something else")

        val thrown =
            assertThrows<RuntimeException> {
                runBlocking { bigQueryCall { throw runtimeException } }
            }

        assertEquals("something else", thrown.message)
    }
}
