/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.bigQueryCall
import java.util.concurrent.CancellationException
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
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

        // The coroutine framework may rewrap the CancellationException, so we
        // walk the cause chain to find our message rather than asserting on the
        // immediate thrown exception's properties.
        val messages = generateSequence(thrown as Throwable) { it.cause }.map { it.message }
        assert(
            messages.any { it == "BigQuery operation cancelled due to coroutine cancellation." }
        ) { "Expected cancellation message in cause chain but found: ${messages.toList()}" }
    }

    @Test
    fun `bigQueryCall converts direct InterruptedException to CancellationException`() {
        val ie = InterruptedException("directly interrupted")

        val thrown =
            assertThrows<CancellationException> { runBlocking { bigQueryCall { throw ie } } }

        val messages = generateSequence(thrown as Throwable) { it.cause }.map { it.message }
        assert(
            messages.any { it == "BigQuery operation cancelled due to coroutine cancellation." }
        ) { "Expected cancellation message in cause chain but found: ${messages.toList()}" }
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
