/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.component.config

import com.databricks.sdk.WorkspaceClient
import io.airbyte.cdk.load.component.config.TestConfigLoader.loadTestConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.databricksv2.DatabricksV2BeanFactory
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2ConfigurationFactory
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Specification
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
    fun config(): DatabricksV2Configuration {
        return loadTestConfig(
            DatabricksV2Specification::class.java,
            DatabricksV2ConfigurationFactory::class.java,
            "oauth_config.json",
        )
    }

    @Singleton
    @Primary
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    @Primary
    fun databricksDataSource(config: DatabricksV2Configuration): DataSource =
        DatabricksV2BeanFactory().databricksDataSource(config)

    @Singleton
    @Primary
    fun workspaceClient(config: DatabricksV2Configuration): WorkspaceClient =
        DatabricksV2BeanFactory().workspaceClient(config)
}
