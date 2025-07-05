/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import io.mockk.Runs
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.just
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class CloseableCoroutineTest {
    @Test
    fun testCloseCleanly() = runTest {
        val closeable = mockk<CloseableCoroutine> { coEvery { close() } just Runs }
        val ret = closeable.use { 42 }
        assertEquals(42, ret)
        coVerify { closeable.close() }
    }

    @Test
    fun testCloseThrows() = runTest {
        val closeable =
            object : CloseableCoroutine {
                override suspend fun close() {
                    throw RuntimeException("exception in close")
                }
            }
        val e =
            assertThrows<RuntimeException> {
                closeable.use {
                    // `close` will throw an exception, so we never actually use this value.
                    @Suppress("UNUSED_EXPRESSION") 42
                }
            }
        assertEquals("exception in close", e.message)
    }

    @Test
    fun testCloseableThrowsAndCloseThrows() = runTest {
        val closeable =
            object : CloseableCoroutine {
                override suspend fun close() {
                    throw RuntimeException("exception in close")
                }
            }
        val e =
            assertThrows<RuntimeException> {
                closeable.use { throw RuntimeException("exception in block") }
            }
        assertEquals("exception in block", e.message)
        assertEquals(listOf("exception in close"), e.suppressedExceptions.map { it.message })
    }
}
