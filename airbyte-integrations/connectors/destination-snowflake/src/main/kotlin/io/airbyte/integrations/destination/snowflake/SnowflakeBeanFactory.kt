/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.check.CheckOperationV2
import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.KeyPairAuthConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.UsernamePasswordAuthConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeRawRecordFormatter
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeRecordFormatter
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeSchemaRecordFormatter
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.File
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.util.logging.Level
import java.util.logging.Logger
import javax.sql.DataSource
import kotlin.Int
import kotlin.time.DurationUnit
import kotlin.time.toDuration
import net.snowflake.client.jdbc.SnowflakeDriver

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
internal const val DATA_SOURCE_PROPERTY_TRACING = "tracing"
internal const val DATA_SOURCE_PROPERTY_WAREHOUSE = "warehouse"
internal const val JSON_FORMAT = "JSON"
internal const val NETWORK_TIMEOUT_MINUTES: Long = 1L
internal const val PRIVATE_KEY_FILE_NAME: String = "rsa_key.p8"

@Factory
class SnowflakeBeanFactory {

    @Singleton
    fun tempTableNameGenerator(
        snowflakeConfig: SnowflakeConfiguration,
    ): TempTableNameGenerator =
        DefaultTempTableNameGenerator(internalNamespace = snowflakeConfig.internalTableSchema)

    @Singleton
    fun snowflakeConfiguration(
        configFactory: SnowflakeConfigurationFactory,
        specFactory: SnowflakeMigratingConfigurationSpecificationSupplier,
    ): SnowflakeConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /**
     * Dummy [DataSource] for the spec operation. Spec doesn't have a configuration present, so we
     * cannot create the real data source. However, to avoid having to pull conditional checks on
     * every singleton related to using the data source, we can simply create a dummy one here so
     * that everything will be wired correctly even if all of those beans are unused when running
     * the spec operation.
     */
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptySnowflakeDataSource(): DataSource {
        return object : DataSource {
            override fun getConnection(): Connection? = null
            override fun getConnection(username: String, password: String): Connection? =
                getConnection()
            override fun getLogWriter(): PrintWriter =
                PrintWriter(System.out.writer(StandardCharsets.UTF_8))
            override fun setLogWriter(out: PrintWriter) {}
            override fun setLoginTimeout(seconds: Int) {}
            override fun getLoginTimeout(): Int = 0
            override fun getParentLogger(): Logger = Logger.getGlobal()
            override fun <T : Any> unwrap(iface: Class<T>): T? = null
            override fun isWrapperFor(iface: Class<*>): Boolean = false
        }
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun snowflakeDataSource(
        snowflakeConfiguration: SnowflakeConfiguration,
        @Named("snowflakePrivateKeyFileName")
        snowflakePrivateKeyFileName: String = PRIVATE_KEY_FILE_NAME,
        @Value("\${airbyte.edition:COMMUNITY}") airbyteEdition: String,
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

                // https://docs.snowflake.com/en/developer-guide/jdbc/jdbc-parameters#tracing
                addDataSourceProperty(DATA_SOURCE_PROPERTY_TRACING, Level.SEVERE.name)
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
                    snowflakeConfiguration.schema.toSnowflakeCompatibleName()
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
    @Named("snowflakePrivateKeyFileName")
    fun snowflakePrivateKeyFileName() = PRIVATE_KEY_FILE_NAME

    @Primary
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "check")
    fun checkOperation(
        destinationChecker: DestinationCheckerV2,
        outputConsumer: OutputConsumer,
    ) = CheckOperationV2(destinationChecker, outputConsumer)

    @Singleton
    fun snowflakeRecordFormatter(
        snowflakeConfiguration: SnowflakeConfiguration
    ): SnowflakeRecordFormatter {
        return if (snowflakeConfiguration.legacyRawTablesOnly) {
            SnowflakeRawRecordFormatter()
        } else {
            SnowflakeSchemaRecordFormatter()
        }
    }

    @Singleton
    fun aggregatePublishingConfig(dataChannelMedium: DataChannelMedium): AggregatePublishingConfig {
        // NOT speed mode
        return if (dataChannelMedium == DataChannelMedium.STDIO) {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
            )
        } else {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
                maxBufferedAggregates = 6,
            )
        }
    }
}
