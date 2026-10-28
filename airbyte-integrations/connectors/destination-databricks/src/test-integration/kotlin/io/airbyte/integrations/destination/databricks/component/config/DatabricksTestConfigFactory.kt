/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.component.config

import com.databricks.sdk.WorkspaceClient
import io.airbyte.cdk.load.component.config.TestConfigLoader.loadTestConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.databricks.DatabricksBeanFactory
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfigurationFactory
import io.airbyte.integrations.destination.databricks.spec.DatabricksSpecification
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import javax.sql.DataSource

@Requires(env = ["component"])
@Factory
class DatabricksTestConfigFactory {
    @Singleton
    @Primary
    fun config(): DatabricksConfiguration {
        return loadTestConfig(
            DatabricksSpecification::class.java,
            DatabricksConfigurationFactory::class.java,
            "oauth_config.json",
        )
    }

    @Singleton
    @Primary
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    @Primary
    fun databricksDataSource(config: DatabricksConfiguration): DataSource =
        DatabricksBeanFactory().databricksDataSource(config)

    @Singleton
    @Primary
    fun workspaceClient(config: DatabricksConfiguration): WorkspaceClient =
        DatabricksBeanFactory().workspaceClient(config)
}
