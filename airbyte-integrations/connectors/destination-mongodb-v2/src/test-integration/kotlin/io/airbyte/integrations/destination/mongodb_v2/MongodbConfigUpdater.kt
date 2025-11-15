/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult

class MongodbConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String {
        // Replace placeholder connection string with actual Testcontainers connection string
        val connectionString = MongodbContainerHelper.getConnectionString()

        return config.replace(
            "mongodb://test:test@localhost:27017",
            connectionString
        )
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            updatedConfig = config.replace("\"database\": \"test\"", "\"database\": \"$defaultNamespace\""),
            actualDefaultNamespace = defaultNamespace
        )
}
