/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.component.config

import io.airbyte.integrations.destination.mongodb_v2.MongodbContainerHelper
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Requires(env = ["component"])
@Factory
class ComponentTestConfigFactory {
    @Singleton
    @Primary
    fun config(): MongodbConfiguration {
        // Use Testcontainers for component tests
        val connectionString = MongodbContainerHelper.getConnectionString()

        return MongodbConfiguration(
            connectionString = connectionString,
            database = "test",
            authSource = "admin",
            batchSize = 1000,
        )
    }
}
