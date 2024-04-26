/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.consumers.BufferingCatalogValidationFailureHandler
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
class StateManagerTest {

    @Inject lateinit var config: SourceConfiguration
    @Inject lateinit var configuredCatalog: ConfiguredAirbyteCatalog
    @Inject lateinit var inputState: InputState
    @Inject lateinit var stateManagerFactory: StateManagerFactory
    @Inject lateinit var handler: BufferingCatalogValidationFailureHandler

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "airbyte.connector.config.cursor.cursor_method", value = "user_defined")
    @Property(name = "airbyte.connector.catalog.resource", value = "read/cursor-catalog.json")
    @Property(name = "airbyte.connector.state.json", value = "[]")
    @Property(name = "metadata.resource", value = "read/metadata.json")
    fun testCursorBasedEmptyState() {
        val stateManager: StateManager =
            stateManagerFactory.create(config, configuredCatalog, inputState)
        val actualCurrentStates: List<State<*>> =
            stateManager.currentStates().sortedBy { it.key.toString() }
        Assertions.assertEquals(2, actualCurrentStates.size)
        val kv = actualCurrentStates[0]
        Assertions.assertTrue(kv is FullRefreshNotStarted && kv.key.name == "KV", kv.toString())
        val events = actualCurrentStates[1]
        Assertions.assertTrue(
            events is CursorBasedNotStarted && events.key.name == "EVENTS",
            events.toString()
        )
    }

    // TODO: flesh this out
}
