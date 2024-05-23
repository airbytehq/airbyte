/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
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
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.io.IOException
import java.math.BigDecimal
import java.time.Instant
import java.util.Optional
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Consumer
import java.util.stream.Stream
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito

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
                    java.util.List.of(
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

    private lateinit var consumer: AsyncStreamConsumer
    private lateinit var onStart: OnStartFunction
    private lateinit var flushFunction: DestinationFlushFunction
    private lateinit var onClose: OnCloseFunction
    private lateinit var outputRecordCollector: Consumer<AirbyteMessage>
    private lateinit var flushFailure: FlushFailure
    private lateinit var streamAwareDataTransformer: StreamAwareDataTransformer
    private lateinit var airbyteMessageDeserializer: AirbyteMessageDeserializer

    @BeforeEach
    @Suppress("UNCHECKED_CAST")
    @SuppressFBWarnings(value = ["RCN_REDUNDANT_NULLCHECK_WOULD_HAVE_BEEN_A_NPE"])
    internal fun setup() {
        onStart =
            Mockito.mock(
                OnStartFunction::class.java,
            )
        onClose = Mockito.mock(OnCloseFunction::class.java)
        flushFunction = Mockito.mock(DestinationFlushFunction::class.java)
        outputRecordCollector = Mockito.mock(Consumer::class.java) as Consumer<AirbyteMessage>
        flushFailure = Mockito.mock(FlushFailure::class.java)
        airbyteMessageDeserializer = AirbyteMessageDeserializer()
        consumer =
            AsyncStreamConsumer(
                outputRecordCollector = outputRecordCollector,
                onStart = onStart,
                onClose = onClose,
                onFlush = flushFunction,
                catalog = CATALOG,
                bufferManager = BufferManager(),
                flushFailure = flushFailure,
                defaultNamespace = Optional.of("default_ns"),
                airbyteMessageDeserializer = airbyteMessageDeserializer,
                workerPool = Executors.newFixedThreadPool(5),
            )

        Mockito.`when`(flushFunction.optimalBatchSizeBytes).thenReturn(10000L)
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

        val stateMessageWithDestinationStatsUpdated =
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
                        )
                        .withDestinationStats(
                            AirbyteStateStats().withRecordCount(expectedRecords.size.toDouble()),
                        ),
                )

        Mockito.verify(outputRecordCollector).accept(stateMessageWithDestinationStatsUpdated)
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

        val stateMessageWithDestinationStatsUpdated =
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
                        )
                        .withDestinationStats(AirbyteStateStats().withRecordCount(0.0)),
                )

        Mockito.verify(
                outputRecordCollector,
                Mockito.times(1),
            )
            .accept(stateMessageWithDestinationStatsUpdated)
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
        flushFunction = Mockito.mock(DestinationFlushFunction::class.java)
        flushFailure = Mockito.mock(FlushFailure::class.java)
        consumer =
            AsyncStreamConsumer(
                {},
                Mockito.mock(OnStartFunction::class.java),
                Mockito.mock(OnCloseFunction::class.java),
                flushFunction,
                CATALOG,
                BufferManager((1024 * 10).toLong()),
                flushFailure,
                Optional.of("default_ns"),
            )
        Mockito.`when`(flushFunction.optimalBatchSizeBytes).thenReturn(0L)

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
            airbyteMessageDeserializer.deserializeAirbyteMessage(
                serializedAirbyteMessage,
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
            airbyteMessageDeserializer.deserializeAirbyteMessage(
                serializedAirbyteMessage,
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
            airbyteMessageDeserializer.deserializeAirbyteMessage(
                serializedAirbyteMessage,
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
            airbyteMessageDeserializer.deserializeAirbyteMessage(
                serializedAirbyteMessage,
            )
        }
    }

    @Test
    internal fun deserializeAirbyteMessageWithAirbyteState() {
        val serializedAirbyteMessage = Jsons.serialize(STATE_MESSAGE1)
        val partial =
            airbyteMessageDeserializer.deserializeAirbyteMessage(
                serializedAirbyteMessage,
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
            airbyteMessageDeserializer.deserializeAirbyteMessage(
                serializedAirbyteMessage,
            )
        }
    }

    @Nested
    internal inner class ErrorHandling {
        @Test
        @Throws(Exception::class)
        internal fun testErrorOnAccept() {
            Mockito.`when`(flushFailure.isFailed()).thenReturn(false).thenReturn(true)
            Mockito.`when`(flushFailure.exception).thenReturn(IOException("test exception"))

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
            Mockito.`when`(flushFailure.isFailed()).thenReturn(true)
            Mockito.`when`(flushFailure.exception).thenReturn(IOException("test exception"))

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
        Mockito.verify(onStart).call()
        Mockito.verify(onClose).accept(ArgumentMatchers.any(), ArgumentMatchers.any())
    }

    @Throws(Exception::class)
    private fun verifyRecords(
        streamName: String,
        namespace: String,
        allRecords: List<AirbyteMessage>,
    ) {
        val argumentCaptor = org.mockito.kotlin.argumentCaptor<Stream<PartialAirbyteMessage>>()
        Mockito.verify(flushFunction, Mockito.atLeast(1))
            .flush(
                org.mockito.kotlin.eq(
                    StreamDescriptor().withNamespace(namespace).withName(streamName)
                ),
                argumentCaptor.capture(),
            )

        // captures the output of all the workers, since our records could come out in any of them.
        val actualRecords =
            argumentCaptor.allValues
                .stream() // flatten those results into a single list for the simplicity of
                // comparison
                .flatMap { s: Stream<*> -> s }
                .toList()

        val expRecords =
            allRecords.map { m: AirbyteMessage ->
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
        assertEquals(expRecords, actualRecords)
    }
}
