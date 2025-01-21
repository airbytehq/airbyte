/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.Container
import org.testcontainers.containers.MySQLContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName

object MysqlContainerFactory {
    const val COMPATIBLE_NAME = "mysql:8.0"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::MySQLContainer)
    }

    sealed interface MysqlContainerModifier :
        TestContainerFactory.ContainerModifier<MySQLContainer<*>>

    data object WithNetwork : MysqlContainerModifier {
        override fun modify(container: MySQLContainer<*>) {
            container.withNetwork(Network.newNetwork())
        }
    }

    data object WithCdcOff : MysqlContainerModifier {
        override fun modify(container: MySQLContainer<*>) {
            container.withCommand("--skip-log-bin")
        }
    }

    fun exclusive(
        imageName: String,
        vararg modifiers: MysqlContainerModifier,
    ): MySQLContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: MysqlContainerModifier,
    ): MySQLContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun config(mySQLContainer: MySQLContainer<*>): MysqlSourceConfigurationSpecification =
        MysqlSourceConfigurationSpecification().apply {
            host = mySQLContainer.host
            port = mySQLContainer.getMappedPort(MySQLContainer.MYSQL_PORT)
            username = mySQLContainer.username
            password = mySQLContainer.password
            jdbcUrlParams = ""
            database = "test"
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
            setMethodValue(UserDefinedCursor)
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
