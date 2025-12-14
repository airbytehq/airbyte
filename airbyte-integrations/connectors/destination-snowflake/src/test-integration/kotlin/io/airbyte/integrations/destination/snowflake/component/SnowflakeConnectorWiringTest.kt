/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.ConnectorWiringSuite
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.dataflow.SnowflakeAggregateFactory
import io.airbyte.integrations.destination.snowflake.write.SnowflakeWriter
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Singleton
import org.junit.jupiter.api.Test

/**
 * Validates basic Micronaut DI wiring and write path functionality for Snowflake.
 *
 * Tests:
 * 1. all beans are injectable - Catches missing @Singleton, circular dependencies, missing beans
 * 2. writer setup completes - Validates namespace creation and status gathering
 * 3. can create append stream loader - Validates StreamLoader instantiation
 * 4. stream loader start creates table - Validates table creation
 * 5. can write one record - Full write path validation (most important)
 */
@MicronautTest(environments = ["component"])
@Property(name = "airbyte.connector.operation", value = "write")
@Property(name = "micronaut.caches.table-columns.maximum-size", value = "100")
class SnowflakeConnectorWiringTest(
    override val writer: SnowflakeWriter,
    override val client: SnowflakeAirbyteClient,
    override val aggregateFactory: SnowflakeAggregateFactory,
    private val catalog: DestinationCatalog,
) : ConnectorWiringSuite {

    // Use uppercase namespace to match Snowflake's identifier behavior
    override val testNamespace: String
        get() = "TEST"

    override fun createTestStream(
        namespace: String,
        name: String,
        importType: ImportType
    ): DestinationStream = catalog.streams.first()

    @Test
    override fun `all beans are injectable`() {
        super.`all beans are injectable`()
    }

    @Test
    override fun `writer setup completes`() {
        super.`writer setup completes`()
    }

    @Test
    override fun `can create append stream loader`() {
        super.`can create append stream loader`()
    }

    @Test
    override fun `stream loader start creates table`() {
        super.`stream loader start creates table`()
    }

    @Test
    override fun `can write one record`() {
        super.`can write one record`()
    }
}

/**
 * Factory providing beans required for ConnectorWiringSuite tests.
 *
 * Creates a catalog with UPPERCASE names to match Snowflake's identifier behavior. Snowflake
 * uppercases unquoted identifiers, so we use uppercase in the catalog to ensure the test's
 * TableName matches the actual created table.
 */
@Requires(env = ["component"])
@io.micronaut.context.annotation.Factory
class SnowflakeConnectorWiringTestCatalogFactory {
    @Singleton
    @Primary
    fun catalog(): ConfiguredAirbyteCatalog {
        val jsonNodeFactory = JsonNodeFactory.instance
        val schema =
            jsonNodeFactory.objectNode().apply {
                put("type", "object")
                set<Nothing>(
                    "properties",
                    jsonNodeFactory.objectNode().apply {
                        set<Nothing>(
                            "id",
                            jsonNodeFactory.objectNode().apply { put("type", "integer") }
                        )
                        set<Nothing>(
                            "name",
                            jsonNodeFactory.objectNode().apply { put("type", "string") }
                        )
                    }
                )
            }

        // Use UPPERCASE names to match Snowflake's identifier behavior
        val stream =
            AirbyteStream()
                .withName("TEST_STREAM")
                .withNamespace("TEST")
                .withJsonSchema(schema)
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH))
                .withSourceDefinedCursor(false)
                .withSourceDefinedPrimaryKey(emptyList())

        val configuredStream =
            ConfiguredAirbyteStream()
                .withStream(stream)
                .withSyncMode(SyncMode.FULL_REFRESH)
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withCursorField(emptyList())
                .withPrimaryKey(emptyList())
                .withGenerationId(0L)
                .withMinimumGenerationId(0L)
                .withSyncId(42L)

        return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
    }
}
