/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.snowflake.cdk.migrateJson

class SnowflakeMigrationConfigurationUpdater : ConfigurationUpdater {
    override fun update(config: String): String =
        (Jsons.readTree(migrateJson(config)) as ObjectNode)
            .apply { put("raw_data_schema", TEST_INTERNAL_SCHEMA) }
            .serializeToString()

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String,
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            updatedConfig = config.replace("TEXT_SCHEMA", defaultNamespace),
            actualDefaultNamespace = defaultNamespace,
        )

    companion object {
        /**
         * Raw tables (legacy raw-tables mode) and temp tables + stages (direct-load mode) are
         * written to `raw_data_schema` rather than the per-test namespace. Pointing it at a
         * `test`-prefixed schema means [SnowflakeDataCleaner] sweeps them along with everything
         * else. One schema per JVM is enough: table names already embed the per-test namespace.
         */
        val TEST_INTERNAL_SCHEMA: String = "${IntegrationTest.generateRandomNamespace()}_internal"
    }
}
