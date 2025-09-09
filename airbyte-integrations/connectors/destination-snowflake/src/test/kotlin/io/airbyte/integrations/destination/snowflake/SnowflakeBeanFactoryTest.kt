/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.airbyte.integrations.destination.snowflake.spec.KeyPairAuthConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.UsernamePasswordAuthConfiguration
import io.mockk.every
import io.mockk.mockk
import java.io.File
import kotlin.time.DurationUnit
import kotlin.time.toDuration
import net.snowflake.client.jdbc.SnowflakeDriver
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeBeanFactoryTest {

    @ParameterizedTest
    @CsvSource(value = ["OSS", "CLOUD", "ENTERPRISE"])
    fun testCreateDataSourcePrivateKeyAuth(airbyteEdition: String) {
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
                internalTableDataset = "snowflake",
                jdbcUrlParams = jdbcUrlParams,
                retentionPeriodDays = 1,
                useMergeForUpsert = false,
            )
        val snowflakeSqlNameTransformer =
            mockk<SnowflakeSqlNameTransformer> { every { transform(any()) } answers { firstArg() } }
        val factory = SnowflakeBeanFactory()
        val dataSource =
            factory.dataSource(
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeSqlNameTransformer = snowflakeSqlNameTransformer,
                snowflakePrivateKeyFileName = privateKeyFile.path,
                airbyteEdition = airbyteEdition,
            )
        try {
            Assertions.assertEquals(HikariDataSource::class, dataSource::class)
            Assertions.assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS,
                (dataSource as HikariConfig).connectionTimeout
            )
            Assertions.assertEquals(10, (dataSource as HikariConfig).maximumPoolSize)
            Assertions.assertEquals(0, (dataSource as HikariConfig).minimumIdle)
            Assertions.assertEquals(
                DATA_SOURCE_IDLE_TIMEOUT_MS,
                (dataSource as HikariConfig).idleTimeout
            )
            Assertions.assertEquals(-1, (dataSource as HikariConfig).initializationFailTimeout)
            Assertions.assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).leakDetectionThreshold
            )
            Assertions.assertEquals(
                DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).maxLifetime
            )
            Assertions.assertEquals(
                SnowflakeDriver::class.qualifiedName,
                (dataSource as HikariConfig).driverClassName
            )
            Assertions.assertEquals(
                "jdbc:snowflake://${snowflakeConfiguration.host}/?${snowflakeConfiguration.jdbcUrlParams}",
                (dataSource as HikariConfig).jdbcUrl
            )
            Assertions.assertEquals(
                privateKeyFile.path,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_PRIVATE_KEY_FILE]
            )
            Assertions.assertEquals(
                privateKeyPassword,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_PRIVATE_KEY_PASSWORD]
            )
            Assertions.assertEquals(
                warehouse,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_WAREHOUSE]
            )
            Assertions.assertEquals(
                database,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_DATABASE]
            )
            Assertions.assertEquals(
                role,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_ROLE]
            )
            Assertions.assertEquals(
                schema,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_SCHEMA]
            )
            Assertions.assertEquals(
                NETWORK_TIMEOUT_MINUTES.toDuration(DurationUnit.MINUTES).inWholeSeconds.toInt(),
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_NETWORK_TIMEOUT]
            )
            Assertions.assertEquals(
                0,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_MULTI_STATEMENT_COUNT]
            )
            Assertions.assertEquals(
                "airbyte_${airbyteEdition.lowercase()}",
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_APPLICATION]
            )
            Assertions.assertEquals(
                JSON_FORMAT,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_JDBC_QUERY_RESULT_FORMAT]
            )
            Assertions.assertEquals(
                "true",
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_ABORT_DETACHED_QUERY]
            )
            Assertions.assertEquals(username, (dataSource as HikariConfig).username)
        } finally {
            dataSource.close()
        }
    }

    @ParameterizedTest
    @CsvSource(value = ["OSS", "CLOUD", "ENTERPRISE"])
    fun testCreateDataSourceUsernamePasswordAuth(airbyteEdition: String) {
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
                internalTableDataset = "snowflake",
                jdbcUrlParams = jdbcUrlParams,
                retentionPeriodDays = 1,
                useMergeForUpsert = false,
            )
        val snowflakeSqlNameTransformer =
            mockk<SnowflakeSqlNameTransformer> { every { transform(any()) } answers { firstArg() } }
        val factory = SnowflakeBeanFactory()
        val dataSource =
            factory.dataSource(
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeSqlNameTransformer = snowflakeSqlNameTransformer,
                airbyteEdition = airbyteEdition,
            )
        try {
            Assertions.assertEquals(HikariDataSource::class, dataSource::class)
            Assertions.assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS,
                (dataSource as HikariConfig).connectionTimeout
            )
            Assertions.assertEquals(10, (dataSource as HikariConfig).maximumPoolSize)
            Assertions.assertEquals(0, (dataSource as HikariConfig).minimumIdle)
            Assertions.assertEquals(
                DATA_SOURCE_IDLE_TIMEOUT_MS,
                (dataSource as HikariConfig).idleTimeout
            )
            Assertions.assertEquals(-1, (dataSource as HikariConfig).initializationFailTimeout)
            Assertions.assertEquals(
                DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).leakDetectionThreshold
            )
            Assertions.assertEquals(
                DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L,
                (dataSource as HikariConfig).maxLifetime
            )
            Assertions.assertEquals(
                SnowflakeDriver::class.qualifiedName,
                (dataSource as HikariConfig).driverClassName
            )
            Assertions.assertEquals(
                "jdbc:snowflake://${snowflakeConfiguration.host}/?${snowflakeConfiguration.jdbcUrlParams}",
                (dataSource as HikariConfig).jdbcUrl
            )
            Assertions.assertEquals(
                warehouse,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_WAREHOUSE]
            )
            Assertions.assertEquals(
                database,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_DATABASE]
            )
            Assertions.assertEquals(
                role,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_ROLE]
            )
            Assertions.assertEquals(
                schema,
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_SCHEMA]
            )
            Assertions.assertEquals(
                NETWORK_TIMEOUT_MINUTES.toDuration(DurationUnit.MINUTES).inWholeSeconds.toInt(),
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_NETWORK_TIMEOUT]
            )
            Assertions.assertEquals(
                0,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_MULTI_STATEMENT_COUNT]
            )
            Assertions.assertEquals(
                "airbyte_${airbyteEdition.lowercase()}",
                (dataSource as HikariConfig).dataSourceProperties[DATA_SOURCE_PROPERTY_APPLICATION]
            )
            Assertions.assertEquals(
                JSON_FORMAT,
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_JDBC_QUERY_RESULT_FORMAT]
            )
            Assertions.assertEquals(
                "true",
                (dataSource as HikariConfig)
                    .dataSourceProperties[DATA_SOURCE_PROPERTY_ABORT_DETACHED_QUERY]
            )
            Assertions.assertEquals(username, (dataSource as HikariConfig).username)
            Assertions.assertEquals(password, (dataSource as HikariConfig).password)
        } finally {
            dataSource.close()
        }
    }
}
