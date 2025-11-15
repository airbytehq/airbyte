/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.micronaut.context.annotation.Property
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.every
import io.mockk.mockk
import jakarta.inject.Inject
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

@Property(name = "airbyte.connector.metadata.docker-repository", value = "default_connector_name")
@Property(name = "airbyte.connector.operation", value = "any_operation")
@MicronautTest(rebuildContext = true)
class AirbyteConnectorRunnableTest {

    @Inject lateinit var runnable: AirbyteConnectorRunnable
    @Inject lateinit var outputConsumer: BufferingOutputConsumer
    private lateinit var operation: Operation

    @BeforeEach
    fun setUp() {
        outputConsumer.resetNewMessagesCursor()
        operation = mockk()
    }

    @MockBean(Operation::class)
    fun operation(): Operation {
        return operation
    }

    @Test
    fun `test when exception then emit trace and raise exception`() {
        every { operation.execute() } throws IllegalArgumentException("Error")

        assertThrows<IllegalArgumentException> { runnable.run() }

        assertEquals(1, outputConsumer.traces().size)
        assertEquals(AirbyteTraceMessage.Type.ERROR, outputConsumer.traces()[0].type)
    }

    @Test
    @Property(name = "airbyte.connector.operation", value = "check")
    fun `test given check operation when exception then emit trace and connection status`() {
        every { operation.execute() } throws IllegalArgumentException("Error")

        runnable.run()

        assertEquals(1, outputConsumer.traces().size)
        assertEquals(AirbyteTraceMessage.Type.ERROR, outputConsumer.traces()[0].type)
        assertEquals(1, outputConsumer.statuses().size)
        assertEquals(AirbyteConnectionStatus.Status.FAILED, outputConsumer.statuses()[0].status)
    }
}
