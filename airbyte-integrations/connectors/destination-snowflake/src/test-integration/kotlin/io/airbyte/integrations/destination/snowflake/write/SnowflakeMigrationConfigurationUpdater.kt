/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.integrations.destination.snowflake.cdk.migrateJson

class SnowflakeMigrationConfigurationUpdater : ConfigurationUpdater {
    override fun update(config: String): String = migrateJson(config)

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            updatedConfig = config.replace("TEXT_SCHEMA", defaultNamespace),
            actualDefaultNamespace = defaultNamespace
        )
}
