/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.write.WriteInitializationTest
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import java.nio.file.Path

/**
 * Validates write operation can initialize with real catalog loading for Snowflake.
 *
 * Tests that all beans required for catalog processing exist:
 * - RawTableNameGenerator, FinalTableNameGenerator, ColumnNameGenerator
 * - ColumnNameMapper, TableCatalog factory dependencies
 *
 * Complements ConnectorWiringSuite:
 * - ConnectorWiringSuite: Fast component test, validates write path
 * - WriteInitializationTest: Integration test, validates catalog loading
 */
class SnowflakeWriteInitializationTest : WriteInitializationTest<SnowflakeSpecification>(
    configContents = Path.of("secrets/config.json").toFile().readText(),
    configSpecClass = SnowflakeSpecification::class.java,
)
