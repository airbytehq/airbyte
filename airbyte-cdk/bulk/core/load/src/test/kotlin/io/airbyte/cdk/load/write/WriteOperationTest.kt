/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Test

class WriteOperationTest {

    @Test
    fun testWriteOperation() {
        val destinationLifecycle = mockk<DestinationLifecycle> { every { run() } returns Unit }
        val writeOperation = WriteOperation(destinationLifecycle)
        writeOperation.execute()
        verify(exactly = 1) { destinationLifecycle.run() }
    }
}
