/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import com.databricks.client.jdbc.Driver
import com.databricks.sdk.WorkspaceClient
import com.databricks.sdk.core.DatabricksConfig
import io.airbyte.integrations.destination.databricks.model.ApiAuthentication
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.model.JdbcAuthentication
import javax.sql.DataSource

object ConnectorClientsFactory {

    fun createWorkspaceClient(
        hostName: String,
        apiAuthentication: ApiAuthentication
    ): WorkspaceClient {
        return when (apiAuthentication) {
            is ApiAuthentication.PersonalAccessToken -> {
                val config =
                    DatabricksConfig()
                        .setAuthType("pat")
                        .setHost("https://$hostName")
                        .setToken(apiAuthentication.token)
                WorkspaceClient(config)
            }
            is ApiAuthentication.OAuthToken -> TODO("Not yet supported")
        }
    }

    fun createDataSource(config: DatabricksConnectorConfig): DataSource {
        val className = Driver::class.java.canonicalName
        Class.forName(className)
        val datasource = com.databricks.client.jdbc.DataSource()
        // https://community.databricks.com/t5/data-engineering/java-21-support-with-databricks-jdbc-driver/td-p/49297
        // Jdbc driver 2.3.36 still uses Apache Arrow which isn't compatible with Java 21
        // EnableArrow=0 flag is undocumented and disables ArrowBuf when reading data
        // Destinations only reads data for metadata or for comparison of actual data in tests. so
        // we don't need it to be optimized.
        val jdbcUrl =
            "jdbc:databricks://${config.hostname}:${config.port}/${config.database};transportMode=http;httpPath=${config.httpPath};EnableArrow=0"
        when (config.jdbcAuthentication) {
            is JdbcAuthentication.BasicAuthentication -> {
                datasource.userID = config.jdbcAuthentication.username
                datasource.password = config.jdbcAuthentication.password
                datasource.setURL("$jdbcUrl;AuthMech=3")
            }
            is JdbcAuthentication.OIDCAuthentication -> TODO("Not yet supported")
        }
        return datasource
    }
}
