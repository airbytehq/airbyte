/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.Container
import org.testcontainers.containers.MySQLContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName

object MySqlContainerFactory {
    const val COMPATIBLE_NAME = "mysql:9.2.0"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::MySQLContainer)
    }

    sealed interface MySqlContainerModifier :
        TestContainerFactory.ContainerModifier<MySQLContainer<*>>

    data object WithNetwork : MySqlContainerModifier {
        override fun modify(container: MySQLContainer<*>) {
            container.withNetwork(Network.newNetwork())
        }
    }

    data object WithCdc : MySqlContainerModifier {
        override fun modify(container: MySQLContainer<*>) {
            container.start()
            container.execAsRoot(GTID_ON)
            container.execAsRoot(GRANT.format(container.username))
            container.execAsRoot("FLUSH PRIVILEGES;")
        }

        const val GTID_ON =
            "SET @@GLOBAL.ENFORCE_GTID_CONSISTENCY = 'ON';" +
                "SET @@GLOBAL.GTID_MODE = 'OFF_PERMISSIVE';" +
                "SET @@GLOBAL.GTID_MODE = 'ON_PERMISSIVE';" +
                "SET @@GLOBAL.GTID_MODE = 'ON';"

        const val GRANT =
            "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT " +
                "ON *.* TO '%s'@'%%';"
    }

    data object WithCdcOff : MySqlContainerModifier {
        override fun modify(container: MySQLContainer<*>) {
            container.withCommand("--skip-log-bin")
        }
    }

    fun exclusive(
        imageName: String,
        vararg modifiers: MySqlContainerModifier,
    ): MySQLContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: MySqlContainerModifier,
    ): MySQLContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun config(mySQLContainer: MySQLContainer<*>): MySqlSourceConfigurationSpecification =
        MySqlSourceConfigurationSpecification().apply {
            host = mySQLContainer.host
            port = mySQLContainer.getMappedPort(MySQLContainer.MYSQL_PORT)
            username = mySQLContainer.username
            password = mySQLContainer.password
            jdbcUrlParams = ""
            database = "test"
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
            setIncrementalValue(UserDefinedCursor)
        }

    fun MySQLContainer<*>.execAsRoot(sql: String) {
        val cleanSql: String = sql.trim().removeSuffix(";") + ";"
        log.info { "Executing SQL as root: $cleanSql" }
        val result: Container.ExecResult =
            execInContainer("mysql", "-u", "root", "-ptest", "-e", cleanSql)
        for (line in (result.stdout ?: "").lines()) {
            log.info { "STDOUT: $line" }
        }
        for (line in (result.stderr ?: "").lines()) {
            log.info { "STDOUT: $line" }
        }
        if (result.exitCode == 0) {
            return
        }
        log.error { "Exit code ${result.exitCode}" }
        throw RuntimeException("Failed to execute query $cleanSql")
    }
}
