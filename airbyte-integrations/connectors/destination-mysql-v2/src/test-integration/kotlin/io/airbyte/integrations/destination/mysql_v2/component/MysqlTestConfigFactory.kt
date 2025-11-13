/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.component

import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import io.airbyte.integrations.destination.mysql_v2.spec.SslMode
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import org.testcontainers.containers.MySQLContainer
import org.testcontainers.utility.DockerImageName

@Requires(env = ["component"])
@Factory
class MysqlTestConfigFactory {

    @Singleton
    @Primary
    fun mysqlContainer(): MySQLContainer<*> {
        val container = MySQLContainer(DockerImageName.parse("mysql:8.0"))
            .withDatabaseName("test_db")
            .withUsername("root") // Use root to allow CREATE DATABASE
            .withPassword("test_password")
            .withCommand(
                "--character-set-server=utf8mb4",
                "--collation-server=utf8mb4_unicode_ci",
                "--max_allowed_packet=67108864", // 64MB for large batches
                "--sql-mode=NO_ENGINE_SUBSTITUTION" // Relaxed SQL mode for temp table TIMESTAMP defaults
            )

        container.start()
        return container
    }

    @Singleton
    @Primary
    fun config(container: MySQLContainer<*>): MysqlConfiguration {
        return MysqlConfiguration(
            host = container.host,
            port = container.firstMappedPort,
            database = container.databaseName,
            username = "root", // Use root user
            password = container.password,
            ssl = false,
            sslMode = SslMode.DISABLED,
            jdbcUrlParams = null,
            batchSize = 5000
        )
    }
}
