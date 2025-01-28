/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordSerialized
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.coEvery
import io.mockk.impl.annotations.MockK
import java.io.ByteArrayInputStream
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ReservingDeserializingInputFlowTest {
    companion object {
        const val RATIO = 1.1
    }

    @MockK(relaxed = true) lateinit var config: DestinationConfiguration
    @MockK(relaxed = true) lateinit var deserializer: ProtocolMessageDeserializer
    @MockK(relaxed = true) lateinit var memoryManager: ReservationManager
    @MockK(relaxed = true) lateinit var stream: DestinationStream.Descriptor
    lateinit var inputFlow: ReservingDeserializingInputFlow

    @BeforeEach
    fun setup() {
        coEvery { memoryManager.reserve<String>(any(), any()) } answers
            {
                Reserved(memoryManager, firstArg<Long>(), secondArg<String>())
            }
    }

    @Test
    fun testInputConsumer() = runTest {
        val records =
            listOf(
                "foo",
                "hello there",
                "goodbye",
            )
        val bytes = records.joinToString("\n").toByteArray()
        val inputStream = ByteArrayInputStream(bytes)

        inputFlow =
            ReservingDeserializingInputFlow(config, deserializer, memoryManager, inputStream)

        coEvery { config.estimatedRecordMemoryOverheadRatio } returns RATIO
        coEvery { deserializer.deserialize(any()) } answers
            {
                DestinationRecord(
                    stream,
                    AirbyteMessage(),
                    firstArg<String>().reversed() + "!",
                    ObjectTypeWithoutSchema
                )
            }
        val inputs =
            inputFlow.toList().map {
                it.first to (it.second.value as DestinationRecord).asRecordSerialized()
            }
        val expectedOutputs =
            records.map {
                it.length.toLong() to DestinationRecordSerialized(stream, it.reversed() + "!")
            }
        assert(inputs == expectedOutputs)
    }
}
