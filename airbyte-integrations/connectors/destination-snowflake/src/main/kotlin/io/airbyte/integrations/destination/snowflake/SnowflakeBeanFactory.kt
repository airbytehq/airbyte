/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.integrations.destination.snowflake.spec.KeyPairAuthConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.airbyte.integrations.destination.snowflake.spec.UsernamePasswordAuthConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.File
import java.nio.charset.StandardCharsets
import java.util.Properties
import kotlin.time.DurationUnit
import kotlin.time.toDuration
import net.snowflake.client.jdbc.SnowflakeDriver
import net.snowflake.ingest.streaming.SnowflakeStreamingIngestClient
import net.snowflake.ingest.streaming.SnowflakeStreamingIngestClientFactory

internal const val DATA_SOURCE_CONNECTION_TIMEOUT_MS = 30000L
internal const val DATA_SOURCE_IDLE_TIMEOUT_MS = 600000L
internal const val DATA_SOURCE_PROPERTY_ABORT_DETACHED_QUERY = "ABORT_DETACHED_QUERY"
internal const val DATA_SOURCE_PROPERTY_APPLICATION = "application"
internal const val DATA_SOURCE_PROPERTY_DATABASE = "database"
internal const val DATA_SOURCE_PROPERTY_JDBC_QUERY_RESULT_FORMAT = "JDBC_QUERY_RESULT_FORMAT"
internal const val DATA_SOURCE_PROPERTY_MULTI_STATEMENT_COUNT = "MULTI_STATEMENT_COUNT"
internal const val DATA_SOURCE_PROPERTY_NETWORK_TIMEOUT = "networkTimeout"
internal const val DATA_SOURCE_PROPERTY_PRIVATE_KEY_FILE = "private_key_file"
internal const val DATA_SOURCE_PROPERTY_PRIVATE_KEY_PASSWORD = "private_key_file_pwd"
internal const val DATA_SOURCE_PROPERTY_ROLE = "role"
internal const val DATA_SOURCE_PROPERTY_SCHEMA = "schema"
internal const val DATA_SOURCE_PROPERTY_WAREHOUSE = "warehouse"
internal const val JSON_FORMAT = "JSON"
internal const val NETWORK_TIMEOUT_MINUTES: Long = 1L
internal const val PRIVATE_KEY_FILE_NAME: String = "rsa_key.p8"

@Factory
class SnowflakeBeanFactory {
    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    fun snowflakeConfiguration(
        configFactory: SnowflakeConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<SnowflakeSpecification>,
    ): SnowflakeConfiguration {
        val spec = specFactory.get()

        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    fun snowflakeDataSource(
        snowflakeConfiguration: SnowflakeConfiguration,
        snowflakeSqlNameTransformer: SnowflakeSqlNameTransformer,
        @Named("snowflakePrivateKeyFileName")
        snowflakePrivateKeyFileName: String = PRIVATE_KEY_FILE_NAME,
        @Value("\${airbyte.edition}") airbyteEdition: String,
    ): HikariDataSource {
        val snowflakeJdbcUrl =
            "jdbc:snowflake://${snowflakeConfiguration.host}/?${snowflakeConfiguration.jdbcUrlParams}"
        val datasourceConfig =
            HikariConfig().apply {
                connectionTimeout = DATA_SOURCE_CONNECTION_TIMEOUT_MS
                maximumPoolSize = 10 // TODO adjust based on speed sockets?
                minimumIdle = 0
                idleTimeout = DATA_SOURCE_IDLE_TIMEOUT_MS
                initializationFailTimeout = -1
                // This should be slightly higher than the connection-timeout setting
                // but not too high to avoid false positives and negatives.
                leakDetectionThreshold = DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L
                // This should be slightly higher than the idle timeout setting
                // but not too high to avoid connections living for too long when unused
                maxLifetime = DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L
                driverClassName = SnowflakeDriver::class.qualifiedName
                jdbcUrl = snowflakeJdbcUrl
                when (snowflakeConfiguration.authType) {
                    is KeyPairAuthConfiguration -> {
                        val privateKeyFile = File(snowflakePrivateKeyFileName)
                        privateKeyFile.deleteOnExit()
                        privateKeyFile.writeText(
                            snowflakeConfiguration.authType.privateKey,
                            StandardCharsets.UTF_8
                        )
                        addDataSourceProperty(
                            DATA_SOURCE_PROPERTY_PRIVATE_KEY_FILE,
                            snowflakePrivateKeyFileName
                        )
                        snowflakeConfiguration.authType.privateKeyPassword?.let { password ->
                            addDataSourceProperty(
                                DATA_SOURCE_PROPERTY_PRIVATE_KEY_PASSWORD,
                                password
                            )
                        }
                        username = snowflakeConfiguration.username
                    }
                    is UsernamePasswordAuthConfiguration -> {
                        username = snowflakeConfiguration.username
                        password = snowflakeConfiguration.authType.password
                    }
                }

                addDataSourceProperty(
                    DATA_SOURCE_PROPERTY_WAREHOUSE,
                    snowflakeConfiguration.warehouse
                )
                addDataSourceProperty(
                    DATA_SOURCE_PROPERTY_DATABASE,
                    snowflakeConfiguration.database
                )
                addDataSourceProperty(DATA_SOURCE_PROPERTY_ROLE, snowflakeConfiguration.role)
                addDataSourceProperty(
                    DATA_SOURCE_PROPERTY_SCHEMA,
                    snowflakeSqlNameTransformer.transform(snowflakeConfiguration.schema)
                )
                addDataSourceProperty(
                    DATA_SOURCE_PROPERTY_NETWORK_TIMEOUT,
                    Math.toIntExact(
                        NETWORK_TIMEOUT_MINUTES.toDuration(DurationUnit.MINUTES).inWholeSeconds
                    )
                )
                // allows queries to contain any number of statements.
                addDataSourceProperty(DATA_SOURCE_PROPERTY_MULTI_STATEMENT_COUNT, 0)
                // https://docs.snowflake.com/en/user-guide/jdbc-parameters.html#application
                // identify airbyte traffic to snowflake to enable partnership & optimization
                // opportunities
                addDataSourceProperty(
                    DATA_SOURCE_PROPERTY_APPLICATION,
                    "airbyte_${airbyteEdition.lowercase()}"
                )
                // Needed for JDK17 - see
                // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
                addDataSourceProperty(DATA_SOURCE_PROPERTY_JDBC_QUERY_RESULT_FORMAT, JSON_FORMAT)

                // https://docs.snowflake.com/sql-reference/parameters#abort-detached-query
                // If the connector crashes, snowflake should abort in-flight queries.
                addDataSourceProperty(DATA_SOURCE_PROPERTY_ABORT_DETACHED_QUERY, "true")
            }

        return HikariDataSource(datasourceConfig)
    }

    @Singleton
    fun snowflakeStreamingIngestClient(
        snowflakeConfiguration: SnowflakeConfiguration,
        snowflakeSqlNameTransformer: SnowflakeSqlNameTransformer,
        @Named("snowflakePrivateKeyFileName")
        snowflakePrivateKeyFileName: String = PRIVATE_KEY_FILE_NAME,
        @Value("\${airbyte.edition}") airbyteEdition: String,
    ): SnowflakeStreamingIngestClient {
        val properties =
            Properties().apply {
                // Connection properties
                setProperty("url", "https://${snowflakeConfiguration.host}")
                setProperty("account", snowflakeConfiguration.host.substringBefore("."))
                setProperty("user", snowflakeConfiguration.username)
                setProperty("role", snowflakeConfiguration.role)
                setProperty("warehouse", snowflakeConfiguration.warehouse)
                setProperty("database", snowflakeConfiguration.database)
                setProperty(
                    "schema",
                    snowflakeSqlNameTransformer.transform(snowflakeConfiguration.schema)
                )

                // Authentication
                when (snowflakeConfiguration.authType) {
                    is KeyPairAuthConfiguration -> {
                        val privateKeyFile = File("${snowflakePrivateKeyFileName}_streaming")
                        privateKeyFile.deleteOnExit()
                        privateKeyFile.writeText(
                            snowflakeConfiguration.authType.privateKey,
                            StandardCharsets.UTF_8
                        )
                        setProperty("private_key", privateKeyFile.absolutePath)
                        snowflakeConfiguration.authType.privateKeyPassword?.let { password ->
                            setProperty("private_key_passphrase", password)
                        }
                    }
                    is UsernamePasswordAuthConfiguration -> {
                        setProperty("password", snowflakeConfiguration.authType.password)
                    }
                }

                // Additional properties for streaming
                setProperty("application", "airbyte_${airbyteEdition.lowercase()}_streaming")

                // Add any JDBC URL parameters if they exist
                snowflakeConfiguration.jdbcUrlParams?.let { params ->
                    // Parse and add any additional parameters from JDBC URL params
                    params.split("&").forEach { param ->
                        val parts = param.split("=")
                        if (parts.size == 2) {
                            setProperty(parts[0], parts[1])
                        }
                    }
                }
            }

        return SnowflakeStreamingIngestClientFactory.builder(
                "airbyte_${airbyteEdition.lowercase()}_streaming_client"
            )
            .setProperties(properties)
            .build()
    }
}
