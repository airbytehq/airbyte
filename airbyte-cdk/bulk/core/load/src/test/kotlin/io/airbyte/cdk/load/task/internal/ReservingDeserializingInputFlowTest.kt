/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
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
                DestinationRecordAirbyteValue(
                    stream,
                    NullValue,
                    0L,
                    null,
                    firstArg<String>().reversed() + "!",
                )
            }
        val inputs = inputFlow.toList().map { it.first to it.second.value }
        val expectedOutputs =
            records.map {
                it.length.toLong() to
                    DestinationRecordAirbyteValue(stream, NullValue, 0L, null, it.reversed() + "!")
            }
        assert(inputs == expectedOutputs)
    }
}
