/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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

    // Connection timeout for establishing the JDBC connection (seconds).
    // Databricks SQL warehouses may auto-pause and take time to resume; this value must be
    // large enough to allow for warehouse startup while still failing faster than the platform
    // job deadline.
    private const val CONNECT_TIMEOUT_SECONDS = 120

    // Socket timeout for JDBC read operations (seconds).
    // Large MERGE / T+D queries can legitimately run for tens of minutes, so we set a generous
    // ceiling. A value of 0 means "wait forever", which caused the 20+ hour hang in
    // https://github.com/airbytehq/oncall/issues/11610.
    private const val SOCKET_TIMEOUT_SECONDS = 3600

    fun createDataSource(config: DatabricksConnectorConfig): DataSource {
        val className = Driver::class.java.canonicalName
        Class.forName(className)
        val datasource = com.databricks.client.jdbc.DataSource()
        // https://community.databricks.com/t5/data-engineering/java-21-support-with-databricks-jdbc-driver/td-p/49297
        // Jdbc driver 2.3.36 still uses Apache Arrow which isn't compatible with Java 21
        // EnableArrow=0 flag is undocumented and disables ArrowBuf when reading data
        // Destinations only reads data for metadata or for comparison of actual data in tests. so
        // we don't need it to be optimized.
        //
        // ConnectTimeout / SocketTimeout prevent indefinite hangs when the warehouse is paused
        // or unresponsive. See
        // https://kb.databricks.com/dbsql/job-timeout-when-connecting-to-a-sql-endpoint-over-jdbc
        val jdbcUrl =
            "jdbc:databricks://${config.hostname}:${config.port}/${config.database}" +
                ";transportMode=http;httpPath=${config.httpPath};EnableArrow=0" +
                ";ConnectTimeout=$CONNECT_TIMEOUT_SECONDS;SocketTimeout=$SOCKET_TIMEOUT_SECONDS"
        when (config.authentication) {
            is BasicAuthentication -> {
                datasource.setURL(
                    "$jdbcUrl;AuthMech=3;UID=token;PWD=${config.authentication.personalAccessToken}"
                )
            }
            is OAuth2Authentication -> {
                datasource.setURL(
                    "$jdbcUrl;AuthMech=11;Auth_Flow=1;OAuth2ClientId=${config.authentication.clientId};OAuth2Secret=${config.authentication.secret}"
                )
            }
        }
        return datasource
    }
}
