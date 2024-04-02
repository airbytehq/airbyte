/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core

import io.airbyte.cdk.core.operation.Operation
import io.airbyte.cdk.core.operation.OperationType
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import java.util.function.Consumer
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import picocli.CommandLine
import picocli.CommandLine.Model.CommandSpec

class IntegrationCommandTest {
    @Test
    internal fun `test that the operation command is executed`() {
        val operationType = OperationType.CHECK
        val command = operationType.name.lowercase()
        val commandSpec: CommandSpec = mockk()
        val connectorName = "test-connector"
        val operation: Operation = mockk()
        val outputRecordCollector: Consumer<AirbyteMessage> = mockk()
        val expectedMessage = AirbyteMessage()

        every { operation.type() } returns operationType
        every { operation.execute() } returns Result.success(expectedMessage)
        every { outputRecordCollector.accept(expectedMessage) } returns Unit

        val integrationCommand = IntegrationCommand()
        integrationCommand.command = command
        integrationCommand.commandSpec = commandSpec
        integrationCommand.connectorName = connectorName
        integrationCommand.operation = operation
        integrationCommand.outputRecordCollector = outputRecordCollector

        integrationCommand.run()

        verify { operation.execute() }
        verify(exactly = 1) { outputRecordCollector.accept(expectedMessage) }
    }

    @Test
    internal fun `test that when the operation command is executed and fails, the failure is handled`() {
        val operationType = OperationType.CHECK
        val command = operationType.name.lowercase()
        val commandSpec: CommandSpec = mockk()
        val commandLine: CommandLine = mockk()
        val connectorName = "test-connector"
        val failureException = NullPointerException("test")
        val operation: Operation = mockk()
        val outputRecordCollector: Consumer<AirbyteMessage> = mockk()
        val failureMessage = slot<AirbyteMessage>()

        every { commandLine.usage(System.out) } returns Unit
        every { commandSpec.commandLine() } returns commandLine
        every { operation.type() } returns operationType
        every { operation.execute() } returns Result.failure(failureException)
        every { outputRecordCollector.accept(any()) } returns Unit

        val integrationCommand = IntegrationCommand()
        integrationCommand.command = command
        integrationCommand.commandSpec = commandSpec
        integrationCommand.connectorName = connectorName
        integrationCommand.operation = operation
        integrationCommand.outputRecordCollector = outputRecordCollector

        integrationCommand.run()

        verify { operation.execute() }
        verify { commandLine.usage(System.out) }
        verify(exactly = 1) { outputRecordCollector.accept(capture(failureMessage)) }
        assertEquals(
            ConnectorExceptionUtil.getDisplayMessage(Exception(failureException)),
            failureMessage.captured.connectionStatus.message,
        )
    }
}
