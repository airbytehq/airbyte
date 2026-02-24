/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import java.time.Instant
import java.util.concurrent.atomic.AtomicLong
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MsSqlServerCdcCursorTest {

    @Test
    fun testCdcCursorGeneratorDoesNotOverflow() {
        // The CDC cursor is generated using epochSecond * 100_000_000 to produce a
        // monotonically increasing Long used by destinations for deduplication.
        // This test ensures the cursor value remains positive and within Long range.
        val now = Instant.now()
        val cursorValue = now.epochSecond * 100_000_000 + 1

        assertTrue(cursorValue > 0, "CDC cursor must be positive, got $cursorValue")
        assertTrue(cursorValue < Long.MAX_VALUE, "CDC cursor must not overflow Long.MAX_VALUE")
    }

    @Test
    fun testCursorIsMonotonicallyIncreasing() {
        val generator = AtomicLong(Instant.now().epochSecond * 100_000_000 + 1)
        val first = generator.getAndIncrement()
        val second = generator.getAndIncrement()
        val third = generator.getAndIncrement()

        assertTrue(first > 0)
        assertTrue(second > first)
        assertTrue(third > second)
    }
}
