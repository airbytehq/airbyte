/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultCheckOperationTest {
    @Test
    internal fun `test that the correct operation type is returned`() {
        val operationExecutor: OperationExecutor = mockk()
        val operation = DefaultCheckOperation(operationExecutor = operationExecutor)
        assertEquals(OperationType.CHECK, operation.type())
    }

    @Test
    internal fun `test that on successful execution of the operation, the result is returned`() {
        val operationExecutor: OperationExecutor = mockk()

        every { operationExecutor.execute() } returns Result.success(AirbyteMessage())

        val operation = DefaultCheckOperation(operationExecutor = operationExecutor)

        val result = operation.execute()
        assertTrue(result.isSuccess)
        verify { operationExecutor.execute() }
    }

    @Test
    internal fun `test that on a failed execution of the operation, the failed check message is returned`() {
        val operationExecutor: OperationExecutor = mockk()
        val failure = NullPointerException("test")
        val expectedMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(
                    AirbyteConnectionStatus()
                        .withStatus(AirbyteConnectionStatus.Status.FAILED)
                        .withMessage(failure.message),
                )

        every { operationExecutor.execute() } returns Result.failure(failure)

        val operation = DefaultCheckOperation(operationExecutor = operationExecutor)

        val result = operation.execute()
        assertTrue(result.isSuccess)
        assertEquals(expectedMessage, result.getOrNull())
        verify { operationExecutor.execute() }
    }
}
