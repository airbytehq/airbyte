/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultReadOperationTest {
    @Test
    internal fun `test that the correct operation type is returned`() {
        val operationExecutor: OperationExecutor = mockk()
        val operation = DefaultReadOperation(operationExecutor = operationExecutor)
        assertEquals(OperationType.READ, operation.type())
    }

    @Test
    internal fun `test that the result of the operation is returned`() {
        val operationExecutor: OperationExecutor = mockk()

        every {
            operationExecutor.execute()
        } answers { Result.success(AirbyteMessage()) } andThenAnswer { Result.failure(NullPointerException("test")) }

        val operation = DefaultReadOperation(operationExecutor = operationExecutor)

        val result1 = operation.execute()
        assertTrue(result1.isSuccess)
        val result2 = operation.execute()
        assertTrue(result2.isFailure)
    }
}
