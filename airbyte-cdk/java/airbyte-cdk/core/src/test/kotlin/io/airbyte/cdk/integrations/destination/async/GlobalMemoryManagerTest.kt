/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.integrations.destination.async.buffers.BufferMemory
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class GlobalMemoryManagerTest {
    companion object {
        private const val BYTES_MB = (1024 * 1024).toLong()
    }

    @Test
    internal fun test() {
        val bufferMemory: BufferMemory = mockk()
        every { bufferMemory.getMemoryLimit() } returns 15 * BYTES_MB
        val mgr = GlobalMemoryManager(bufferMemory = bufferMemory)

        assertEquals(10 * BYTES_MB, mgr.requestMemory())
        assertEquals(5 * BYTES_MB, mgr.requestMemory())
        assertEquals(0, mgr.requestMemory())

        mgr.free(10 * BYTES_MB)
        assertEquals(10 * BYTES_MB, mgr.requestMemory())
        mgr.free(16 * BYTES_MB)
        assertEquals(10 * BYTES_MB, mgr.requestMemory())
    }
}
