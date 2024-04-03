/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.core.command.option.ConnectorConfiguration
import io.airbyte.cdk.core.command.option.MicronautConfiguredAirbyteCatalog
import io.airbyte.cdk.integrations.destination.async.buffers.AsyncBuffers
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.buffers.BufferEnqueue
import io.airbyte.cdk.integrations.destination.async.buffers.BufferMemory
import io.airbyte.cdk.integrations.destination.async.deser.DeserializationUtil
import io.airbyte.cdk.integrations.destination.async.deser.IdentityDataTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordSizeEstimator
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.scheduling.ScheduledExecutorTaskScheduler
import io.micronaut.scheduling.instrument.InstrumentedExecutorService
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.IOException
import java.math.BigDecimal
import java.time.Clock
import java.time.Instant
import java.util.Optional
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Consumer
import java.util.stream.Collectors
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class AsyncStreamConsumerTest {
    companion object {
        private const val RECORD_SIZE_20_BYTES = 20
        private const val SCHEMA_NAME = "public"
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = STREAM_NAME + 2
        private val STREAM1_DESC: StreamDescriptor =
            StreamDescriptor().withNamespace(SCHEMA_NAME).withName(STREAM_NAME)

        private val CATALOG: ConfiguredAirbyteCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        CatalogHelpers.createConfiguredAirbyteStream(
                            STREAM_NAME,
                            SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING),
                        ),
                        CatalogHelpers.createConfiguredAirbyteStream(
                            STREAM_NAME2,
                            SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING),
                        ),
                    ),
                )

        private val PAYLOAD: JsonNode =
            Jsons.jsonNode(
                mapOf(
                    "created_at" to "2022-02-01T17:02:19+00:00",
                    "id" to 1,
                    "make" to "Mazda",
                    "nested_column" to mapOf("array_column" to listOf(1, 2, 3)),
                ),
            )

        private val STATE_MESSAGE1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    STREAM1_DESC,
                                )
                                .withStreamState(Jsons.jsonNode(1)),
                        ),
                )
        private val STATE_MESSAGE2: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    STREAM1_DESC,
                                )
                                .withStreamState(Jsons.jsonNode(2)),
                        ),
                )
    }

    private lateinit var micronautConfiguredAirbyteCatalog: MicronautConfiguredAirbyteCatalog
    private lateinit var connectorConfiguration: ConnectorConfiguration
    private lateinit var bufferEnqueue: BufferEnqueue
    private lateinit var consumer: AsyncStreamConsumer
    private lateinit var flushFailure: FlushFailure
    private lateinit var streamAwareDataTransformer: StreamAwareDataTransformer
    private lateinit var deserializationUtil: DeserializationUtil
    private lateinit var flushWorkers: FlushWorkers
    private lateinit var onClose: OnCloseFunction
    private lateinit var onStart: OnStartFunction
    private lateinit var streamDescriptorUtils: StreamDescriptorUtils

    @BeforeEach
    @SuppressFBWarnings(value = ["RCN_REDUNDANT_NULLCHECK_WOULD_HAVE_BEEN_A_NPE"])
    internal fun setup() {
        micronautConfiguredAirbyteCatalog = mockk()
        connectorConfiguration = mockk()
        bufferEnqueue = mockk()
        flushFailure = mockk()
        flushWorkers = mockk()
        onClose = mockk()
        onStart = mockk()
        streamDescriptorUtils = StreamDescriptorUtils()
        deserializationUtil = DeserializationUtil()
        streamAwareDataTransformer = IdentityDataTransformer()

        every { micronautConfiguredAirbyteCatalog.getConfiguredCatalog() } returns CATALOG
        every { bufferEnqueue.addRecord(any(), any(), any()) } returns Unit
        every { connectorConfiguration.getDefaultNamespace() } returns Optional.of(SCHEMA_NAME)
        every { flushFailure.isFailed() } returns false
        every { flushWorkers.close() } returns Unit
        every { flushWorkers.start() } returns Unit
        every { onClose.accept(any(), any()) } returns Unit
        every { onStart.call() } returns null

        consumer =
            AsyncStreamConsumer(
                micronautConfiguredAirbyteCatalog = micronautConfiguredAirbyteCatalog,
                bufferEnqueue = bufferEnqueue,
                connectorConfiguration = connectorConfiguration,
                flushFailure = flushFailure,
                flushWorkers = flushWorkers,
                onClose = onClose,
                onStart = onStart,
                streamDescriptorUtils = streamDescriptorUtils,
                deserializationUtil = deserializationUtil,
                dataTransformer = streamAwareDataTransformer,
            )
    }

    @Test
    @Throws(Exception::class)
    internal fun test1StreamWith1State() {
        val expectedRecords = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecords)
        consumer.accept(Jsons.serialize(STATE_MESSAGE1), RECORD_SIZE_20_BYTES)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords)

        verify(exactly = 7) { bufferEnqueue.addRecord(any(), any(), Optional.of(SCHEMA_NAME)) }
    }

    @Test
    @Throws(Exception::class)
    internal fun test1StreamWith2State() {
        val expectedRecords = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecords)
        consumer.accept(Jsons.serialize(STATE_MESSAGE1), RECORD_SIZE_20_BYTES)
        consumer.accept(Jsons.serialize(STATE_MESSAGE2), RECORD_SIZE_20_BYTES)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords)

        verify(exactly = 8) { bufferEnqueue.addRecord(any(), any(), Optional.of(SCHEMA_NAME)) }
    }

    @Test
    @Throws(Exception::class)
    internal fun test1StreamWith0State() {
        val allRecords = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, allRecords)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, allRecords)
    }

    @Test
    @Throws(Exception::class)
    internal fun testShouldBlockWhenQueuesAreFull() {
        consumer.start()
    }

    /*
     * Tests that the consumer will block when the buffer is full. Achieves this by setting optimal
     * batch size to 0, so the flush worker never actually pulls anything from the queue.
     */
    @Test
    @Throws(Exception::class)
    internal fun testBackPressure() {
        val bufferMemory: BufferMemory = mockk()
        val destinationFlushFunction: DestinationFlushFunction = mockk()

        every { bufferMemory.getMemoryLimit() } returns (1024 * 10)
        every { destinationFlushFunction.optimalBatchSizeBytes } returns 0L
        every { destinationFlushFunction.queueFlushThresholdBytes } returns 0L
        every { destinationFlushFunction.flush(any(), any()) } returns Unit

        val airbyteFileUtils = AirbyteFileUtils()
        val asyncBuffers = AsyncBuffers()
        val globalMemoryManager = GlobalMemoryManager(bufferMemory = bufferMemory)
        val globalAsyncStateManager =
            GlobalAsyncStateManager(globalMemoryManager = globalMemoryManager)
        val bufferEnqueue =
            BufferEnqueue(
                globalMemoryManager = globalMemoryManager,
                globalAsyncStateManager = globalAsyncStateManager,
                asyncBuffers = asyncBuffers,
            )
        val bufferDequeue =
            BufferDequeue(
                globalAsyncStateManager = globalAsyncStateManager,
                globalMemoryManager = globalMemoryManager,
                asyncBuffers = asyncBuffers,
            )
        val runningFlushWorkers = RunningFlushWorkers()
        val detectStreamToFlush =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                destinationFlushFunction = destinationFlushFunction,
                runningFlushWorkers = runningFlushWorkers,
                airbyteFileUtils = airbyteFileUtils,
                nowProvider = Optional.of(Clock.systemUTC()),
            )
        val flushWorkers =
            FlushWorkers(
                globalAsyncStateManager = globalAsyncStateManager,
                bufferDequeue = bufferDequeue,
                flushFailure = flushFailure,
                destinationFlushFunction = destinationFlushFunction,
                airbyteFileUtils = airbyteFileUtils,
                outputRecordCollector = {},
                runningFlushWorkers = runningFlushWorkers,
                detectStreamToFlush = detectStreamToFlush,
                workerPool = TestExecutorServiceInstrumenter(),
                taskScheduler = ScheduledExecutorTaskScheduler(Executors.newScheduledThreadPool(1)),
            )

        every { destinationFlushFunction.optimalBatchSizeBytes } returns 0L

        consumer =
            AsyncStreamConsumer(
                micronautConfiguredAirbyteCatalog = micronautConfiguredAirbyteCatalog,
                bufferEnqueue = bufferEnqueue,
                connectorConfiguration = connectorConfiguration,
                flushFailure = flushFailure,
                flushWorkers = flushWorkers,
                onClose = onClose,
                onStart = onStart,
                streamDescriptorUtils = streamDescriptorUtils,
                dataTransformer = streamAwareDataTransformer,
                deserializationUtil = deserializationUtil
            )

        val recordCount = AtomicLong()

        consumer.start()

        val executor = Executors.newSingleThreadExecutor()
        while (true) {
            val future =
                executor.submit {
                    try {
                        consumer.accept(
                            Jsons.serialize(
                                AirbyteMessage()
                                    .withType(AirbyteMessage.Type.RECORD)
                                    .withRecord(
                                        AirbyteRecordMessage()
                                            .withStream(STREAM_NAME)
                                            .withNamespace(SCHEMA_NAME)
                                            .withEmittedAt(Instant.now().toEpochMilli())
                                            .withData(
                                                Jsons.jsonNode(recordCount.getAndIncrement()),
                                            ),
                                    ),
                            ),
                            RECORD_SIZE_20_BYTES,
                        )
                    } catch (e: Exception) {
                        throw RuntimeException(e)
                    }
                }

            try {
                future[1, TimeUnit.SECONDS]
            } catch (e: TimeoutException) {
                future.cancel(true) // Stop the operation running in thread
                break
            }
        }
        executor.shutdownNow()

        assertTrue(recordCount.get() < 1000, "Record count was ${recordCount.get()}")
    }

    @Test
    internal fun deserializeAirbyteMessageWithAirbyteRecord() {
        val airbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(STREAM_NAME)
                        .withNamespace(SCHEMA_NAME)
                        .withData(PAYLOAD),
                )
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        val airbyteRecordString = Jsons.serialize(PAYLOAD)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(airbyteRecordString, partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithBigDecimalAirbyteRecord() {
        val payload =
            Jsons.jsonNode(
                mapOf(
                    "foo" to BigDecimal("1234567890.1234567890"),
                ),
            )
        val airbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(STREAM_NAME)
                        .withNamespace(SCHEMA_NAME)
                        .withData(payload),
                )
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        val airbyteRecordString = Jsons.serialize(payload)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(airbyteRecordString, partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithEmptyAirbyteRecord() {
        val emptyMap: Map<*, *> = java.util.Map.of<Any, Any>()
        val airbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(STREAM_NAME)
                        .withNamespace(SCHEMA_NAME)
                        .withData(Jsons.jsonNode(emptyMap)),
                )
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(emptyMap.toString(), partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithNoStateOrRecord() {
        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.LOG).withLog(AirbyteLogMessage())
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        assertThrows(
            RuntimeException::class.java,
        ) {
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        }
    }

    @Test
    internal fun deserializeAirbyteMessageWithAirbyteState() {
        val serializedAirbyteMessage = Jsons.serialize(STATE_MESSAGE1)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(serializedAirbyteMessage, partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithBadAirbyteState() {
        val badState =
            AirbyteMessage()
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    STREAM1_DESC,
                                )
                                .withStreamState(Jsons.jsonNode(1)),
                        ),
                )
        val serializedAirbyteMessage = Jsons.serialize(badState)
        assertThrows(
            RuntimeException::class.java,
        ) {
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        }
    }

    @Nested
    internal inner class ErrorHandling {
        @Test
        @Throws(Exception::class)
        internal fun testErrorOnAccept() {
            every { flushFailure.isFailed() } returns false andThen true
            every { flushFailure.getException() } returns IOException("test exception")

            val m =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(STREAM_NAME)
                            .withNamespace(SCHEMA_NAME)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(Jsons.deserialize("")),
                    )
            consumer.start()
            consumer.accept(Jsons.serialize(m), RECORD_SIZE_20_BYTES)
            assertThrows(
                IOException::class.java,
            ) {
                consumer.accept(
                    Jsons.serialize(
                        m,
                    ),
                    RECORD_SIZE_20_BYTES,
                )
            }
        }

        @Test
        @Throws(Exception::class)
        internal fun testErrorOnClose() {
            every { flushFailure.isFailed() } returns true
            every { flushFailure.getException() } returns IOException("test exception")

            consumer.start()
            assertThrows(
                IOException::class.java,
            ) {
                consumer.close()
            }
        }
    }

    private fun consumeRecords(
        consumer: AsyncStreamConsumer?,
        records: Collection<AirbyteMessage>,
    ) {
        records.forEach(
            Consumer { m: AirbyteMessage ->
                try {
                    consumer!!.accept(
                        Jsons.serialize(m),
                        RECORD_SIZE_20_BYTES,
                    )
                } catch (e: Exception) {
                    throw RuntimeException(e)
                }
            },
        )
    }

    // NOTE: Generates records at chunks of 160 bytes
    private fun generateRecords(targetSizeInBytes: Long): List<AirbyteMessage> {
        val output: MutableList<AirbyteMessage> = arrayListOf()
        var bytesCounter: Long = 0
        var i = 0
        while (true) {
            val payload =
                Jsons.jsonNode(
                    mapOf(
                        "id" to RandomStringUtils.randomAlphabetic(7),
                        "name" to "human " + String.format("%8d", i),
                    ),
                )
            val sizeInBytes = RecordSizeEstimator.getStringByteSize(payload)
            bytesCounter += sizeInBytes
            val airbyteMessage =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(STREAM_NAME)
                            .withNamespace(SCHEMA_NAME)
                            .withData(payload),
                    )
            if (bytesCounter > targetSizeInBytes) {
                break
            } else {
                output.add(airbyteMessage)
            }
            i++
        }
        return output
    }

    @Throws(Exception::class)
    private fun verifyStartAndClose() {
        verify(exactly = 1) { onStart.call() }
        verify(exactly = 1) { onClose.accept(any(), any()) }
    }

    @Throws(Exception::class)
    private fun verifyRecords(
        streamName: String,
        namespace: String,
        allRecords: List<AirbyteMessage>,
    ) {
        val actualRecords = mutableListOf<PartialAirbyteMessage>()
        verify { bufferEnqueue.addRecord(capture(actualRecords), any(), any()) }

        val expRecords =
            allRecords
                .stream()
                .map { m: AirbyteMessage ->
                    PartialAirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            PartialAirbyteRecordMessage()
                                .withStream(m.record.stream)
                                .withNamespace(m.record.namespace)
                                .withData(m.record.data),
                        )
                        .withSerialized(
                            Jsons.serialize(
                                m.record.data,
                            ),
                        )
                }
                .collect(Collectors.toList())
        assertEquals(
            expRecords,
            actualRecords.filter {
                it.type == AirbyteMessage.Type.RECORD &&
                    it.record?.stream == streamName &&
                    it.record?.namespace == namespace
            },
        )
    }
}

class TestExecutorServiceInstrumenter : InstrumentedExecutorService {
    override fun getTarget(): ExecutorService {
        return ThreadPoolExecutor(1, 1, 0L, TimeUnit.MILLISECONDS, LinkedBlockingQueue())
    }
}
