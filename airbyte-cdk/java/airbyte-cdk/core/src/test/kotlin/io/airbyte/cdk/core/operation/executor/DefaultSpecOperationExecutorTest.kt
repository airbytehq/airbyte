/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.protocol.models.v0.AirbyteMessage
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultSpecOperationExecutorTest {
    @Test
    internal fun `test that when the spec file is located on the classpath, a successful result is returned`() {
        val executor = DefaultSpecOperationExecutor()

        val result = executor.execute()

        assertTrue(result.isSuccess)
        result.onSuccess {
            assertEquals(AirbyteMessage.Type.SPEC, it.type)
            assertNotNull(it.spec)
        }
    }

    @Test
    internal fun `test that when the spec file cannot be located on the classpath, a failure result is returned`() {
        val executor = DefaultSpecOperationExecutor("missing-spec.json")
        val result = executor.execute()
        assertTrue(result.isFailure)
    }
}
