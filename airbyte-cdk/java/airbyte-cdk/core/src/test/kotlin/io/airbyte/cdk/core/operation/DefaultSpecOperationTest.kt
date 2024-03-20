/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultSpecOperationTest {
    @Test
    internal fun testThatTheCorrectOperationTypeIsReturned() {
        val operationExecutor: OperationExecutor = mockk()
        val operation = DefaultSpecOperation(operationExecutor = operationExecutor)
        assertEquals(OperationType.SPEC, operation.type())
    }

    @Test
    internal fun testThatOnSuccessfulExecutionOfTheOperationTheResultIsWrittenToTheOutputRecordCollector() {
        val operationExecutor: OperationExecutor = mockk()
        val expectedMessage = AirbyteMessage()

        every { operationExecutor.execute() } returns Result.success(expectedMessage)

        val operation = DefaultSpecOperation(operationExecutor = operationExecutor)

        val result = operation.execute()
        assertTrue(result.isSuccess)
        verify { operationExecutor.execute() }
    }

    @Test
    internal fun testThatOnAFailedExecutionOfTheOperationTheFailureResultIsReturned() {
        val operationExecutor: OperationExecutor = mockk()

        every { operationExecutor.execute() } returns Result.failure(NullPointerException("test"))

        val operation = DefaultSpecOperation(operationExecutor = operationExecutor)

        val result = operation.execute()
        assertTrue(result.isFailure)
        verify { operationExecutor.execute() }
    }
}
