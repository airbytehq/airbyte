/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

/** Test suite for the [StreamStateManager] class. */
class StreamStateManagerTest {
    @Test
    fun testCreationFromInvalidState() {
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(
                            StreamDescriptor()
                                .withName(StateTestConstants.STREAM_NAME1)
                                .withNamespace(StateTestConstants.NAMESPACE)
                        )
                        .withStreamState(Jsons.jsonNode("Not a state object"))
                )
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)

        Assertions.assertDoesNotThrow {
            val stateManager: StateManager =
                StreamStateManager(java.util.List.of(airbyteStateMessage), catalog)
            Assertions.assertNotNull(stateManager)
        }
    }

    @Test
    fun testGetters() {
        val state: MutableList<AirbyteStateMessage> = ArrayList()
        state.add(
            createStreamState(
                StateTestConstants.STREAM_NAME1,
                StateTestConstants.NAMESPACE,
                java.util.List.of(StateTestConstants.CURSOR_FIELD1),
                StateTestConstants.CURSOR,
                0L
            )
        )
        state.add(
            createStreamState(
                StateTestConstants.STREAM_NAME2,
                StateTestConstants.NAMESPACE,
                listOf<String>(),
                null,
                0L
            )
        )

        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                    )
                )

        val stateManager: StateManager = StreamStateManager(state, catalog)

        Assertions.assertEquals(
            Optional.of(StateTestConstants.CURSOR_FIELD1),
            stateManager.getOriginalCursorField(StateTestConstants.NAME_NAMESPACE_PAIR1)
        )
        Assertions.assertEquals(
            Optional.of(StateTestConstants.CURSOR),
            stateManager.getOriginalCursor(StateTestConstants.NAME_NAMESPACE_PAIR1)
        )
        Assertions.assertEquals(
            Optional.of(StateTestConstants.CURSOR_FIELD1),
            stateManager.getCursorField(StateTestConstants.NAME_NAMESPACE_PAIR1)
        )
        Assertions.assertEquals(
            Optional.of(StateTestConstants.CURSOR),
            stateManager.getCursor(StateTestConstants.NAME_NAMESPACE_PAIR1)
        )

        Assertions.assertEquals(
            Optional.empty<Any>(),
            stateManager.getOriginalCursorField(StateTestConstants.NAME_NAMESPACE_PAIR2)
        )
        Assertions.assertEquals(
            Optional.empty<Any>(),
            stateManager.getOriginalCursor(StateTestConstants.NAME_NAMESPACE_PAIR2)
        )
        Assertions.assertEquals(
            Optional.empty<Any>(),
            stateManager.getCursorField(StateTestConstants.NAME_NAMESPACE_PAIR2)
        )
        Assertions.assertEquals(
            Optional.empty<Any>(),
            stateManager.getCursor(StateTestConstants.NAME_NAMESPACE_PAIR2)
        )
    }

    @Test
    fun testToState() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD2)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME3)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                    )
                )

        val stateManager: StateManager = StreamStateManager(createDefaultState(), catalog)

        val expectedFirstDbState =
            DbState()
                .withCdc(false)
                .withStreams(
                    java.util.List.of(
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME1)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(
                                    java.util.List.of(StateTestConstants.CURSOR_FIELD1)
                                )
                                .withCursor("a"),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME2)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(
                                    java.util.List.of(StateTestConstants.CURSOR_FIELD2)
                                ),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME3)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                        )
                        .stream()
                        .sorted(Comparator.comparing { obj: DbStreamState -> obj.streamName })
                        .toList()
                )
        val expectedFirstEmission =
            createStreamState(
                    StateTestConstants.STREAM_NAME1,
                    StateTestConstants.NAMESPACE,
                    java.util.List.of(StateTestConstants.CURSOR_FIELD1),
                    "a",
                    0L
                )
                .withData(Jsons.jsonNode(expectedFirstDbState))

        val actualFirstEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR1, "a")
        Assertions.assertEquals(expectedFirstEmission, actualFirstEmission)

        val expectedRecordCount = 17L
        val expectedSecondDbState =
            DbState()
                .withCdc(false)
                .withStreams(
                    java.util.List.of(
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME1)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(
                                    java.util.List.of(StateTestConstants.CURSOR_FIELD1)
                                )
                                .withCursor("a"),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME2)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(
                                    java.util.List.of(StateTestConstants.CURSOR_FIELD2)
                                )
                                .withCursor("b")
                                .withCursorRecordCount(expectedRecordCount),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME3)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                        )
                        .stream()
                        .sorted(Comparator.comparing { obj: DbStreamState -> obj.streamName })
                        .toList()
                )
        val expectedSecondEmission =
            createStreamState(
                    StateTestConstants.STREAM_NAME2,
                    StateTestConstants.NAMESPACE,
                    java.util.List.of(StateTestConstants.CURSOR_FIELD2),
                    "b",
                    expectedRecordCount
                )
                .withData(Jsons.jsonNode(expectedSecondDbState))

        val actualSecondEmission =
            stateManager.updateAndEmit(
                StateTestConstants.NAME_NAMESPACE_PAIR2,
                "b",
                expectedRecordCount
            )
        Assertions.assertEquals(expectedSecondEmission, actualSecondEmission)
    }

    @Test
    fun testToStateWithoutCursorInfo() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD2)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME3)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                    )
                )
        val airbyteStreamNameNamespacePair = AirbyteStreamNameNamespacePair("other", "other")

        val stateManager: StateManager = StreamStateManager(createDefaultState(), catalog)
        val airbyteStateMessage = stateManager.toState(Optional.of(airbyteStreamNameNamespacePair))
        Assertions.assertNotNull(airbyteStateMessage)
        Assertions.assertEquals(
            AirbyteStateMessage.AirbyteStateType.STREAM,
            airbyteStateMessage.type
        )
        Assertions.assertNotNull(airbyteStateMessage.stream)
    }

    @Test
    fun testToStateWithoutStreamPair() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD2)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME3)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                    )
                )

        val stateManager: StateManager = StreamStateManager(createDefaultState(), catalog)
        val airbyteStateMessage = stateManager.toState(Optional.empty())
        Assertions.assertNotNull(airbyteStateMessage)
        Assertions.assertEquals(
            AirbyteStateMessage.AirbyteStateType.STREAM,
            airbyteStateMessage.type
        )
        Assertions.assertNotNull(airbyteStateMessage.stream)
        Assertions.assertNull(airbyteStateMessage.stream.streamState)
    }

    @Test
    fun testToStateNullCursorField() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                            .withCursorField(java.util.List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(SyncMode.FULL_REFRESH)
                                    )
                            )
                    )
                )
        val stateManager: StateManager = StreamStateManager(createDefaultState(), catalog)

        val expectedFirstDbState =
            DbState()
                .withCdc(false)
                .withStreams(
                    java.util.List.of(
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME1)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(
                                    java.util.List.of(StateTestConstants.CURSOR_FIELD1)
                                )
                                .withCursor("a"),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME2)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                        )
                        .stream()
                        .sorted(Comparator.comparing { obj: DbStreamState -> obj.streamName })
                        .toList()
                )

        val expectedFirstEmission =
            createStreamState(
                    StateTestConstants.STREAM_NAME1,
                    StateTestConstants.NAMESPACE,
                    java.util.List.of(StateTestConstants.CURSOR_FIELD1),
                    "a",
                    0L
                )
                .withData(Jsons.jsonNode(expectedFirstDbState))
        val actualFirstEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR1, "a")
        Assertions.assertEquals(expectedFirstEmission, actualFirstEmission)
    }

    @Test
    fun testCdcStateManager() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val stateManager: StateManager =
            StreamStateManager(
                java.util.List.of(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(AirbyteStreamState())
                ),
                catalog
            )
        Assertions.assertThrows(UnsupportedOperationException::class.java) {
            stateManager.cdcStateManager
        }
    }

    private fun createDefaultState(): List<AirbyteStateMessage> {
        return java.util.List.of(
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(AirbyteStreamState())
        )
    }

    private fun createStreamState(
        name: String?,
        namespace: String?,
        cursorFields: List<String?>?,
        cursorValue: String?,
        cursorRecordCount: Long
    ): AirbyteStateMessage {
        val dbStreamState = DbStreamState().withStreamName(name).withStreamNamespace(namespace)

        if (cursorFields != null && !cursorFields.isEmpty()) {
            dbStreamState.withCursorField(cursorFields)
        }

        if (cursorValue != null) {
            dbStreamState.withCursor(cursorValue)
        }

        if (cursorRecordCount > 0L) {
            dbStreamState.withCursorRecordCount(cursorRecordCount)
        }

        return AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(
                AirbyteStreamState()
                    .withStreamDescriptor(
                        StreamDescriptor().withName(name).withNamespace(namespace)
                    )
                    .withStreamState(Jsons.jsonNode(dbStreamState))
            )
    }
}
