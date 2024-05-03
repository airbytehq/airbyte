/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.testutils.ContainerFactory
import org.testcontainers.containers.Network
import org.testcontainers.containers.OracleContainer
import org.testcontainers.utility.DockerImageName

class OracleContainerFactory : ContainerFactory<OracleContainer>() {

    override fun createNewContainer(imageName: DockerImageName?): OracleContainer =
        OracleContainer(imageName?.asCompatibleSubstituteFor("gvenzl/oracle-xe"))

    companion object {
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
