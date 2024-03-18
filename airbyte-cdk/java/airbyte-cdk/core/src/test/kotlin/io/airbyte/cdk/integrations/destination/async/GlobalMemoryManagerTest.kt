/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class GlobalMemoryManagerTest {
    private val BYTES_MB = (1024 * 1024).toLong()

    @Test
    internal fun test() {
        val mgr = GlobalMemoryManager(15 * BYTES_MB)

        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(5 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(0, mgr.requestMemory())

        mgr.free(10 * BYTES_MB)
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        mgr.free(16 * BYTES_MB)
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
    }
}
