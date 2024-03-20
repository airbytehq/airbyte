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

class DefaultWriteOperationTest {
    @Test
    internal fun testThatTheCorrectOperationTypeIsReturned() {
        val operationExecutor: OperationExecutor = mockk()
        val operation = DefaultWriteOperation(operationExecutor = operationExecutor)
        assertEquals(OperationType.WRITE, operation.type())
    }

    @Test
    internal fun testThatTheResultOfTheOperationIsReturned() {
        val operationExecutor: OperationExecutor = mockk()

        every { operationExecutor.execute() } answers
            {
                Result.success(AirbyteMessage())
            } andThenAnswer
            {
                Result.failure(NullPointerException("test"))
            }

        val operation = DefaultWriteOperation(operationExecutor = operationExecutor)

        val result1 = operation.execute()
        assertTrue(result1.isSuccess)
        val result2 = operation.execute()
        assertTrue(result2.isFailure)
    }
}
