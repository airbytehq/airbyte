/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.StreamFlushEvent
import io.airbyte.cdk.load.state.Reserved
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.slot
import java.time.Clock
import java.util.stream.Stream
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class FlushTickTaskTest {
    @MockK(relaxed = true) lateinit var clock: Clock
    @MockK(relaxed = true) lateinit var coroutineTimeUtils: TimeProvider
    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog
    @MockK(relaxed = true)
    lateinit var recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>

    private val tickIntervalMs = 60000L // 1 min

    private lateinit var task: FlushTickTask

    @BeforeEach
    fun setup() {
        task =
            FlushTickTask(
                tickIntervalMs,
                clock,
                coroutineTimeUtils,
                catalog,
                recordQueueSupplier,
            )
    }

    @Test
    fun `waits for the configured amount of time`() = runTest {
        task.waitAndPublishFlushTick()

        coVerify { coroutineTimeUtils.delay(tickIntervalMs) }
    }

    @ParameterizedTest
    @MethodSource("streamMatrix")
    fun `publishes a flush message for each stream in the catalog`(
        streams: List<DestinationStream>
    ) = runTest {
        every { catalog.streams } returns streams
        val queues =
            streams.associateWith {
                mockk<MessageQueue<Reserved<DestinationStreamEvent>>>(relaxed = true)
            }

        streams.forEach {
            every { recordQueueSupplier.get(eq(it.descriptor)) } returns queues[it]!!
        }

        task.waitAndPublishFlushTick()

        streams.forEach {
            val msgSlot = slot<Reserved<DestinationStreamEvent>>()
            coVerify { queues[it]!!.publish(capture(msgSlot)) }
            assert(msgSlot.captured.value is StreamFlushEvent)
        }
    }

    companion object {
        @JvmStatic
        fun streamMatrix(): Stream<Arguments> {
            return Stream.of(
                Arguments.of(listOf(Fixtures.stream1)),
                Arguments.of(listOf(Fixtures.stream1, Fixtures.stream2)),
                Arguments.of(listOf(Fixtures.stream1, Fixtures.stream3)),
                Arguments.of(listOf(Fixtures.stream2, Fixtures.stream3)),
                Arguments.of(listOf(Fixtures.stream1, Fixtures.stream2, Fixtures.stream3)),
            )
        }
    }

    object Fixtures {
        val stream1 =
            DestinationStream(
                DestinationStream.Descriptor("test", "stream1"),
                importType = Append,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(type = IntegerType, nullable = true),
                                "name" to FieldType(type = StringType, nullable = true),
                            ),
                    ),
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 42,
            )
        val stream2 =
            DestinationStream(
                DestinationStream.Descriptor("test", "stream2"),
                importType = Append,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(type = IntegerType, nullable = true),
                                "name" to FieldType(type = StringType, nullable = true),
                            ),
                    ),
                generationId = 3,
                minimumGenerationId = 0,
                syncId = 42,
            )
        val stream3 =
            DestinationStream(
                DestinationStream.Descriptor(null, "stream3"),
                importType = Append,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(type = IntegerType, nullable = true),
                                "name" to FieldType(type = StringType, nullable = true),
                            ),
                    ),
                generationId = 9,
                minimumGenerationId = 0,
                syncId = 42,
            )
    }
}
