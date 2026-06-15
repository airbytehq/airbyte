/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.databricksv2.DatabricksV2BeanFactory
import io.airbyte.integrations.destination.databricksv2.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2ConfigurationFactory
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Specification
import io.airbyte.integrations.destination.databricksv2.sql.DatabricksSqlGenerator
import java.nio.file.Files
import kotlin.io.path.Path

/** Centralized provider for test infrastructure. Reads config from the secrets file. */
object DatabricksTestConfigProvider {

    fun configFromFile(): DatabricksV2Configuration {
        val configStr = Files.readString(Path(CONFIG_PATH))
        val spec = Jsons.readValue(configStr, DatabricksV2Specification::class.java)
        return DatabricksV2ConfigurationFactory().makeWithoutExceptionHandling(spec)
    }

    fun configFrom(spec: ConfigurationSpecification): DatabricksV2Configuration {
        val factory = DatabricksV2ConfigurationFactory()
        return factory.makeWithoutExceptionHandling(spec as DatabricksV2Specification)
    }

    fun sqlGenerator(config: DatabricksV2Configuration): DatabricksSqlGenerator =
        DatabricksSqlGenerator(config)

    fun airbyteClientFrom(spec: ConfigurationSpecification): DatabricksAirbyteClient {
        val config = configFrom(spec)
        val beanFactory = DatabricksV2BeanFactory()
        val dataSource = beanFactory.databricksDataSource(config)
        val workspaceClient = beanFactory.workspaceClient(config)
        val sqlGenerator = sqlGenerator(config)
        return DatabricksAirbyteClient(dataSource, sqlGenerator, workspaceClient)
    }
}
