/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

/** Test suite for the [StateManagerFactory] class. */
class StateManagerFactoryTest {
    @Test
    fun testNullOrEmptyState() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.GLOBAL,
                null,
                catalog
            )
        }

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.GLOBAL,
                listOf(),
                catalog
            )
        }

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.LEGACY,
                null,
                catalog
            )
        }

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.LEGACY,
                listOf(),
                catalog
            )
        }

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.STREAM,
                null,
                catalog
            )
        }

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.STREAM,
                listOf(),
                catalog
            )
        }
    }

    @Test
    fun testLegacyStateManagerCreationFromAirbyteStateMessage() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val airbyteStateMessage = Mockito.mock(AirbyteStateMessage::class.java)
        Mockito.`when`(airbyteStateMessage.data).thenReturn(Jsons.jsonNode(DbState()))

        val stateManager =
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.LEGACY,
                List.of(airbyteStateMessage),
                catalog
            )

        Assertions.assertNotNull(stateManager)
        Assertions.assertEquals(LegacyStateManager::class.java, stateManager.javaClass)
    }

    @Test
    fun testGlobalStateManagerCreation() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val globalState =
            AirbyteGlobalState()
                .withSharedState(
                    Jsons.jsonNode(
                        DbState().withCdcState(CdcState().withState(Jsons.jsonNode(DbState())))
                    )
                )
                .withStreamStates(
                    List.of(
                        AirbyteStreamState()
                            .withStreamDescriptor(
                                StreamDescriptor().withNamespace(NAMESPACE).withName(NAME)
                            )
                            .withStreamState(Jsons.jsonNode(DbStreamState()))
                    )
                )
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(globalState)

        val stateManager =
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.GLOBAL,
                List.of(airbyteStateMessage),
                catalog
            )

        Assertions.assertNotNull(stateManager)
        Assertions.assertEquals(GlobalStateManager::class.java, stateManager.javaClass)
    }

    @Test
    fun testGlobalStateManagerCreationFromLegacyState() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val cdcState = CdcState()
        val dbState =
            DbState()
                .withCdcState(cdcState)
                .withStreams(
                    List.of(DbStreamState().withStreamName(NAME).withStreamNamespace(NAMESPACE))
                )
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(Jsons.jsonNode(dbState))

        val stateManager =
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.GLOBAL,
                List.of(airbyteStateMessage),
                catalog
            )

        Assertions.assertNotNull(stateManager)
        Assertions.assertEquals(GlobalStateManager::class.java, stateManager.javaClass)
    }

    @Test
    fun testGlobalStateManagerCreationFromStreamState() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(
                            StreamDescriptor().withName(NAME).withNamespace(NAMESPACE)
                        )
                        .withStreamState(Jsons.jsonNode(DbStreamState()))
                )

        Assertions.assertThrows(ConfigErrorException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.GLOBAL,
                List.of(airbyteStateMessage),
                catalog
            )
        }
    }

    @Test
    fun testGlobalStateManagerCreationWithLegacyDataPresent() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val globalState =
            AirbyteGlobalState()
                .withSharedState(
                    Jsons.jsonNode(
                        DbState().withCdcState(CdcState().withState(Jsons.jsonNode(DbState())))
                    )
                )
                .withStreamStates(
                    List.of(
                        AirbyteStreamState()
                            .withStreamDescriptor(
                                StreamDescriptor().withNamespace(NAMESPACE).withName(NAME)
                            )
                            .withStreamState(Jsons.jsonNode(DbStreamState()))
                    )
                )
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(globalState)
                .withData(Jsons.jsonNode(DbState()))

        val stateManager =
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.GLOBAL,
                List.of(airbyteStateMessage),
                catalog
            )

        Assertions.assertNotNull(stateManager)
        Assertions.assertEquals(GlobalStateManager::class.java, stateManager.javaClass)
    }

    @Test
    fun testStreamStateManagerCreation() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(
                            StreamDescriptor().withName(NAME).withNamespace(NAMESPACE)
                        )
                        .withStreamState(Jsons.jsonNode(DbStreamState()))
                )

        val stateManager =
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.STREAM,
                List.of(airbyteStateMessage),
                catalog
            )

        Assertions.assertNotNull(stateManager)
        Assertions.assertEquals(StreamStateManager::class.java, stateManager.javaClass)
    }

    @Test
    fun testStreamStateManagerCreationFromLegacy() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val cdcState = CdcState()
        val dbState =
            DbState()
                .withCdcState(cdcState)
                .withStreams(
                    List.of(DbStreamState().withStreamName(NAME).withStreamNamespace(NAMESPACE))
                )
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(Jsons.jsonNode(dbState))

        val stateManager =
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.STREAM,
                List.of(airbyteStateMessage),
                catalog
            )

        Assertions.assertNotNull(stateManager)
        Assertions.assertEquals(StreamStateManager::class.java, stateManager.javaClass)
    }

    @Test
    fun testStreamStateManagerCreationFromGlobal() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val globalState =
            AirbyteGlobalState()
                .withSharedState(
                    Jsons.jsonNode(
                        DbState().withCdcState(CdcState().withState(Jsons.jsonNode(DbState())))
                    )
                )
                .withStreamStates(
                    List.of(
                        AirbyteStreamState()
                            .withStreamDescriptor(
                                StreamDescriptor().withNamespace(NAMESPACE).withName(NAME)
                            )
                            .withStreamState(Jsons.jsonNode(DbStreamState()))
                    )
                )
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(globalState)

        Assertions.assertThrows(ConfigErrorException::class.java) {
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.STREAM,
                List.of(airbyteStateMessage),
                catalog
            )
        }
    }

    @Test
    fun testStreamStateManagerCreationWithLegacyDataPresent() {
        val catalog = Mockito.mock(ConfiguredAirbyteCatalog::class.java)
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(
                            StreamDescriptor().withName(NAME).withNamespace(NAMESPACE)
                        )
                        .withStreamState(Jsons.jsonNode(DbStreamState()))
                )
                .withData(Jsons.jsonNode(DbState()))

        val stateManager =
            StateManagerFactory.createStateManager(
                AirbyteStateMessage.AirbyteStateType.STREAM,
                List.of(airbyteStateMessage),
                catalog
            )

        Assertions.assertNotNull(stateManager)
        Assertions.assertEquals(StreamStateManager::class.java, stateManager.javaClass)
    }

    companion object {
        private const val NAMESPACE = "namespace"
        private const val NAME = "name"
    }
}
