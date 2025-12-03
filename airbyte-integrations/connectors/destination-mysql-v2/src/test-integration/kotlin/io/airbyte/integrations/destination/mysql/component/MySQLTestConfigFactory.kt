/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.component

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import org.testcontainers.containers.MySQLContainer
import java.time.Clock
import javax.sql.DataSource

@Factory
@Requires(env = ["component"])
class MySQLTestConfigFactory {

    @Singleton
    @Primary
    fun testContainer(): MySQLContainer<*> {
        // Use root user to have CREATE DATABASE privileges for tests
        val container = MySQLContainer("mysql:8.0")
            .withDatabaseName("test")
            .withUsername("root")
            .withPassword("test")
            .withEnv("MYSQL_ROOT_PASSWORD", "test")
            .withCommand("--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci")

        container.start()
        return container
    }

    @Singleton
    @Primary
    fun testConfig(container: MySQLContainer<*>): MySQLConfiguration {
        return MySQLConfiguration(
            hostname = container.host,
            port = container.firstMappedPort,
            database = container.databaseName,
            username = "root",  // Use root for CREATE DATABASE privileges
            password = "test",
            sslMode = "disabled",
            tunnelConfig = null,
        )
    }

    @Singleton
    @Primary
    @Named("resolvedHost")
    fun resolvedHost(config: MySQLConfiguration): String = config.hostname

    @Singleton
    @Primary
    @Named("resolvedPort")
    fun resolvedPort(config: MySQLConfiguration): Int = config.port

    @Singleton
    @Primary
    fun testDataSource(config: MySQLConfiguration): DataSource {
        // Don't specify a database in the URL to allow namespace/database operations
        val hikariConfig = HikariConfig().apply {
            jdbcUrl = "jdbc:mysql://${config.hostname}:${config.port}/?sslMode=DISABLED&allowPublicKeyRetrieval=true&createDatabaseIfNotExist=true"
            username = config.username
            password = config.password
            maximumPoolSize = 5
            connectionTimeout = 30000
            driverClassName = "com.mysql.cj.jdbc.Driver"
        }
        return HikariDataSource(hikariConfig)
    }

    @Singleton
    @Primary
    fun testClock(): Clock = Clock.systemUTC()
}
