/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.factory

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.integrations.JdbcConnector
import javax.sql.DataSource
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.testcontainers.containers.MySQLContainer

/** Test suite for the [DataSourceFactory] class. */
internal class DataSourceFactoryTest : CommonFactoryTest() {
    @Test
    fun testCreatingDataSourceWithConnectionTimeoutSetAboveDefault() {
        val connectionProperties = mapOf(CONNECT_TIMEOUT to "61")
        val dataSource =
            DataSourceFactory.create(
                username,
                password,
                driverClassName,
                jdbcUrl,
                connectionProperties,
                JdbcConnector.getConnectionTimeout(connectionProperties, driverClassName)
            )
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            61000,
            (dataSource as HikariDataSource).hikariConfigMXBean.connectionTimeout
        )
    }

    @Test
    fun testCreatingPostgresDataSourceWithConnectionTimeoutSetBelowDefault() {
        val connectionProperties = mapOf(CONNECT_TIMEOUT to "30")
        val dataSource =
            DataSourceFactory.create(
                username,
                password,
                driverClassName,
                jdbcUrl,
                connectionProperties,
                JdbcConnector.getConnectionTimeout(connectionProperties, driverClassName)
            )
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            30000,
            (dataSource as HikariDataSource).hikariConfigMXBean.connectionTimeout
        )
    }

    @Test
    fun testCreatingMySQLDataSourceWithConnectionTimeoutSetBelowDefault() {
        MySQLContainer<Nothing>("mysql:8.0").use { mySQLContainer ->
            mySQLContainer.start()
            val connectionProperties = mapOf(CONNECT_TIMEOUT to "5000")
            val dataSource =
                DataSourceFactory.create(
                    mySQLContainer.username,
                    mySQLContainer.password,
                    mySQLContainer.driverClassName,
                    mySQLContainer.getJdbcUrl(),
                    connectionProperties,
                    JdbcConnector.getConnectionTimeout(
                        connectionProperties,
                        mySQLContainer.driverClassName
                    )
                )
            Assertions.assertNotNull(dataSource)
            Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
            Assertions.assertEquals(
                5000,
                (dataSource as HikariDataSource).hikariConfigMXBean.connectionTimeout
            )
        }
    }

    @Test
    fun testCreatingDataSourceWithConnectionTimeoutSetWithZero() {
        val connectionProperties = mapOf(CONNECT_TIMEOUT to "0")
        val dataSource =
            DataSourceFactory.create(
                username,
                password,
                driverClassName,
                jdbcUrl,
                connectionProperties,
                JdbcConnector.getConnectionTimeout(connectionProperties, driverClassName)
            )
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            Int.MAX_VALUE.toLong(),
            (dataSource as HikariDataSource).hikariConfigMXBean.connectionTimeout
        )
    }

    @Test
    fun testCreatingPostgresDataSourceWithConnectionTimeoutNotSet() {
        val connectionProperties = mapOf<String, String>()
        val dataSource =
            DataSourceFactory.create(
                username,
                password,
                driverClassName,
                jdbcUrl,
                connectionProperties,
                JdbcConnector.getConnectionTimeout(connectionProperties, driverClassName)
            )
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            10000,
            (dataSource as HikariDataSource).hikariConfigMXBean.connectionTimeout
        )
    }

    @Test
    fun testCreatingMySQLDataSourceWithConnectionTimeoutNotSet() {
        MySQLContainer<Nothing>("mysql:8.0").use { mySQLContainer ->
            mySQLContainer.start()
            val connectionProperties = mapOf<String, String>()
            val dataSource =
                DataSourceFactory.create(
                    mySQLContainer.username,
                    mySQLContainer.password,
                    mySQLContainer.driverClassName,
                    mySQLContainer.getJdbcUrl(),
                    connectionProperties,
                    JdbcConnector.getConnectionTimeout(
                        connectionProperties,
                        mySQLContainer.driverClassName
                    )
                )
            Assertions.assertNotNull(dataSource)
            Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
            Assertions.assertEquals(
                60000,
                (dataSource as HikariDataSource).hikariConfigMXBean.connectionTimeout
            )
        }
    }

    @Test
    fun testCreatingADataSourceWithJdbcUrl() {
        val dataSource = DataSourceFactory.create(username, password, driverClassName, jdbcUrl)
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            10,
            (dataSource as HikariDataSource).hikariConfigMXBean.maximumPoolSize
        )
    }

    @Test
    fun testCreatingADataSourceWithJdbcUrlAndConnectionProperties() {
        val connectionProperties = mapOf("foo" to "bar")

        val dataSource =
            DataSourceFactory.create(
                username,
                password,
                driverClassName,
                jdbcUrl,
                connectionProperties,
                JdbcConnector.getConnectionTimeout(connectionProperties, driverClassName)
            )
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            10,
            (dataSource as HikariDataSource).hikariConfigMXBean.maximumPoolSize
        )
    }

    @Test
    fun testCreatingADataSourceWithHostAndPort() {
        val dataSource =
            DataSourceFactory.create(username, password, host, port, database, driverClassName)
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            10,
            (dataSource as HikariDataSource).hikariConfigMXBean.maximumPoolSize
        )
    }

    @Test
    fun testCreatingADataSourceWithHostPortAndConnectionProperties() {
        val connectionProperties = mapOf("foo" to "bar")

        val dataSource =
            DataSourceFactory.create(
                username,
                password,
                host,
                port,
                database,
                driverClassName,
                connectionProperties
            )
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            10,
            (dataSource as HikariDataSource).hikariConfigMXBean.maximumPoolSize
        )
    }

    @Test
    fun testCreatingAnInvalidDataSourceWithHostAndPort() {
        val driverClassName = "Unknown"

        Assertions.assertThrows(RuntimeException::class.java) {
            DataSourceFactory.create(username, password, host, port, database, driverClassName)
        }
    }

    @Test
    fun testCreatingAPostgresqlDataSource() {
        val dataSource = DataSourceFactory.createPostgres(username, password, host, port, database)
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            10,
            (dataSource as HikariDataSource).hikariConfigMXBean.maximumPoolSize
        )
    }

    @Test
    fun testClosingADataSource() {
        val dataSource1 = Mockito.mock(HikariDataSource::class.java)
        Assertions.assertDoesNotThrow { DataSourceFactory.close(dataSource1) }
        Mockito.verify(dataSource1, Mockito.times(1)).close()

        val dataSource2 = Mockito.mock(DataSource::class.java)
        Assertions.assertDoesNotThrow { DataSourceFactory.close(dataSource2) }

        Assertions.assertDoesNotThrow { DataSourceFactory.close(null) }
    }

    companion object {
        private const val CONNECT_TIMEOUT = "connectTimeout"

        var database: String = container.databaseName
        var driverClassName: String = container.driverClassName
        var host: String = container.host
        var jdbcUrl: String = container.getJdbcUrl()
        var password: String = container.password
        var port: Int = container.firstMappedPort
        var username: String = container.username
    }
}
