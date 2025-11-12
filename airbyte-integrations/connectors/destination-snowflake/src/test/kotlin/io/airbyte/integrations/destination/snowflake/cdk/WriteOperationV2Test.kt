/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.cdk

import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Test

internal class WriteOperationV2Test {

    @Test
    fun testWriteOperation() {
        val destinationLifecycle = mockk<DestinationLifecycle> { every { run() } returns Unit }
        val writeOperation = WriteOperationV2(destinationLifecycle)
        writeOperation.execute()
        verify(exactly = 1) { destinationLifecycle.run() }
    }
}
