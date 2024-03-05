/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultCheckOperationExecutorTest {
    @Test
    internal fun `test that the expected Airbyte message is returned when executed`() {
        val executor = DefaultCheckOperationExecutor()
        val result = executor.execute()
        assertTrue(result.isSuccess)
        result.onSuccess {
            assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, it?.connectionStatus?.status)
        }
    }
}
