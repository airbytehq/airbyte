/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.Network
import org.testcontainers.containers.OracleContainer
import org.testcontainers.utility.DockerImageName

object OracleContainerFactory {
    const val COMPATIBLE_NAME = "gvenzl/oracle-xe"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::OracleContainer)
        val osArch: String? = System.getProperty("os.arch")
        val osName: String? = System.getProperty("os.name")
        if (osArch == "aarch64" && osName?.contains("Mac") == true) {
            log.warn { "USE COLIMA WHEN RUNNING ON APPLE SILICON, or Oracle container will die." }
        }
    }

    sealed interface OracleContainerModifier :
        TestContainerFactory.ContainerModifier<OracleContainer>

    data object WithNetwork : OracleContainerModifier {
        override fun modify(container: OracleContainer) {
            container.withNetwork(Network.newNetwork())
        }
    }

    fun exclusive(
        imageName: String,
        vararg modifiers: OracleContainerModifier,
    ): OracleContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: OracleContainerModifier,
    ): OracleContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun config(oracleContainer: OracleContainer): OracleSourceConfigurationJsonObject =
        OracleSourceConfigurationJsonObject().apply {
            host = oracleContainer.host
            port = oracleContainer.oraclePort
            username = oracleContainer.username
            password = oracleContainer.password
            jdbcUrlParams = ""
            schemas = listOf(oracleContainer.username)
            setConnectionDataValue(ServiceName().apply { serviceName = "FREEPDB1" })
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
        }
}
