/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.Network
import org.testcontainers.containers.MysqlContainer
import org.testcontainers.utility.DockerImageName

object MysqlContainerFactory {
    const val COMPATIBLE_NAME = "mysql"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::MysqlContainer)
        val osArch: String? = System.getProperty("os.arch")
        val osName: String? = System.getProperty("os.name")
        if (osArch == "aarch64" && osName?.contains("Mac") == true) {
            log.warn { "USE COLIMA WHEN RUNNING ON APPLE SILICON, or Mysql container will die." }
        }
    }

    sealed interface MysqlContainerModifier :
        TestContainerFactory.ContainerModifier<MysqlContainer>

    data object WithNetwork : MysqlContainerModifier {
        override fun modify(container: MysqlContainer) {
            container.withNetwork(Network.newNetwork())
        }
    }

    fun exclusive(
        imageName: String,
        vararg modifiers: MysqlContainerModifier,
    ): MysqlContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: MysqlContainerModifier,
    ): MysqlContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun config(mysqlContainer: MysqlContainer): MysqlSourceConfigurationJsonObject =
        MysqlSourceConfigurationJsonObject().apply {
            host = mysqlContainer.host
            port = mysqlContainer.mysqlPort
            username = mysqlContainer.username
            password = mysqlContainer.password
            jdbcUrlParams = ""
            schemas = listOf(mysqlContainer.username)
            setConnectionDataValue(ServiceName().apply { serviceName = "FREEPDB1" })
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
        }
}
