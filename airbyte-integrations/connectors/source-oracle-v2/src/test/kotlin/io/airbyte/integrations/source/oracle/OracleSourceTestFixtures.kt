/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.ConfigurationFactory
import io.airbyte.cdk.testutils.ContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration
import org.testcontainers.containers.Network
import org.testcontainers.containers.OracleContainer
import org.testcontainers.utility.DockerImageName

class OracleContainerFactory : ContainerFactory<OracleContainer>() {

    override fun createNewContainer(imageName: DockerImageName?): OracleContainer {
        val osArch: String? = System.getProperty("os.arch")
        val osName: String? = System.getProperty("os.name")
        if (osArch == "aarch64" && osName?.contains("Mac") == true) {
            log.warn { "USE COLIMA WHEN RUNNING ON APPLE SILICON, or Oracle container will die. " }
        }
        val betterName: DockerImageName? = imageName?.asCompatibleSubstituteFor("gvenzl/oracle-xe")
        return OracleContainer(betterName)
    }

    companion object {

        private val log = KotlinLogging.logger {}

        val withNetwork: NamedContainerModifier<OracleContainer> =
            NamedContainerModifierImpl("withNetwork") { it.withNetwork(Network.newNetwork()) }

        @JvmStatic
        fun config(dbContainer: OracleContainer): OracleSourceConfigurationJsonObject =
            OracleSourceConfigurationJsonObject().apply {
                host = dbContainer.host
                port = dbContainer.oraclePort
                username = dbContainer.username
                password = dbContainer.password
                jdbcUrlParams = ""
                schemas = listOf(dbContainer.username)
                setConnectionDataValue(ServiceName().apply { serviceName = "FREEPDB1" })
            }
    }
}

@Singleton
@Requires(env = [Environment.TEST])
@Primary
class OracleSourceTestConfigurationFactory :
    ConfigurationFactory<OracleSourceConfigurationJsonObject, OracleSourceConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: OracleSourceConfigurationJsonObject
    ): OracleSourceConfiguration =
        OracleSourceConfigurationFactory()
            .makeWithoutExceptionHandling(pojo)
            .copy(workerConcurrency = 1, workUnitSoftTimeout = Duration.ofSeconds(3))
}
