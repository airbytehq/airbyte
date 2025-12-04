/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component.config

import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.postgres.PostgresContainerHelper
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.spec.PostgresConfigurationFactory
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecificationOss
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Requires(env = ["component"])
@Factory
class ComponentTestConfigFactory {
    @Singleton
    @Primary
    fun config(): PostgresConfiguration {
        // Start the container
        PostgresContainerHelper.start()

        // Build config JSON with container connection details
        val configJson =
            """
            {
                "host": "${PostgresContainerHelper.getHost()}",
                "port": ${PostgresContainerHelper.getPort()},
                "database": "${PostgresContainerHelper.getDatabaseName()}",
                "schema": "public",
                "username": "${PostgresContainerHelper.getUsername()}",
                "password": "${PostgresContainerHelper.getPassword()}"
            }
            """.trimIndent()

        val spec = Jsons.readValue(configJson, PostgresSpecificationOss::class.java)
        return PostgresConfigurationFactory().makeWithoutExceptionHandling(spec)
    }
}
