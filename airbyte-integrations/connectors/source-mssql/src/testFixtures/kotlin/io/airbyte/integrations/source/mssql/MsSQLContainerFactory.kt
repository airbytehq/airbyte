/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.test.fixtures.legacy.ContainerFactory
import org.apache.commons.lang3.StringUtils
import org.testcontainers.containers.MSSQLServerContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName

class MsSQLContainerFactory : ContainerFactory<MSSQLServerContainer<*>>() {
    override fun createNewContainer(imageName: DockerImageName): MSSQLServerContainer<*> {
        val realImageName = imageName.asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server")
        val container: MSSQLServerContainer<*> = MSSQLServerContainer(realImageName).acceptLicense()
        container.addEnv("MSSQL_MEMORY_LIMIT_MB", "384")
        withNetwork(container)
        return container
    }

    companion object {
        /**
         * Create a new network and bind it to the container.
         */
        fun withNetwork(container: MSSQLServerContainer<*>) {
            container.withNetwork(Network.newNetwork())
        }

        fun withAgent(container: MSSQLServerContainer<*>) {
            container.addEnv("MSSQL_AGENT_ENABLED", "True")
        }

        fun withSslCertificates(container: MSSQLServerContainer<*>) {
            // yes, this is uglier than sin. The reason why I'm doing this is because there's no command to
            // reload a SqlServer config. So I need to create all the necessary files before I start the
            // SQL server. Hence this horror
            val command = StringUtils.replace(
                """
        mkdir /tmp/certs/ &&
        openssl req -nodes -new -x509 -sha256 -keyout /tmp/certs/ca.key -out /tmp/certs/ca.crt -subj "/CN=ca" &&
        openssl req -nodes -new -x509 -sha256 -keyout /tmp/certs/dummy_ca.key -out /tmp/certs/dummy_ca.crt -subj "/CN=ca" &&
        openssl req -nodes -new -sha256 -keyout /tmp/certs/server.key -out /tmp/certs/server.csr -subj "/CN={hostName}" &&
        openssl req -nodes -new -sha256 -keyout /tmp/certs/dummy_server.key -out /tmp/certs/dummy_server.csr -subj "/CN={hostName}" &&

        openssl x509 -req -in /tmp/certs/server.csr -CA /tmp/certs/ca.crt -CAkey /tmp/certs/ca.key -out /tmp/certs/server.crt -days 365 -sha256 &&
        openssl x509 -req -in /tmp/certs/dummy_server.csr -CA /tmp/certs/ca.crt -CAkey /tmp/certs/ca.key -out /tmp/certs/dummy_server.crt -days 365 -sha256 &&
        openssl x509 -req -in /tmp/certs/server.csr -CA /tmp/certs/dummy_ca.crt -CAkey /tmp/certs/dummy_ca.key -out /tmp/certs/server_dummy_ca.crt -days 365 -sha256 &&
        chmod 440 /tmp/certs/* &&
        {
        cat > /var/opt/mssql/mssql.conf <<- EOF
        [network]
          tlscert = /tmp/certs/server.crt
          tlskey = /tmp/certs/server.key
          tlsprotocols = 1.2
          forceencryption = 1
        EOF
        } && /opt/mssql/bin/sqlservr
        
        """.trimIndent(),
                "{hostName}", container.host
            )
            container.withCommand("bash", "-c", command)
                .withUrlParam("trustServerCertificate", "true")
        }
    }
}
