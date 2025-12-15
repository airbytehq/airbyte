/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.postgres.PostgresConfigUpdater
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
class PostgresComponentTestConfigFactory {
    @Singleton
    @Primary
    fun config(): PostgresConfiguration {
        // Start the postgres container
        PostgresContainerHelper.start()

        // Create a minimal config JSON and update it with container details
        val configJson =
            """
            {
                "host": "replace_me_host",
                "port": "replace_me_port",
                "database": "replace_me_database",
                "schema": "public",
                "username": "replace_me_username",
                "password": "replace_me_password",
                "ssl": false
            }
        """

        val updatedConfig = PostgresConfigUpdater().update(configJson)
        val spec = Jsons.readValue(updatedConfig, PostgresSpecificationOss::class.java)
        return PostgresConfigurationFactory().makeWithoutExceptionHandling(spec)
    }
}
