/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.util.MoreIterators
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.sql.SQLException
import java.time.Duration
import java.util.*
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap

internal class CursorStateMessageProducerTest {
    private fun createExceptionIterator(): Iterator<AirbyteMessage> {
        return object : Iterator<AirbyteMessage> {
            val internalMessageIterator: Iterator<AirbyteMessage> =
                MoreIterators.of(
                    RECORD_MESSAGE_1,
                    RECORD_MESSAGE_2,
                    RECORD_MESSAGE_2,
                    RECORD_MESSAGE_3
                )

            override fun hasNext(): Boolean {
                return true
            }

            override fun next(): AirbyteMessage {
                if (internalMessageIterator.hasNext()) {
                    return internalMessageIterator.next()
                } else {
                    // this line throws a RunTimeException wrapped around a SQLException to mimic
                    // the flow of when a
                    // SQLException is thrown and wrapped in
                    // StreamingJdbcDatabase#tryAdvance
                    throw RuntimeException(
                        SQLException(
                            "Connection marked broken because of SQLSTATE(080006)",
                            "08006"
                        )
                    )
                }
            }
        }
    }

    private var stateManager: StateManager? = null

    @BeforeEach
    fun setup() {
        val airbyteStream = AirbyteStream().withNamespace(NAMESPACE).withName(STREAM_NAME)
        val configuredAirbyteStream =
            ConfiguredAirbyteStream()
                .withStream(airbyteStream)
                .withCursorField(listOf(UUID_FIELD_NAME))

        stateManager =
            StreamStateManager(
                emptyList(),
                ConfiguredAirbyteCatalog().withStreams(listOf(configuredAirbyteStream))
            )
    }

    @Test
    fun testWithoutInitialCursor() {
        messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2)

        val producer = CursorStateMessageProducer(stateManager, Optional.empty())

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(0, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_1, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_2, 1, 2.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testWithInitialCursor() {
        // record 1 and 2 has smaller cursor value, so at the end, the initial cursor is emitted
        // with 0
        // record count

        messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2)

        val producer = CursorStateMessageProducer(stateManager, Optional.of(RECORD_VALUE_5))

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(0, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_1, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_5, 0, 2.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testCursorFieldIsEmpty() {
        val recordMessage = Jsons.clone(RECORD_MESSAGE_1)
        (recordMessage.record.data as ObjectNode).remove(UUID_FIELD_NAME)
        val messageStream = MoreIterators.of(recordMessage)

        val producer = CursorStateMessageProducer(stateManager, Optional.empty())

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageStream,
                STREAM,
                producer,
                StateEmitFrequency(0, Duration.ZERO)
            )

        Assertions.assertEquals(recordMessage, iterator.next())
        // null because no records with a cursor field were replicated for the stream.
        Assertions.assertEquals(createEmptyStateMessage(1.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testIteratorCatchesExceptionWhenEmissionFrequencyNonZero() {
        val exceptionIterator = createExceptionIterator()

        val producer = CursorStateMessageProducer(stateManager, Optional.of(RECORD_VALUE_1))

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                exceptionIterator,
                STREAM,
                producer,
                StateEmitFrequency(1, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_1, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        // continues to emit RECORD_MESSAGE_2 since cursorField has not changed thus not satisfying
        // the
        // condition of "ready"
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        // emits the first state message since the iterator has changed cursorFields (2 -> 3) and
        // met the
        // frequency minimum of 1 record
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_2, 2, 4.0), iterator.next())
        // no further records to read since Exception was caught above and marked iterator as
        // endOfData()
        Assertions.assertThrows(FailedRecordIteratorException::class.java) { iterator.hasNext() }
    }

    @Test
    fun testIteratorCatchesExceptionWhenEmissionFrequencyZero() {
        val exceptionIterator = createExceptionIterator()

        val producer = CursorStateMessageProducer(stateManager, Optional.of(RECORD_VALUE_1))

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                exceptionIterator,
                STREAM,
                producer,
                StateEmitFrequency(0, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_1, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())

        Assertions.assertThrows(RuntimeException::class.java) { iterator.hasNext() }
    }

    @Test
    fun testEmptyStream() {
        val producer = CursorStateMessageProducer(stateManager, Optional.empty())

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                Collections.emptyIterator(),
                STREAM,
                producer,
                StateEmitFrequency(1, Duration.ZERO)
            )

        Assertions.assertEquals(EMPTY_STATE_MESSAGE, iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testUnicodeNull() {
        val recordValueWithNull = "abc\u0000"
        val recordMessageWithNull = createRecordMessage(recordValueWithNull)

        // UTF8 null \u0000 is removed from the cursor value in the state message
        messageIterator = MoreIterators.of(recordMessageWithNull)

        val producer = CursorStateMessageProducer(stateManager, Optional.empty())

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(0, Duration.ZERO)
            )

        Assertions.assertEquals(recordMessageWithNull, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_1, 1, 1.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testStateEmissionFrequency1() {
        messageIterator =
            MoreIterators.of(
                RECORD_MESSAGE_1,
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_4,
                RECORD_MESSAGE_5
            )

        val producer = CursorStateMessageProducer(stateManager, Optional.empty())

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(1, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_1, iterator.next())
        // should emit state 1, but it is unclear whether there will be more
        // records with the same cursor value, so no state is ready for emission
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        // emit state 1 because it is the latest state ready for emission
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_1, 1, 2.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_2, 1, 1.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_4, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_3, 1, 1.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_5, iterator.next())
        // state 4 is not emitted because there is no more record and only
        // the final state should be emitted at this point; also the final
        // state should only be emitted once
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_5, 1, 1.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testStateEmissionFrequency2() {
        messageIterator =
            MoreIterators.of(
                RECORD_MESSAGE_1,
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_4,
                RECORD_MESSAGE_5
            )

        val producer = CursorStateMessageProducer(stateManager, Optional.empty())

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(2, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_1, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        // emit state 1 because it is the latest state ready for emission
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_1, 1, 2.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_4, iterator.next())
        // emit state 3 because it is the latest state ready for emission
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_3, 1, 2.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_5, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_5, 1, 1.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testStateEmissionWhenInitialCursorIsNotNull() {
        messageIterator =
            MoreIterators.of(RECORD_MESSAGE_2, RECORD_MESSAGE_3, RECORD_MESSAGE_4, RECORD_MESSAGE_5)

        val producer = CursorStateMessageProducer(stateManager, Optional.of(RECORD_VALUE_1))

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(1, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_2, 1, 2.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_4, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_3, 1, 1.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_5, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_5, 1, 1.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    /**
     * Incremental syncs will sort the table with the cursor field, and emit the max cursor for
     * every N records. The purpose is to emit the states frequently, so that if any transient
     * failure occurs during a long sync, the next run does not need to start from the beginning,
     * but can resume from the last successful intermediate state committed on the destination. The
     * next run will start with `cursorField > cursor`. However, it is possible that there are
     * multiple records with the same cursor value. If the intermediate state is emitted before all
     * these records have been synced to the destination, some of these records may be lost.
     *
     * Here is an example:
     *
     * <pre> | Record ID | Cursor Field | Other Field | Note | | --------- | ------------ |
     * ----------- | ----------------------------- | | 1 | F1=16 | F2="abc" | | | 2 | F1=16 |
     * F2="def" | <- state emission and failure | | 3 | F1=16 | F2="ghi" | | </pre> *
     *
     * If the intermediate state is emitted for record 2 and the sync fails immediately such that
     * the cursor value `16` is committed, but only record 1 and 2 are actually synced, the next run
     * will start with `F1 > 16` and skip record 3.
     *
     * So intermediate state emission should only happen when all records with the same cursor value
     * has been synced to destination. Reference:
     * [link](https://github.com/airbytehq/airbyte/issues/15427)
     */
    @Test
    fun testStateEmissionForRecordsSharingSameCursorValue() {
        messageIterator =
            MoreIterators.of(
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_4,
                RECORD_MESSAGE_5,
                RECORD_MESSAGE_5
            )

        val producer = CursorStateMessageProducer(stateManager, Optional.of(RECORD_VALUE_1))

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(1, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        // state 2 is the latest state ready for emission because
        // all records with the same cursor value have been emitted
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_2, 2, 3.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_4, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_3, 3, 3.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_5, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_4, 1, 1.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_5, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_5, 2, 1.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    @Test
    fun testStateEmissionForRecordsSharingSameCursorValueButDifferentStatsCount() {
        messageIterator =
            MoreIterators.of(
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_2,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3,
                RECORD_MESSAGE_3
            )

        val producer = CursorStateMessageProducer(stateManager, Optional.of(RECORD_VALUE_1))

        val iterator: SourceStateIterator<*> =
            SourceStateIterator(
                messageIterator,
                STREAM,
                producer,
                StateEmitFrequency(10, Duration.ZERO)
            )

        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_2, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        // state 2 is the latest state ready for emission because
        // all records with the same cursor value have been emitted
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_2, 4, 10.0), iterator.next())
        Assertions.assertEquals(RECORD_MESSAGE_3, iterator.next())
        Assertions.assertEquals(createStateMessage(RECORD_VALUE_3, 7, 1.0), iterator.next())
        Assertions.assertFalse(iterator.hasNext())
    }

    companion object {
        private const val NAMESPACE = "public"
        private const val STREAM_NAME = "shoes"
        private const val UUID_FIELD_NAME = "ascending_inventory_uuid"

        private val STREAM: ConfiguredAirbyteStream =
            CatalogHelpers.createConfiguredAirbyteStream(
                    STREAM_NAME,
                    NAMESPACE,
                    Field.of(UUID_FIELD_NAME, JsonSchemaType.STRING)
                )
                .withSyncMode(SyncMode.INCREMENTAL)
                .withCursorField(List.of(UUID_FIELD_NAME))

        private val EMPTY_STATE_MESSAGE = createEmptyStateMessage(0.0)

        private const val RECORD_VALUE_1 = "abc"
        private val RECORD_MESSAGE_1 = createRecordMessage(RECORD_VALUE_1)

        private const val RECORD_VALUE_2 = "def"
        private val RECORD_MESSAGE_2 = createRecordMessage(RECORD_VALUE_2)

        private const val RECORD_VALUE_3 = "ghi"
        private val RECORD_MESSAGE_3 = createRecordMessage(RECORD_VALUE_3)

        private const val RECORD_VALUE_4 = "jkl"
        private val RECORD_MESSAGE_4 = createRecordMessage(RECORD_VALUE_4)

        private const val RECORD_VALUE_5 = "xyz"
        private val RECORD_MESSAGE_5 = createRecordMessage(RECORD_VALUE_5)

        private fun createRecordMessage(recordValue: String): AirbyteMessage {
            return AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, recordValue)))
                )
        }

        private fun createStateMessage(
            recordValue: String,
            cursorRecordCount: Long,
            statsRecordCount: Double
        ): AirbyteMessage {
            val dbStreamState =
                DbStreamState()
                    .withCursorField(listOf(UUID_FIELD_NAME))
                    .withCursor(recordValue)
                    .withStreamName(STREAM_NAME)
                    .withStreamNamespace(NAMESPACE)
            if (cursorRecordCount > 0) {
                dbStreamState.withCursorRecordCount(cursorRecordCount)
            }
            val dbState = DbState().withCdc(false).withStreams(listOf(dbStreamState))
            return AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(STREAM_NAME)
                                        .withNamespace(NAMESPACE)
                                )
                                .withStreamState(Jsons.jsonNode(dbStreamState))
                        )
                        .withData(Jsons.jsonNode(dbState))
                        .withSourceStats(AirbyteStateStats().withRecordCount(statsRecordCount))
                )
        }

        private fun createEmptyStateMessage(statsRecordCount: Double): AirbyteMessage {
            val dbStreamState =
                DbStreamState()
                    .withCursorField(listOf(UUID_FIELD_NAME))
                    .withStreamName(STREAM_NAME)
                    .withStreamNamespace(NAMESPACE)

            val dbState = DbState().withCdc(false).withStreams(listOf(dbStreamState))
            return AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(STREAM_NAME)
                                        .withNamespace(NAMESPACE)
                                )
                                .withStreamState(Jsons.jsonNode(dbStreamState))
                        )
                        .withData(Jsons.jsonNode(dbState))
                        .withSourceStats(AirbyteStateStats().withRecordCount(statsRecordCount))
                )
        }

        private lateinit var messageIterator: Iterator<AirbyteMessage>
    }
}
