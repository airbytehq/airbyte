/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.MSSQLServerContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName

object MsSqlServerContainerFactory {
    const val COMPATIBLE_NAME = "mcr.microsoft.com/mssql/server:2022-latest"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME) { imageName: DockerImageName ->
            MSSQLServerContainer(imageName).acceptLicense()
        }
    }

    sealed interface MsSqlServerContainerModifier :
        TestContainerFactory.ContainerModifier<MSSQLServerContainer<*>>

    data object WithNetwork : MsSqlServerContainerModifier {
        override fun modify(container: MSSQLServerContainer<*>) {
            container.withNetwork(Network.newNetwork())
        }
    }

    data object WithTestDatabase : MsSqlServerContainerModifier {
        override fun modify(container: MSSQLServerContainer<*>) {
            container.start()
            container.execInContainer(
                "/opt/mssql-tools18/bin/sqlcmd",
                "-S",
                "localhost",
                "-U",
                container.username,
                "-P",
                container.password,
                "-Q",
                "CREATE DATABASE test",
                "-C"
            )
        }
    }

    fun exclusive(
        imageName: String,
        vararg modifiers: MsSqlServerContainerModifier,
    ): MSSQLServerContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: MsSqlServerContainerModifier,
    ): MSSQLServerContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun config(
        msSQLContainer: MSSQLServerContainer<*>
    ): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerSourceConfigurationSpecification().apply {
            host = msSQLContainer.host
            port = msSQLContainer.getMappedPort(MSSQLServerContainer.MS_SQL_SERVER_PORT)
            username = msSQLContainer.username
            password = msSQLContainer.password
            jdbcUrlParams = ""
            database = "test" // Connect to test database
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
            setIncrementalValue(UserDefinedCursor())
        }
}
