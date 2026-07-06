/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.write

import io.airbyte.integrations.destination.databricks.DatabricksBeanFactory
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import javax.sql.DataSource

/**
 * Thread-safe singleton providing a shared [DataSource] for all integration tests. Avoids
 * recreating JDBC connections for each test class.
 */
object DatabricksTestDataSourceProvider {
    @Volatile private var dataSource: DataSource? = null

    fun get(config: DatabricksConfiguration? = null): DataSource {
        dataSource?.let {
            return it
        }
        synchronized(this) {
            dataSource?.let {
                return it
            }
            val resolvedConfig = config ?: DatabricksTestConfigProvider.configFromFile()
            val ds = DatabricksBeanFactory().databricksDataSource(resolvedConfig)
            dataSource = ds
            return ds
        }
    }
}
