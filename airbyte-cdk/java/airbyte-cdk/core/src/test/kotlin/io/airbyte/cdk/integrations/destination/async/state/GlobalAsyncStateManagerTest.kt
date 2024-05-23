/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.state

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteStateMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteStreamState
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class GlobalAsyncStateManagerTest {
    companion object {
        private const val TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES =
            (100 * 1024 * 1024 // 10MB
                )
                .toLong()
        private const val DEFAULT_NAMESPACE = "foo_namespace"
        private const val STATE_MSG_SIZE: Long = 1000
        private const val NAMESPACE = "namespace"
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = STREAM_NAME + 2
        private const val STREAM_NAME3 = STREAM_NAME + 3
        private val STREAM1_DESC: StreamDescriptor =
            StreamDescriptor().withName(STREAM_NAME).withNamespace(NAMESPACE)
        private val STREAM2_DESC: StreamDescriptor =
            StreamDescriptor().withName(STREAM_NAME2).withNamespace(NAMESPACE)
        private val STREAM3_DESC: StreamDescriptor =
            StreamDescriptor().withName(STREAM_NAME3).withNamespace(NAMESPACE)

        private val GLOBAL_STATE_MESSAGE1: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    PartialAirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL),
                )
                .withSerialized(
                    serializedState(
                        STREAM1_DESC,
                        AirbyteStateMessage.AirbyteStateType.GLOBAL,
                        Jsons.jsonNode(mapOf("cursor" to 1)),
                    ),
                )
        private val GLOBAL_STATE_MESSAGE2: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    PartialAirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL),
                )
                .withSerialized(
                    serializedState(
                        STREAM2_DESC,
                        AirbyteStateMessage.AirbyteStateType.GLOBAL,
                        Jsons.jsonNode(mapOf("cursor" to 2)),
                    ),
                )

        private val GLOBAL_STATE_MESSAGE3: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    PartialAirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL),
                )
                .withSerialized(
                    serializedState(
                        STREAM3_DESC,
                        AirbyteStateMessage.AirbyteStateType.GLOBAL,
                        Jsons.jsonNode(mapOf("cursor" to 2)),
                    ),
                )
        private val STREAM1_STATE_MESSAGE1: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    PartialAirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)),
                )
                .withSerialized(
                    serializedState(
                        STREAM1_DESC,
                        AirbyteStateMessage.AirbyteStateType.STREAM,
                        Jsons.jsonNode(mapOf("cursor" to 1)),
                    ),
                )
        private val STREAM1_STATE_MESSAGE2: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    PartialAirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)),
                )
                .withSerialized(
                    serializedState(
                        STREAM1_DESC,
                        AirbyteStateMessage.AirbyteStateType.STREAM,
                        Jsons.jsonNode(mapOf("cursor" to 2)),
                    ),
                )

        private val STREAM1_STATE_MESSAGE3: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    PartialAirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)),
                )
                .withSerialized(
                    serializedState(
                        STREAM1_DESC,
                        AirbyteStateMessage.AirbyteStateType.STREAM,
                        Jsons.jsonNode(mapOf("cursor" to 3)),
                    ),
                )
        private val STREAM2_STATE_MESSAGE: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    PartialAirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(PartialAirbyteStreamState().withStreamDescriptor(STREAM2_DESC)),
                )
                .withSerialized(
                    serializedState(
                        STREAM2_DESC,
                        AirbyteStateMessage.AirbyteStateType.STREAM,
                        Jsons.jsonNode(mapOf("cursor" to 4)),
                    ),
                )

        private fun serializedState(
            streamDescriptor: StreamDescriptor?,
            type: AirbyteStateMessage.AirbyteStateType?,
            state: JsonNode?,
        ): String {
            return when (type) {
                AirbyteStateMessage.AirbyteStateType.GLOBAL -> {
                    Jsons.serialize(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.STATE)
                            .withState(
                                AirbyteStateMessage()
                                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                                    .withGlobal(
                                        AirbyteGlobalState()
                                            .withSharedState(state)
                                            .withStreamStates(
                                                listOf(
                                                    AirbyteStreamState()
                                                        .withStreamState(Jsons.emptyObject())
                                                        .withStreamDescriptor(streamDescriptor),
                                                ),
                                            ),
                                    ),
                            ),
                    )
                }
                AirbyteStateMessage.AirbyteStateType.STREAM -> {
                    Jsons.serialize(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.STATE)
                            .withState(
                                AirbyteStateMessage()
                                    .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                                    .withStream(
                                        AirbyteStreamState()
                                            .withStreamState(state)
                                            .withStreamDescriptor(streamDescriptor),
                                    ),
                            ),
                    )
                }
                else -> throw RuntimeException("LEGACY STATE NOT SUPPORTED")
            }
        }
    }

    @Test
    internal fun testBasic() {
        val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
        val stateManager =
            GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

        val firstStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC)
        val secondStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC)
        assertEquals(firstStateId, secondStateId)

        stateManager.decrement(firstStateId, 2)
        stateManager.flushStates { e: AirbyteMessage ->
            emittedStatesFromDestination.add(
                e,
            )
        }
        // because no state message has been tracked, there is nothing to flush yet.
        val stateWithStats =
            emittedStatesFromDestination.associateWith { it.state?.destinationStats }
        assertEquals(0, stateWithStats.size)

        stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
        stateManager.flushStates { e: AirbyteMessage ->
            emittedStatesFromDestination.add(
                e,
            )
        }

        val expectedDestinationStats = AirbyteStateStats().withRecordCount(2.0)
        val stateWithStats2 =
            emittedStatesFromDestination.associateWith { it.state?.destinationStats }
        assertEquals(
            setOf(
                attachDestinationStateStats(
                    Jsons.deserialize(
                        STREAM1_STATE_MESSAGE1.serialized,
                        AirbyteMessage::class.java,
                    ),
                    expectedDestinationStats,
                ),
            ),
            stateWithStats2.keys,
        )
        assertEquals(listOf(expectedDestinationStats), stateWithStats2.values.toList())
    }

    private fun attachDestinationStateStats(
        stateMessage: AirbyteMessage,
        airbyteStateStats: AirbyteStateStats?,
    ): AirbyteMessage {
        stateMessage.state.withDestinationStats(airbyteStateStats)
        return stateMessage
    }

    @Nested
    internal inner class GlobalState {
        @Test
        fun testEmptyQueuesGlobalState() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            // GLOBAL
            stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(0.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            //
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())

            assertThrows(
                IllegalArgumentException::class.java,
            ) {
                stateManager.trackState(
                    STREAM1_STATE_MESSAGE1,
                    STATE_MSG_SIZE,
                    DEFAULT_NAMESPACE,
                )
            }
        }

        @Test
        internal fun testConversion() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            val preConvertId0: Long = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            val preConvertId1: Long = simulateIncomingRecords(STREAM2_DESC, 10, stateManager)
            val preConvertId2: Long = simulateIncomingRecords(STREAM3_DESC, 10, stateManager)
            assertEquals(3, setOf(preConvertId0, preConvertId1, preConvertId2).size)

            stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)

            // Since this is actually a global state, we can only flush after all streams are done.
            stateManager.decrement(preConvertId0, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            assertEquals(0, emittedStatesFromDestination.size)
            stateManager.decrement(preConvertId1, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            assertEquals(0, emittedStatesFromDestination.size)
            stateManager.decrement(preConvertId2, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(30.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())
        }

        @Test
        internal fun testCorrectFlushingOneStream() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            val preConvertId0: Long = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(preConvertId0, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(10.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())

            emittedStatesFromDestination.clear()

            val afterConvertId1: Long = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(afterConvertId1, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val stateWithStats2 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE2.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats2.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats2.values.toList())
        }

        @Test
        internal fun testZeroRecordFlushing() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            val preConvertId0: Long = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(preConvertId0, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(10.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())
            emittedStatesFromDestination.clear()

            stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats2 = AirbyteStateStats().withRecordCount(0.0)
            val stateWithStats2 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE2.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats2,
                    ),
                ),
                stateWithStats2.keys,
            )
            assertEquals(
                listOf(expectedDestinationStats2),
                stateWithStats2.values.toList(),
            )
            emittedStatesFromDestination.clear()

            val afterConvertId2: Long = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            stateManager.trackState(GLOBAL_STATE_MESSAGE3, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(afterConvertId2, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val stateWithStats3 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE3.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats3.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats3.values.toList())
        }

        @Test
        internal fun testCorrectFlushingManyStreams() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            val preConvertId0: Long = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            val preConvertId1: Long = simulateIncomingRecords(STREAM2_DESC, 10, stateManager)
            assertNotEquals(preConvertId0, preConvertId1)
            stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(preConvertId0, 10)
            stateManager.decrement(preConvertId1, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(20.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())
            emittedStatesFromDestination.clear()

            val afterConvertId0: Long = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            val afterConvertId1: Long = simulateIncomingRecords(STREAM2_DESC, 10, stateManager)
            assertEquals(afterConvertId0, afterConvertId1)
            stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(afterConvertId0, 20)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val stateWithStats2 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            GLOBAL_STATE_MESSAGE2.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats2.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats2.values.toList())
        }
    }

    @Nested
    internal inner class PerStreamState {
        @Test
        internal fun testEmptyQueues() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            // GLOBAL
            stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(0.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM1_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())

            assertThrows(
                IllegalArgumentException::class.java,
            ) {
                stateManager.trackState(
                    GLOBAL_STATE_MESSAGE1,
                    STATE_MSG_SIZE,
                    DEFAULT_NAMESPACE,
                )
            }
        }

        @Test
        internal fun testCorrectFlushingOneStream() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            var stateId: Long = simulateIncomingRecords(STREAM1_DESC, 3, stateManager)
            stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(stateId, 3)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(3.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM1_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())

            emittedStatesFromDestination.clear()

            stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(stateId, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats2 = AirbyteStateStats().withRecordCount(10.0)
            val stateWithStats2 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM1_STATE_MESSAGE2.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats2,
                    ),
                ),
                stateWithStats2.keys,
            )
            assertEquals(
                listOf(expectedDestinationStats2),
                stateWithStats2.values.toList(),
            )
        }

        @Test
        internal fun testZeroRecordFlushing() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            var stateId: Long = simulateIncomingRecords(STREAM1_DESC, 3, stateManager)
            stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(stateId, 3)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(3.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM1_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())
            emittedStatesFromDestination.clear()

            stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val stateWithStats2 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            val expectedDestinationStats2 = AirbyteStateStats().withRecordCount(0.0)
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM1_STATE_MESSAGE2.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats2,
                    ),
                ),
                stateWithStats2.keys,
            )
            assertEquals(
                listOf(expectedDestinationStats2),
                stateWithStats2.values.toList(),
            )
            emittedStatesFromDestination.clear()

            stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager)
            stateManager.trackState(STREAM1_STATE_MESSAGE3, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(stateId, 10)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val stateWithStats3 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            val expectedDestinationStats3 = AirbyteStateStats().withRecordCount(10.0)
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM1_STATE_MESSAGE3.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats3,
                    ),
                ),
                stateWithStats3.keys,
            )
            assertEquals(
                listOf(expectedDestinationStats3),
                stateWithStats3.values.toList(),
            )
        }

        @Test
        internal fun testCorrectFlushingManyStream() {
            val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
            val stateManager =
                GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))

            val stream1StateId: Long = simulateIncomingRecords(STREAM1_DESC, 3, stateManager)
            val stream2StateId: Long = simulateIncomingRecords(STREAM2_DESC, 7, stateManager)

            stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(stream1StateId, 3)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats = AirbyteStateStats().withRecordCount(3.0)
            val stateWithStats =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM1_STATE_MESSAGE1.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats,
                    ),
                ),
                stateWithStats.keys,
            )
            assertEquals(listOf(expectedDestinationStats), stateWithStats.values.toList())
            emittedStatesFromDestination.clear()

            stateManager.decrement(stream2StateId, 4)
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            assertEquals(listOf<Any>(), emittedStatesFromDestination)
            stateManager.trackState(STREAM2_STATE_MESSAGE, STATE_MSG_SIZE, DEFAULT_NAMESPACE)
            stateManager.decrement(stream2StateId, 3)
            // only flush state if counter is 0.
            stateManager.flushStates { e: AirbyteMessage ->
                emittedStatesFromDestination.add(
                    e,
                )
            }
            val expectedDestinationStats2 = AirbyteStateStats().withRecordCount(7.0)
            val stateWithStats2 =
                emittedStatesFromDestination.associateWith { it.state?.destinationStats }
            assertEquals(
                setOf(
                    attachDestinationStateStats(
                        Jsons.deserialize(
                            STREAM2_STATE_MESSAGE.serialized,
                            AirbyteMessage::class.java,
                        ),
                        expectedDestinationStats2,
                    ),
                ),
                stateWithStats2.keys,
            )
            assertEquals(
                listOf(expectedDestinationStats2),
                stateWithStats2.values.toList(),
            )
        }
    }

    private fun simulateIncomingRecords(
        desc: StreamDescriptor,
        count: Long,
        manager: GlobalAsyncStateManager,
    ): Long {
        var stateId = 0L
        for (i in 0 until count) {
            stateId = manager.getStateIdAndIncrementCounter(desc)
        }
        return stateId
    }

    @Test
    internal fun flushingRecordsShouldNotReduceStatsCounterForGlobalState() {
        val emittedStatesFromDestination: MutableList<AirbyteMessage> = mutableListOf()
        val stateManager =
            GlobalAsyncStateManager(GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES))
        val stateId = simulateIncomingRecords(STREAM1_DESC, 6, stateManager)
        stateManager.decrement(stateId, 4)
        stateManager.trackState(GLOBAL_STATE_MESSAGE1, 1, STREAM1_DESC.namespace)
        stateManager.flushStates { e: AirbyteMessage ->
            emittedStatesFromDestination.add(
                e,
            )
        }
        assertEquals(0, emittedStatesFromDestination.size)
        stateManager.decrement(stateId, 2)
        stateManager.flushStates { e: AirbyteMessage ->
            emittedStatesFromDestination.add(
                e,
            )
        }
        assertEquals(1, emittedStatesFromDestination.size)
        assertEquals(
            6.0,
            emittedStatesFromDestination.first().state?.destinationStats?.recordCount,
        )
    }
}
