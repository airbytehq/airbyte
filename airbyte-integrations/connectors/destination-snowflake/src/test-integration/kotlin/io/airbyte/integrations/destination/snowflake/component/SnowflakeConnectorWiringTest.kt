/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.component.ConnectorWiringSuite
import io.airbyte.cdk.load.component.DefaultComponentTestCatalog
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.dataflow.SnowflakeAggregateFactory
import io.airbyte.integrations.destination.snowflake.write.SnowflakeWriter
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Primary
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
class SnowflakeConnectorWiringTest(
    override val writer: SnowflakeWriter,
    override val client: SnowflakeAirbyteClient,
    override val aggregateFactory: SnowflakeAggregateFactory,
) : ConnectorWiringSuite {

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
 * Factory providing beans required for ConnectorWiringSuite tests. Creates a default catalog
 * matching the test record schema.
 */
@Requires(env = ["component"])
@Singleton
class SnowflakeConnectorWiringTestCatalogFactory {
    @Singleton @Primary fun catalog(): ConfiguredAirbyteCatalog = DefaultComponentTestCatalog.make()
}
