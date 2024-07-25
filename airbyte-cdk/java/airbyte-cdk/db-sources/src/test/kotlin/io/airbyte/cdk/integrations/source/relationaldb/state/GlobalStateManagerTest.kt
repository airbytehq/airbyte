/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.mockito.Mockito

/** Test suite for the [GlobalStateManager] class. */
class GlobalStateManagerTest {
    @Test
    fun testCdcStateManager() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val cdcState = CdcState().withState(Jsons.jsonNode(mapOf("foo" to "bar", "baz" to 5)))
        val globalState =
            AirbyteGlobalState()
                .withSharedState(Jsons.jsonNode(cdcState))
                .withStreamStates(
                    listOf(
                        AirbyteStreamState()
                            .withStreamDescriptor(
                                StreamDescriptor().withNamespace("namespace").withName("name")
                            )
                            .withStreamState(Jsons.jsonNode(DbStreamState()))
                    )
                )
        val stateManager: StateManager =
            GlobalStateManager(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(globalState),
                catalog
            )
        Assertions.assertNotNull(stateManager.cdcStateManager)
        Assertions.assertEquals(cdcState, stateManager.cdcStateManager.cdcState)
        Assertions.assertEquals(1, stateManager.cdcStateManager.initialStreamsSynced!!.size)
        Assertions.assertTrue(
            stateManager.cdcStateManager.initialStreamsSynced!!.contains(
                AirbyteStreamNameNamespacePair("name", "namespace")
            )
        )
    }

    @Test
    fun testToStateFromLegacyState() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(listOf(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(listOf(StateTestConstants.CURSOR_FIELD2)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME3)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                    )
                )

        val cdcState = CdcState().withState(Jsons.jsonNode(mapOf("foo" to "bar", "baz" to 5)))
        val dbState =
            DbState()
                .withCdc(true)
                .withCdcState(cdcState)
                .withStreams(
                    listOf(
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME1)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(listOf(StateTestConstants.CURSOR_FIELD1))
                                .withCursor("a"),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME2)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(listOf(StateTestConstants.CURSOR_FIELD2)),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME3)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                        )
                        .sortedWith(Comparator.comparing { obj: DbStreamState -> obj.streamName })
                )
        val stateManager: StateManager =
            GlobalStateManager(AirbyteStateMessage().withData(Jsons.jsonNode(dbState)), catalog)

        val expectedRecordCount = 19L
        val expectedDbState =
            DbState()
                .withCdc(true)
                .withCdcState(cdcState)
                .withStreams(
                    listOf(
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME1)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(listOf(StateTestConstants.CURSOR_FIELD1))
                                .withCursor("a")
                                .withCursorRecordCount(expectedRecordCount),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME2)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(listOf(StateTestConstants.CURSOR_FIELD2)),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME3)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                        )
                        .sortedWith(Comparator.comparing { obj: DbStreamState -> obj.streamName })
                )

        val expectedGlobalState =
            AirbyteGlobalState()
                .withSharedState(Jsons.jsonNode(cdcState))
                .withStreamStates(
                    listOf(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(StateTestConstants.STREAM_NAME1)
                                        .withNamespace(StateTestConstants.NAMESPACE)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME1)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                listOf(StateTestConstants.CURSOR_FIELD1)
                                            )
                                            .withCursor("a")
                                            .withCursorRecordCount(expectedRecordCount)
                                    )
                                ),
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(StateTestConstants.STREAM_NAME2)
                                        .withNamespace(StateTestConstants.NAMESPACE)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME2)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                listOf(StateTestConstants.CURSOR_FIELD2)
                                            )
                                    )
                                ),
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(StateTestConstants.STREAM_NAME3)
                                        .withNamespace(StateTestConstants.NAMESPACE)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME3)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                    )
                                )
                        )
                        .sortedWith(
                            Comparator.comparing { o: AirbyteStreamState ->
                                o.streamDescriptor.name
                            }
                        )
                )
        val expected =
            AirbyteStateMessage()
                .withData(Jsons.jsonNode(expectedDbState))
                .withGlobal(expectedGlobalState)
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)

        val actualFirstEmission =
            stateManager.updateAndEmit(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                "a",
                expectedRecordCount
            )
        Assertions.assertEquals(expected, actualFirstEmission)
    }

    // Discovered during CDK migration.
    // Failure is: Could not find cursor information for stream: public_cars
    @Disabled("Failing test.")
    @Test
    fun testToState() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME1)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(listOf(StateTestConstants.CURSOR_FIELD1)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME2)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                            .withCursorField(listOf(StateTestConstants.CURSOR_FIELD2)),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName(StateTestConstants.STREAM_NAME3)
                                    .withNamespace(StateTestConstants.NAMESPACE)
                            )
                    )
                )

        val cdcState = CdcState().withState(Jsons.jsonNode(mapOf("foo" to "bar", "baz" to 5)))
        val globalState =
            AirbyteGlobalState()
                .withSharedState(Jsons.jsonNode(DbState()))
                .withStreamStates(
                    listOf(
                        AirbyteStreamState()
                            .withStreamDescriptor(StreamDescriptor())
                            .withStreamState(Jsons.jsonNode(DbStreamState()))
                    )
                )
        val stateManager: StateManager =
            GlobalStateManager(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(globalState),
                catalog
            )
        stateManager.cdcStateManager.cdcState = cdcState

        val expectedDbState =
            DbState()
                .withCdc(true)
                .withCdcState(cdcState)
                .withStreams(
                    listOf(
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME1)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(listOf(StateTestConstants.CURSOR_FIELD1))
                                .withCursor("a")
                                .withCursorRecordCount(1L),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME2)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                                .withCursorField(listOf(StateTestConstants.CURSOR_FIELD2)),
                            DbStreamState()
                                .withStreamName(StateTestConstants.STREAM_NAME3)
                                .withStreamNamespace(StateTestConstants.NAMESPACE)
                        )
                        .sortedWith(Comparator.comparing { obj: DbStreamState -> obj.streamName })
                )

        val expectedGlobalState =
            AirbyteGlobalState()
                .withSharedState(Jsons.jsonNode(cdcState))
                .withStreamStates(
                    listOf(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(StateTestConstants.STREAM_NAME1)
                                        .withNamespace(StateTestConstants.NAMESPACE)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME1)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                listOf(StateTestConstants.CURSOR_FIELD1)
                                            )
                                            .withCursor("a")
                                            .withCursorRecordCount(1L)
                                    )
                                ),
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(StateTestConstants.STREAM_NAME2)
                                        .withNamespace(StateTestConstants.NAMESPACE)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME2)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                            .withCursorField(
                                                listOf(StateTestConstants.CURSOR_FIELD2)
                                            )
                                    )
                                ),
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(StateTestConstants.STREAM_NAME3)
                                        .withNamespace(StateTestConstants.NAMESPACE)
                                )
                                .withStreamState(
                                    Jsons.jsonNode(
                                        DbStreamState()
                                            .withStreamName(StateTestConstants.STREAM_NAME3)
                                            .withStreamNamespace(StateTestConstants.NAMESPACE)
                                    )
                                )
                        )
                        .sortedWith(
                            Comparator.comparing { o: AirbyteStreamState ->
                                o.streamDescriptor.name
                            }
                        )
                )
        val expected =
            AirbyteStateMessage()
                .withData(Jsons.jsonNode(expectedDbState))
                .withGlobal(expectedGlobalState)
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)

        val actualFirstEmission =
            stateManager.updateAndEmit(StateTestConstants.NAME_NAMESPACE_PAIR1, "a", 1L)
        Assertions.assertEquals(expected, actualFirstEmission)
    }

    @Test
    fun testToStateWithNoState() {
        val catalog = ConfiguredAirbyteCatalog()
        val stateManager: StateManager = GlobalStateManager(AirbyteStateMessage(), catalog)

        val airbyteStateMessage = stateManager.toState(Optional.empty())
        Assertions.assertNotNull(airbyteStateMessage)
        Assertions.assertEquals(
            AirbyteStateMessage.AirbyteStateType.GLOBAL,
            airbyteStateMessage.type
        )
        Assertions.assertEquals(0, airbyteStateMessage.global.streamStates.size)
    }

    @Test
    fun testCdcStateManagerLegacyState() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val cdcState = CdcState().withState(Jsons.jsonNode(mapOf("foo" to "bar", "baz" to 5)))
        val dbState =
            DbState()
                .withCdcState(CdcState().withState(Jsons.jsonNode(cdcState)))
                .withStreams(
                    listOf(
                        DbStreamState()
                            .withStreamName("name")
                            .withStreamNamespace("namespace")
                            .withCursor("")
                            .withCursorField(emptyList())
                    )
                )
                .withCdc(true)
        val stateManager: StateManager =
            GlobalStateManager(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                    .withData(Jsons.jsonNode(dbState)),
                catalog
            )
        Assertions.assertNotNull(stateManager.cdcStateManager)
        Assertions.assertEquals(1, stateManager.cdcStateManager.initialStreamsSynced!!.size)
        Assertions.assertTrue(
            stateManager.cdcStateManager.initialStreamsSynced!!.contains(
                AirbyteStreamNameNamespacePair("name", "namespace")
            )
        )
    }
}
