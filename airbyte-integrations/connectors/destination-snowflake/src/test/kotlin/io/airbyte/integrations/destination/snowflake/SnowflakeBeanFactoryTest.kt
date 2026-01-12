/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.airbyte.integrations.destination.snowflake.spec.KeyPairAuthConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.UsernamePasswordAuthConfiguration
import java.io.File
import java.util.logging.Level
import kotlin.time.DurationUnit
import kotlin.time.toDuration
import net.snowflake.client.jdbc.SnowflakeDriver
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeBeanFactoryTest {

    @ParameterizedTest
    @CsvSource(value = ["OSS", "CLOUD", "ENTERPRISE"])
    fun testCreateSnowflakeDataSourcePrivateKeyAuth(airbyteEdition: String) {
        val privateKeyFile = File.createTempFile("snowflake-private-key", ".p8")
        privateKeyFile.deleteOnExit()
        val privateKey = "test-private-key"
        val privateKeyPassword = "test-private-key-password"
        val authType =
            KeyPairAuthConfiguration(
                privateKey = privateKey,
                privateKeyPassword = privateKeyPassword,
            )
        val database = "test-database"
        val host = "test-account.test-host"
        val jdbcUrlParams = "param1=foo;param2=bar"
        val role = "test-role"
        val schema = "test-schema"
        val username = "test-username"
        val warehouse = "test-warehouse"
        val snowflakeConfiguration =
            SnowflakeConfiguration(
                host = host,
                role = role,
                warehouse = warehouse,
                database = database,
                schema = schema,
                username = username,
                authType = authType,
                cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
                legacyRawTablesOnly = false,
                internalTableSchema = "snowflake",
                jdbcUrlParams = jdbcUrlParams,
                retentionPeriodDays = 1,
            )
        val factory = SnowflakeBeanFactory()
        val dataSource =
            factory.snowflakeDataSource(
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakePrivateKeyFileName = privateKeyFile.path,
                airbyteEdition = airbyteEdition,
            )
        try {
            assertEquals(HikariDataSource::class, dataSource::class)
            assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS,
                (dataSource as HikariConfig).connectionTimeout
            )
            assertEquals(10, (dataSource as HikariConfig).maximumPoolSize)
            assertEquals(0, (dataSource as HikariConfig).minimumIdle)
            assertEquals(DATA_SOURCE_IDLE_TIMEOUT_MS, (dataSource as HikariConfig).idleTimeout)
            assertEquals(-1, (dataSource as HikariConfig).initializationFailTimeout)
            assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).leakDetectionThreshold
            )
            assertEquals(
                DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).maxLifetime
            )
            assertEquals(
                SnowflakeDriver::class.qualifiedName,
                (dataSource as HikariConfig).driverClassName
            )
            assertEquals(
                "jdbc:snowflake://${snowflakeConfiguration.host}/?${snowflakeConfiguration.jdbcUrlParams}",
                (dataSource as HikariConfig).jdbcUrl
            )
            assertEquals(
                privateKeyFile.path,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_PRIVATE_KEY_FILE]
            )
            assertEquals(
                privateKeyPassword,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_PRIVATE_KEY_PASSWORD]
            )
            assertEquals(
                Level.SEVERE.name,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_TRACING]
            )
            assertEquals(
                warehouse,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_WAREHOUSE]
            )
            assertEquals(
                database,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_DATABASE]
            )
            assertEquals(
                role,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_ROLE]
            )
            assertEquals(
                schema.toSnowflakeCompatibleName(),
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_SCHEMA]
            )
            assertEquals(
                NETWORK_TIMEOUT_MINUTES.toDuration(DurationUnit.MINUTES).inWholeSeconds.toInt(),
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_NETWORK_TIMEOUT]
            )
            assertEquals(
                0,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_MULTI_STATEMENT_COUNT]
            )
            assertEquals(
                "airbyte_${airbyteEdition.lowercase()}",
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_APPLICATION]
            )
            assertEquals(
                JSON_FORMAT,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_JDBC_QUERY_RESULT_FORMAT]
            )
            assertEquals(
                "true",
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_ABORT_DETACHED_QUERY]
            )
            assertEquals(username, (dataSource as HikariConfig).username)
        } finally {
            dataSource.close()
        }
    }

    @ParameterizedTest
    @CsvSource(value = ["COMMUNITY", "CLOUD", "ENTERPRISE"])
    fun testCreateSnowflakeDataSourceUsernamePasswordAuth(airbyteEdition: String) {
        val password = "test-password"
        val authType =
            UsernamePasswordAuthConfiguration(
                password = password,
            )
        val database = "test-database"
        val host = "test-account.test-host"
        val jdbcUrlParams = "param1=foo;param2=bar"
        val role = "test-role"
        val schema = "test-schema"
        val username = "test-username"
        val warehouse = "test-warehouse"
        val snowflakeConfiguration =
            SnowflakeConfiguration(
                host = host,
                role = role,
                warehouse = warehouse,
                database = database,
                schema = schema,
                username = username,
                authType = authType,
                cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
                legacyRawTablesOnly = false,
                internalTableSchema = "snowflake",
                jdbcUrlParams = jdbcUrlParams,
                retentionPeriodDays = 1,
            )
        val factory = SnowflakeBeanFactory()
        val dataSource =
            factory.snowflakeDataSource(
                snowflakeConfiguration = snowflakeConfiguration,
                airbyteEdition = airbyteEdition,
            )
        try {
            assertEquals(HikariDataSource::class, dataSource::class)
            assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS,
                (dataSource as HikariConfig).connectionTimeout
            )
            assertEquals(10, (dataSource as HikariConfig).maximumPoolSize)
            assertEquals(0, (dataSource as HikariConfig).minimumIdle)
            assertEquals(DATA_SOURCE_IDLE_TIMEOUT_MS, (dataSource as HikariConfig).idleTimeout)
            assertEquals(-1, (dataSource as HikariConfig).initializationFailTimeout)
            assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).leakDetectionThreshold
            )
            assertEquals(
                DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).maxLifetime
            )
            assertEquals(
                SnowflakeDriver::class.qualifiedName,
                (dataSource as HikariConfig).driverClassName
            )
            assertEquals(
                "jdbc:snowflake://${snowflakeConfiguration.host}/?${snowflakeConfiguration.jdbcUrlParams}",
                (dataSource as HikariConfig).jdbcUrl
            )
            assertEquals(
                Level.SEVERE.name,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_TRACING]
            )
            assertEquals(
                warehouse,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_WAREHOUSE]
            )
            assertEquals(
                database,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_DATABASE]
            )
            assertEquals(
                role,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_ROLE]
            )
            assertEquals(
                schema.toSnowflakeCompatibleName(),
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_SCHEMA]
            )
            assertEquals(
                NETWORK_TIMEOUT_MINUTES.toDuration(DurationUnit.MINUTES).inWholeSeconds.toInt(),
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_NETWORK_TIMEOUT]
            )
            assertEquals(
                0,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_MULTI_STATEMENT_COUNT]
            )
            assertEquals(
                "airbyte_${airbyteEdition.lowercase()}",
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_APPLICATION]
            )
            assertEquals(
                JSON_FORMAT,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_JDBC_QUERY_RESULT_FORMAT]
            )
            assertEquals(
                "true",
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_ABORT_DETACHED_QUERY]
            )
            assertEquals(username, (dataSource as HikariConfig).username)
            assertEquals(password, (dataSource as HikariConfig).password)
        } finally {
            dataSource.close()
        }
    }
}
