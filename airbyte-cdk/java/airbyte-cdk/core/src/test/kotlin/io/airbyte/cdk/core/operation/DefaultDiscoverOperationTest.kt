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

class DefaultDiscoverOperationTest {
    @Test
    internal fun testThatTheCorrectOperationTypeIsReturned() {
        val operationExecutor: OperationExecutor = mockk()
        val operation = DefaultDiscoverOperation(operationExecutor = operationExecutor)
        assertEquals(OperationType.DISCOVER, operation.type())
    }

    @Test
    internal fun testThatOnSuccessfulExecutionOfTheOperationTheResultIsWrittenToTheOutputRecordCollector() {
        val operationExecutor: OperationExecutor = mockk()
        val expectedMessage = AirbyteMessage()
        val operation = DefaultDiscoverOperation(operationExecutor = operationExecutor)

        every { operationExecutor.execute() } returns Result.success(expectedMessage)

        val result = operation.execute()
        assertTrue(result.isSuccess)
        assertEquals(expectedMessage, result.getOrNull())
    }

    @Test
    internal fun testThatOnAFailedExecutionOfTheOperationTheFailureResultIsReturned() {
        val operationExecutor: OperationExecutor = mockk()

        every { operationExecutor.execute() } returns Result.failure(NullPointerException("test"))

        val operation = DefaultDiscoverOperation(operationExecutor = operationExecutor)

        val result = operation.execute()
        assertTrue(result.isFailure)
    }
}
