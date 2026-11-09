/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.databricks.DatabricksBeanFactory
import io.airbyte.integrations.destination.databricks.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfigurationFactory
import io.airbyte.integrations.destination.databricks.spec.DatabricksSpecification
import io.airbyte.integrations.destination.databricks.sql.DatabricksSqlGenerator
import java.nio.file.Files
import kotlin.io.path.Path

/** Centralized provider for test infrastructure. Reads config from the secrets file. */
object DatabricksTestConfigProvider {

    fun configFromFile(): DatabricksConfiguration {
        val configStr = Files.readString(Path(CONFIG_PATH))
        val spec = Jsons.readValue(configStr, DatabricksSpecification::class.java)
        return DatabricksConfigurationFactory().makeWithoutExceptionHandling(spec)
    }

    fun configFrom(spec: ConfigurationSpecification): DatabricksConfiguration {
        val factory = DatabricksConfigurationFactory()
        return factory.makeWithoutExceptionHandling(spec as DatabricksSpecification)
    }

    fun sqlGenerator(config: DatabricksConfiguration): DatabricksSqlGenerator =
        DatabricksSqlGenerator(config)

    fun airbyteClientFrom(spec: ConfigurationSpecification): DatabricksAirbyteClient {
        val config = configFrom(spec)
        val beanFactory = DatabricksBeanFactory()
        val dataSource = beanFactory.databricksDataSource(config)
        val workspaceClient = beanFactory.workspaceClient(config)
        val sqlGenerator = sqlGenerator(config)
        return DatabricksAirbyteClient(dataSource, sqlGenerator, workspaceClient)
    }
}
