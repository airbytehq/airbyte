/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.protocol.models.v0.AirbyteMessage
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultDiscoverOperationExecutorTest {
    @Test
    internal fun `test that the expected Airbyte message is returned when executed`() {
        val executor = DefaultDiscoverOperationExecutor()
        val result = executor.execute()
        assertTrue(result.isSuccess)
        result.onSuccess {
            assertEquals(AirbyteMessage.Type.CATALOG, it?.type)
            assertNotNull(it?.catalog)
        }
    }
}
