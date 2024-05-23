/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.*
import java.util.List
import java.util.Map
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

/** Test suite for the [LegacyStateManager] class. */
class LegacyStateManagerTest {
    @Test
    fun testGetters() {
        val state =
            DbState()
                .withStreams(
                    List.of(
                        DbStreamState()
                            .withStreamName(StateTestConstants.STREAM_NAME1)
                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                            .withCursorField(List.of(StateTestConstants.CURSOR_FIELD1))
                            .withCursor(StateTestConstants.CURSOR),
                        DbStreamState()
                            .withStreamName(StateTestConstants.STREAM_NAME2)
                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                    )
                )

        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                    )
                )

        val stateManager: StateManager = LegacyStateManager(state, catalog)

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
                    List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(List.of(StateTestConstants.CURSOR_FIELD2)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME3)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                    )
                )

        val stateManager: StateManager = LegacyStateManager(DbState(), catalog)

        val expectedFirstEmission =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(
                    Jsons.jsonNode(
                        DbState()
                            .withStreams(
                                List.of(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME1)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                List.of(StateTestConstants.CURSOR_FIELD1)
                                            )
                                            .withCursor("a"),
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME2)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                List.of(StateTestConstants.CURSOR_FIELD2)
                                            ),
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME3)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                    )
                                    .stream()
                                    .sorted(
                                        Comparator.comparing { obj: DbStreamState ->
                                            obj.streamName
                                        }
                                    )
                                    .toList()
                            )
                            .withCdc(false)
                    )
                )
        val actualFirstEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR1, "a")
        Assertions.assertEquals(expectedFirstEmission, actualFirstEmission)
        val expectedSecondEmission =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(
                    Jsons.jsonNode(
                        DbState()
                            .withStreams(
                                List.of(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME1)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                List.of(StateTestConstants.CURSOR_FIELD1)
                                            )
                                            .withCursor("a"),
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME2)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                List.of(StateTestConstants.CURSOR_FIELD2)
                                            )
                                            .withCursor("b"),
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME3)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                    )
                                    .stream()
                                    .sorted(
                                        Comparator.comparing { obj: DbStreamState ->
                                            obj.streamName
                                        }
                                    )
                                    .toList()
                            )
                            .withCdc(false)
                    )
                )
        val actualSecondEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR2, "b")
        Assertions.assertEquals(expectedSecondEmission, actualSecondEmission)
    }

    @Test
    fun testToStateNullCursorField() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                    )
                )
        val stateManager: StateManager = LegacyStateManager(DbState(), catalog)

        val expectedFirstEmission =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(
                    Jsons.jsonNode(
                        DbState()
                            .withStreams(
                                List.of(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME1)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                List.of(StateTestConstants.CURSOR_FIELD1)
                                            )
                                            .withCursor("a"),
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME2)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                    )
                                    .stream()
                                    .sorted(
                                        Comparator.comparing { obj: DbStreamState ->
                                            obj.streamName
                                        }
                                    )
                                    .toList()
                            )
                            .withCdc(false)
                    )
                )

        val actualFirstEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR1, "a")
        Assertions.assertEquals(expectedFirstEmission, actualFirstEmission)
    }

    @Test
    fun testCursorNotUpdatedForCdc() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    List.of(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(List.of(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                    )
                )

        val state = DbState()
        state.cdc = true
        val stateManager: StateManager = LegacyStateManager(state, catalog)

        val expectedFirstEmission =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(
                    Jsons.jsonNode(
                        DbState()
                            .withStreams(
                                List.of(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME1)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                List.of(StateTestConstants.CURSOR_FIELD1)
                                            )
                                            .withCursor(null),
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME2)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(listOf())
                                    )
                                    .stream()
                                    .sorted(
                                        Comparator.comparing { obj: DbStreamState ->
                                            obj.streamName
                                        }
                                    )
                                    .toList()
                            )
                            .withCdc(true)
                    )
                )
        val actualFirstEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR1, "a")
        Assertions.assertEquals(expectedFirstEmission, actualFirstEmission)
        val expectedSecondEmission =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(
                    Jsons.jsonNode(
                        DbState()
                            .withStreams(
                                List.of(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME1)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                List.of(StateTestConstants.CURSOR_FIELD1)
                                            )
                                            .withCursor(null),
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME2)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(listOf())
                                            .withCursor(null)
                                    )
                                    .stream()
                                    .sorted(
                                        Comparator.comparing { obj: DbStreamState ->
                                            obj.streamName
                                        }
                                    )
                                    .toList()
                            )
                            .withCdc(true)
                    )
                )
        val actualSecondEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR2, "b")
        Assertions.assertEquals(expectedSecondEmission, actualSecondEmission)
    }

    @Test
    fun testCdcStateManager() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val cdcState = CdcState().withState(Jsons.jsonNode(Map.of("foo", "bar", "baz", 5)))
        val dbState =
            DbState()
                .withCdcState(cdcState)
                .withStreams(
                    List.of(
                        DbStreamState()
                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                            .withStreamName(StateTestConstants.STREAM_NAME1)
                    )
                )
        val stateManager: StateManager = LegacyStateManager(dbState, catalog)
        Assertions.assertNotNull(stateManager.cdcStateManager)
        Assertions.assertEquals(cdcState, stateManager.cdcStateManager.cdcState)
    }
}
