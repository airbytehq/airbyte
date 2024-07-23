/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.destination.record_buffer.*
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.time.Duration
import java.time.Instant
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.function.Consumer
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.mockito.kotlin.any
import org.mockito.kotlin.mock

class BufferedStreamConsumerTest {
    private var consumer: BufferedStreamConsumer = mock()
    private var onStart: OnStartFunction = mock()
    private var recordWriter: RecordWriter<AirbyteRecordMessage> = mock()
    private var onClose: OnCloseFunction = mock()
    private var isValidRecord: CheckedFunction<JsonNode?, Boolean?, Exception?> = mock()
    private var outputRecordCollector: Consumer<AirbyteMessage> = mock()

    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        consumer =
            BufferedStreamConsumer(
                outputRecordCollector,
                onStart,
                InMemoryRecordBufferingStrategy(recordWriter, 1000),
                onClose,
                CATALOG,
                isValidRecord
            )

        Mockito.`when`(isValidRecord.apply(ArgumentMatchers.any<JsonNode>())).thenReturn(true)
    }

    @Test
    @Throws(Exception::class)
    fun test1StreamWith1State() {
        val expectedRecords = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecords)
        consumer.accept(STATE_MESSAGE1)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords)

        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
    }

    @Test
    @Throws(Exception::class)
    fun test1StreamWith2State() {
        val expectedRecords = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecords)
        consumer.accept(STATE_MESSAGE1)
        consumer.accept(STATE_MESSAGE2)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords)

        Mockito.verify(outputRecordCollector, Mockito.times(1)).accept(STATE_MESSAGE2)
    }

    @Test
    @Throws(Exception::class)
    fun test1StreamWith0State() {
        val expectedRecords = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecords)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords)
    }

    @Test
    @Throws(Exception::class)
    fun test1StreamWithStateAndThenMoreRecordsBiggerThanBuffer() {
        val expectedRecordsBatch1 = generateRecords(1000)
        val expectedRecordsBatch2 = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecordsBatch1)
        consumer.accept(STATE_MESSAGE1)
        consumeRecords(consumer, expectedRecordsBatch2)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1)
        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch2)

        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
    }

    @Test
    @Throws(Exception::class)
    fun test1StreamWithStateAndThenMoreRecordsSmallerThanBuffer() {
        val expectedRecordsBatch1 = generateRecords(1000)
        val expectedRecordsBatch2 = generateRecords(1000)

        // consumer with big enough buffered that we see both batches are flushed in one go.
        val consumer =
            BufferedStreamConsumer(
                outputRecordCollector,
                onStart,
                InMemoryRecordBufferingStrategy(recordWriter, 10000),
                onClose,
                CATALOG,
                isValidRecord
            )

        consumer.start()
        consumeRecords(consumer, expectedRecordsBatch1)
        consumer.accept(STATE_MESSAGE1)
        consumeRecords(consumer, expectedRecordsBatch2)
        consumer.close()

        verifyStartAndClose()

        val expectedRecords =
            Lists.newArrayList(expectedRecordsBatch1, expectedRecordsBatch2).flatMap {
                obj: List<AirbyteMessage> ->
                obj
            }

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords)

        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
    }

    @Test
    @Throws(Exception::class)
    fun testExceptionAfterOneStateMessage() {
        val expectedRecordsBatch1 = generateRecords(1000)
        val expectedRecordsBatch2 = generateRecords(1000)
        val expectedRecordsBatch3 = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecordsBatch1)
        consumer.accept(STATE_MESSAGE1)
        consumeRecords(consumer, expectedRecordsBatch2)
        Mockito.`when`(isValidRecord.apply(ArgumentMatchers.any()))
            .thenThrow(IllegalStateException("induced exception"))
        Assertions.assertThrows(IllegalStateException::class.java) {
            consumer.accept(expectedRecordsBatch3[0])
        }
        consumer.close()

        verifyStartAndCloseFailure()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1)

        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
    }

    @Test
    @Throws(Exception::class)
    fun testExceptionAfterNoStateMessages() {
        val expectedRecordsBatch1 = generateRecords(1000)
        val expectedRecordsBatch2 = generateRecords(1000)
        val expectedRecordsBatch3 = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecordsBatch1)
        consumeRecords(consumer, expectedRecordsBatch2)
        Mockito.`when`(isValidRecord.apply(ArgumentMatchers.any()))
            .thenThrow(IllegalStateException("induced exception"))
        Assertions.assertThrows(IllegalStateException::class.java) {
            consumer.accept(expectedRecordsBatch3[0])
        }
        consumer.close()

        verifyStartAndCloseFailure()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1)

        Mockito.verifyNoInteractions(outputRecordCollector)
    }

    @Test
    @Throws(Exception::class)
    fun testExceptionDuringOnClose() {
        Mockito.doThrow(IllegalStateException("induced exception"))
            .`when`(onClose)
            .accept(false, HashMap())

        val expectedRecordsBatch1 = generateRecords(1000)
        val expectedRecordsBatch2 = generateRecords(1000)

        consumer.start()
        consumeRecords(consumer, expectedRecordsBatch1)
        consumer.accept(STATE_MESSAGE1)
        consumeRecords(consumer, expectedRecordsBatch2)
        Assertions.assertThrows(
            IllegalStateException::class.java,
            { consumer.close() },
            "Expected an error to be thrown on close"
        )

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1)

        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
    }

    @Test
    @Throws(Exception::class)
    fun test2StreamWith1State() {
        val expectedRecordsStream1 = generateRecords(1000)
        val expectedRecordsStream2 =
            expectedRecordsStream1
                .map { `object`: AirbyteMessage -> Jsons.clone(`object`) }
                .onEach { m: AirbyteMessage -> m.record.withStream(STREAM_NAME2) }

        consumer.start()
        consumeRecords(consumer, expectedRecordsStream1)
        consumer.accept(STATE_MESSAGE1)
        consumeRecords(consumer, expectedRecordsStream2)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsStream1)
        verifyRecords(STREAM_NAME2, SCHEMA_NAME, expectedRecordsStream2)

        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
    }

    @Test
    @Throws(Exception::class)
    fun test2StreamWith2State() {
        val expectedRecordsStream1 = generateRecords(1000)
        val expectedRecordsStream2 =
            expectedRecordsStream1
                .map { `object`: AirbyteMessage -> Jsons.clone(`object`) }
                .onEach { m: AirbyteMessage -> m.record.withStream(STREAM_NAME2) }

        consumer.start()
        consumeRecords(consumer, expectedRecordsStream1)
        consumer.accept(STATE_MESSAGE1)
        consumeRecords(consumer, expectedRecordsStream2)
        consumer.accept(STATE_MESSAGE2)
        consumer.close()

        verifyStartAndClose()

        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsStream1)
        verifyRecords(STREAM_NAME2, SCHEMA_NAME, expectedRecordsStream2)

        Mockito.verify(outputRecordCollector, Mockito.times(1)).accept(STATE_MESSAGE2)
    }

    // Periodic Buffer Flush Tests
    @Test
    @Throws(Exception::class)
    fun testSlowStreamReturnsState() {
        // generate records less than the default maxQueueSizeInBytes to confirm periodic flushing
        // occurs
        val expectedRecordsStream1 = generateRecords(500L)
        val expectedRecordsStream1Batch2 = generateRecords(200L)

        // Overrides flush frequency for testing purposes to 5 seconds
        val flushConsumer = consumerWithFlushFrequency
        flushConsumer.start()
        consumeRecords(flushConsumer, expectedRecordsStream1)
        flushConsumer.accept(STATE_MESSAGE1)
        // NOTE: Sleeps process for 5 seconds, if tests are slow this can be updated to reduce
        // slowdowns
        TimeUnit.SECONDS.sleep(PERIODIC_BUFFER_FREQUENCY.toLong())
        consumeRecords(flushConsumer, expectedRecordsStream1Batch2)
        flushConsumer.close()

        verifyStartAndClose()
        // expects the records to be grouped because periodicBufferFlush occurs at the end of
        // acceptTracked
        verifyRecords(
            STREAM_NAME,
            SCHEMA_NAME,
            expectedRecordsStream1 + expectedRecordsStream1Batch2
        )
        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
    }

    @Test
    @Throws(Exception::class)
    fun testSlowStreamReturnsMultipleStates() {
        // generate records less than the default maxQueueSizeInBytes to confirm periodic flushing
        // occurs
        val expectedRecordsStream1 = generateRecords(500L)
        val expectedRecordsStream1Batch2 = generateRecords(200L)
        // creates records equal to size that triggers buffer flush
        val expectedRecordsStream1Batch3 = generateRecords(1000L)

        // Overrides flush frequency for testing purposes to 5 seconds
        val flushConsumer = consumerWithFlushFrequency
        flushConsumer.start()
        consumeRecords(flushConsumer, expectedRecordsStream1)
        flushConsumer.accept(STATE_MESSAGE1)
        // NOTE: Sleeps process for 5 seconds, if tests are slow this can be updated to reduce
        // slowdowns
        TimeUnit.SECONDS.sleep(PERIODIC_BUFFER_FREQUENCY.toLong())
        consumeRecords(flushConsumer, expectedRecordsStream1Batch2)
        consumeRecords(flushConsumer, expectedRecordsStream1Batch3)
        flushConsumer.accept(STATE_MESSAGE2)
        flushConsumer.close()

        verifyStartAndClose()
        // expects the records to be grouped because periodicBufferFlush occurs at the end of
        // acceptTracked
        verifyRecords(
            STREAM_NAME,
            SCHEMA_NAME,
            expectedRecordsStream1 + expectedRecordsStream1Batch2
        )
        verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsStream1Batch3)
        // expects two STATE messages returned since one will be flushed after periodic flushing
        // occurs
        // and the other after buffer has been filled
        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE1)
        Mockito.verify(outputRecordCollector).accept(STATE_MESSAGE2)
    }

    /**
     * Verify that if we ack a state message for stream2 while stream1 has unflushed records+state,
     * that we do _not_ ack stream1's state message.
     */
    @Test
    @Throws(Exception::class)
    fun testStreamTail() {
        // InMemoryRecordBufferingStrategy always returns FLUSH_ALL, so just mock a new strategy
        // here
        val strategy = Mockito.mock(BufferingStrategy::class.java)
        // The first two records that we push will not trigger any flushes, but the third record
        // _will_
        // trigger a flush
        Mockito.`when`(strategy.addRecord(any(), any()))
            .thenReturn(
                Optional.empty(),
                Optional.empty(),
                Optional.of(BufferFlushType.FLUSH_SINGLE_STREAM)
            )
        consumer =
            BufferedStreamConsumer(
                outputRecordCollector,
                onStart,
                strategy,
                onClose,
                CATALOG,
                isValidRecord, // Never periodic flush
                Duration.ofHours(24),
                null
            )
        val expectedRecordsStream1 =
            java.util.List.of(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage().withStream(STREAM_NAME).withNamespace(SCHEMA_NAME)
                    )
            )
        val expectedRecordsStream2 =
            java.util.List.of(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage().withStream(STREAM_NAME2).withNamespace(SCHEMA_NAME)
                    )
            )

        val state1 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(STREAM_NAME)
                                        .withNamespace(SCHEMA_NAME)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(ImmutableMap.of("state_message_id", 1))
                                )
                        )
                )
        val state2 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(STREAM_NAME2)
                                        .withNamespace(SCHEMA_NAME)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(ImmutableMap.of("state_message_id", 2))
                                )
                        )
                )

        consumer.start()
        consumeRecords(consumer, expectedRecordsStream1)
        consumer.accept(state1)
        // At this point, we have not yet flushed anything
        consumeRecords(consumer, expectedRecordsStream2)
        consumer.accept(state2)
        consumeRecords(consumer, expectedRecordsStream2)
        // Now we have flushed stream 2, but not stream 1
        // Verify that we have only acked stream 2's state.
        Mockito.verify(outputRecordCollector).accept(state2)
        Mockito.verify(outputRecordCollector, Mockito.never()).accept(state1)

        consumer.close()
        // Now we've closed the consumer, which flushes everything.
        // Verify that we ack stream 1's pending state.
        Mockito.verify(outputRecordCollector).accept(state1)
    }

    /**
     * Same idea as [.testStreamTail] but with global state. We shouldn't emit any state messages
     * until we close the consumer.
     */
    @Test
    @Throws(Exception::class)
    fun testStreamTailGlobalState() {
        // InMemoryRecordBufferingStrategy always returns FLUSH_ALL, so just mock a new strategy
        // here
        val strategy = Mockito.mock(BufferingStrategy::class.java)
        // The first two records that we push will not trigger any flushes, but the third record
        // _will_
        // trigger a flush
        Mockito.`when`(strategy.addRecord(any(), any()))
            .thenReturn(
                Optional.empty(),
                Optional.empty(),
                Optional.of(BufferFlushType.FLUSH_SINGLE_STREAM)
            )
        consumer =
            BufferedStreamConsumer(
                outputRecordCollector,
                onStart,
                strategy,
                onClose,
                CATALOG,
                isValidRecord, // Never periodic flush
                Duration.ofHours(24),
                null
            )
        val expectedRecordsStream1 =
            java.util.List.of(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage().withStream(STREAM_NAME).withNamespace(SCHEMA_NAME)
                    )
            )
        val expectedRecordsStream2 =
            java.util.List.of(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage().withStream(STREAM_NAME2).withNamespace(SCHEMA_NAME)
                    )
            )

        val state1 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(
                                    Jsons.jsonNode(ImmutableMap.of("state_message_id", 1))
                                )
                        )
                )
        val state2 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(
                                    Jsons.jsonNode(ImmutableMap.of("state_message_id", 2))
                                )
                        )
                )

        consumer.start()
        consumeRecords(consumer, expectedRecordsStream1)
        consumer.accept(state1)
        // At this point, we have not yet flushed anything
        consumeRecords(consumer, expectedRecordsStream2)
        consumer.accept(state2)
        consumeRecords(consumer, expectedRecordsStream2)
        // Now we have flushed stream 2, but not stream 1
        // We should not have acked any state yet, because we haven't written stream1's records yet.
        Mockito.verify(outputRecordCollector, Mockito.never()).accept(ArgumentMatchers.any())

        consumer.close()
        // Now we've closed the consumer, which flushes everything.
        // Verify that we ack the final state.
        // Note that we discard state1 entirely - this is OK. As long as we ack the last state
        // message,
        // the source can correctly resume from that point.
        Mockito.verify(outputRecordCollector).accept(state2)
    }

    private val consumerWithFlushFrequency: BufferedStreamConsumer
        get() {
            val flushFrequencyConsumer =
                BufferedStreamConsumer(
                    outputRecordCollector,
                    onStart,
                    InMemoryRecordBufferingStrategy(recordWriter, 10000),
                    onClose,
                    CATALOG,
                    isValidRecord,
                    Duration.ofSeconds(PERIODIC_BUFFER_FREQUENCY.toLong()),
                    null
                )
            return flushFrequencyConsumer
        }

    @Throws(Exception::class)
    private fun verifyStartAndClose() {
        Mockito.verify(onStart).call()
        Mockito.verify(onClose).accept(false, HashMap())
    }

    /** Indicates that a failure occurred while consuming AirbyteMessages */
    @Throws(Exception::class)
    private fun verifyStartAndCloseFailure() {
        Mockito.verify(onStart).call()
        Mockito.verify(onClose).accept(true, HashMap())
    }

    @Throws(Exception::class)
    private fun verifyRecords(
        streamName: String,
        namespace: String,
        expectedRecords: Collection<AirbyteMessage>
    ) {
        Mockito.verify(recordWriter)
            .accept(
                AirbyteStreamNameNamespacePair(streamName, namespace),
                expectedRecords.map { obj: AirbyteMessage -> obj.record }
            )
    }

    companion object {
        private const val SCHEMA_NAME = "public"
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = STREAM_NAME + 2
        private const val PERIODIC_BUFFER_FREQUENCY = 5
        private val CATALOG: ConfiguredAirbyteCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        CatalogHelpers.createConfiguredAirbyteStream(
                            STREAM_NAME,
                            SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING)
                        ),
                        CatalogHelpers.createConfiguredAirbyteStream(
                            STREAM_NAME2,
                            SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING)
                        )
                    )
                )

        private val STATE_MESSAGE1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 1)))
                )
        private val STATE_MESSAGE2: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 2)))
                )

        private fun consumeRecords(
            consumer: BufferedStreamConsumer?,
            records: Collection<AirbyteMessage>
        ) {
            records.forEach(
                Consumer { m: AirbyteMessage ->
                    try {
                        consumer!!.accept(m)
                    } catch (e: Exception) {
                        throw RuntimeException(e)
                    }
                }
            )
        }

        // NOTE: Generates records at chunks of 160 bytes
        private fun generateRecords(targetSizeInBytes: Long): List<AirbyteMessage> {
            val output: MutableList<AirbyteMessage> = Lists.newArrayList()
            var bytesCounter: Long = 0
            var i = 0
            while (true) {
                val payload =
                    Jsons.jsonNode(
                        ImmutableMap.of(
                            "id",
                            RandomStringUtils.randomAlphabetic(7),
                            "name",
                            "human " + String.format("%8d", i)
                        )
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
                                .withEmittedAt(Instant.now().toEpochMilli())
                                .withData(payload)
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
    }
}
