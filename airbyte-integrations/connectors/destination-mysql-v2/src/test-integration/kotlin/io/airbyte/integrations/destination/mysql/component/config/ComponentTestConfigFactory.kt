package io.airbyte.integrations.destination.mysql.component.config

import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import org.testcontainers.containers.MySQLContainer

@Requires(env = ["component"])
@Factory
class ComponentTestConfigFactory {

    @Singleton
    @Primary
    fun testContainer(): MySQLContainer<*> {
        val container = MySQLContainer("mysql:8.0")
            .withDatabaseName("airbyte_test")
            .withUsername("root")
            .withPassword("test")
            // Grant all privileges to root user for testing
            .withCommand("--default-authentication-plugin=mysql_native_password")

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
            username = "root",  // Use root for full privileges
            password = container.password,
        )
    }
}
