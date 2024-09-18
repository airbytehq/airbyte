/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import com.databricks.client.jdbc.Driver
import com.databricks.sdk.WorkspaceClient
import com.databricks.sdk.core.DatabricksConfig
import io.airbyte.integrations.destination.databricks.model.Authentication
import io.airbyte.integrations.destination.databricks.model.BasicAuthentication
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.model.OAuth2Authentication
import javax.sql.DataSource

object DatabricksConnectorClientsFactory {

    fun createWorkspaceClient(hostName: String, authentication: Authentication): WorkspaceClient {
        val config =
            when (authentication) {
                is BasicAuthentication -> {
                    DatabricksConfig()
                        .setAuthType("pat")
                        .setHost("https://$hostName")
                        .setToken(authentication.personalAccessToken)
                }
                is OAuth2Authentication -> {
                    DatabricksConfig()
                        .setAuthType("oauth-m2m")
                        .setHost("https://$hostName")
                        .setClientId(authentication.clientId)
                        .setClientSecret(authentication.secret)
                }
            }
        return WorkspaceClient(config)
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
        datasource.host = config.hostname
        datasource.port = config.port
        datasource.httpPath = config.httpPath
        datasource.properties["catalog"] = config.database
        datasource.properties["schema"] = config.schema
        datasource.properties["EnableArrow"] = 0
        // TODO this is supposed to be the default???
        datasource.properties["statement_timeout"] = 172800
        when (config.authentication) {
            is BasicAuthentication -> {
                datasource.properties["AuthMech"] = 3
                datasource.username = "token"
                datasource.password = config.authentication.personalAccessToken
            }
            is OAuth2Authentication -> {
                datasource.properties["AuthMech"] = 11
                datasource.properties["Auth_Flow"] = 1
                datasource.properties["OAuth2ClientId"] = config.authentication.clientId
                datasource.properties["OAuth2Secret"] = config.authentication.secret
            }
        }
        return datasource
    }
}
