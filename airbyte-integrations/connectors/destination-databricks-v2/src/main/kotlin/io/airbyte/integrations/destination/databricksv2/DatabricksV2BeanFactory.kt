/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2

import com.databricks.client.jdbc.Driver
import com.databricks.sdk.WorkspaceClient
import com.databricks.sdk.core.DatabricksConfig
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2ConfigurationFactory
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Specification
import io.airbyte.integrations.destination.databricksv2.spec.OAuthConfiguration
import io.airbyte.integrations.destination.databricksv2.spec.PersonalAccessTokenConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton
import java.util.*
import javax.sql.DataSource

private const val SOCKET_TIMEOUT_SECONDS = 3600
private const val TEMPORARILY_UNAVAILABLE_RETRY_TIMEOUT_SECONDS = 300

@Factory
class DatabricksV2BeanFactory {

    @Singleton
    fun databricksConfiguration(
        configFactory: DatabricksV2ConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<DatabricksV2Specification>,
    ): DatabricksV2Configuration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /**
     * Configures byte-based aggregate publishing limits for Databricks.
     *
     * - maxRecordsPerAgg: Effectively unlimited since we rely on byte limits, not record counts.
     * - maxEstBytesPerAgg: 250 MB per aggregate, per Databricks recommendations.
     * - maxEstBytesAllAggregates: 1 GB total across all in-flight aggregates. Max pod memory.
     * - maxBufferedAggregates: matching supported concurrency of 10x the number of clusters.
     */
    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig {
        return AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000L,
            maxEstBytesPerAgg = 250_000_000L,
            maxEstBytesAllAggregates = 1_000_000_000L,
            maxBufferedAggregates = 5,
        )
    }

    @Singleton
    @Replaces(DefaultTempTableNameGenerator::class)
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    fun databricksDataSource(config: DatabricksV2Configuration): DataSource {
        val className = Driver::class.java.canonicalName
        Class.forName(className)

        val datasource = com.databricks.client.jdbc.DataSource()
        datasource.setHost(config.hostname)
        datasource.setPort(config.port.toInt())
        datasource.setHttpPath(config.httpPath)

        val props = Properties()
        props["transportMode"] = "http"
        props["ConnCatalog"] = config.database
        props["SocketTimeout"] = SOCKET_TIMEOUT_SECONDS.toString()
        // Helps the driver retries connecting to a paused/resuming warehouse
        props["TemporarilyUnavailableRetryTimeout"] =
            TEMPORARILY_UNAVAILABLE_RETRY_TIMEOUT_SECONDS.toString()
        props["query_tags"] = "partner:airbyte"

        when (config.authType) {
            is PersonalAccessTokenConfiguration -> {
                props["AuthMech"] = "3"
                datasource.setUsername("token")
                datasource.setPassword(config.authType.personalAccessToken)
            }
            is OAuthConfiguration -> {
                props["AuthMech"] = "11"
                props["Auth_Flow"] = "1"
                props["OAuth2ClientId"] = config.authType.clientId
                props["OAuth2Secret"] = config.authType.secret
            }
        }

        datasource.setProperties(props)
        return datasource
    }

    @Singleton
    fun workspaceClient(config: DatabricksV2Configuration): WorkspaceClient {
        val databricksConfig =
            when (config.authType) {
                is PersonalAccessTokenConfiguration -> {
                    DatabricksConfig()
                        .setAuthType("pat")
                        .setHost("https://${config.hostname}")
                        .setToken(config.authType.personalAccessToken)
                }
                is OAuthConfiguration -> {
                    DatabricksConfig()
                        .setAuthType("oauth-m2m")
                        .setHost("https://${config.hostname}")
                        .setClientId(config.authType.clientId)
                        .setClientSecret(config.authType.secret)
                }
            }
        return WorkspaceClient(databricksConfig)
    }
}
