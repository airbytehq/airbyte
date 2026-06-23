/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import java.io.IOException
import java.util.*
import java.util.function.Consumer
import org.apache.commons.lang3.tuple.ImmutablePair
import org.testcontainers.containers.Container
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.JdbcDatabaseContainer
import org.testcontainers.containers.Network
import org.testcontainers.images.builder.ImageFromDockerfile
import org.testcontainers.utility.DockerImageName

class SshBastionContainer : AutoCloseable {
    class SshBastionContainerFactory : ContainerFactory<GenericContainer<*>>() {
        override fun createNewContainer(imageName: DockerImageName): GenericContainer<*> {
            val container: GenericContainer<*> =
                GenericContainer<Nothing>(
                        ImageFromDockerfile("bastion-test")
                            .withFileFromClasspath("Dockerfile", "bastion/Dockerfile")
                    )
                    .withExposedPorts(22)
            return container
        }

        fun exclusive(network: Network): GenericContainer<*> {
            val imageModifier = Consumer { c: GenericContainer<*> -> c.withNetwork(network) }
            val container =
                super.exclusiveInternal("bastion-test", listOf(imageModifier to "withNetwork"))
            return container
        }
    }

    var container: GenericContainer<*>? = null
        private set

    fun initAndStartBastion(network: Network) {
        container = factory!!.exclusive(network)
        container!!.start()
    }

    @Throws(IOException::class, InterruptedException::class)
    fun getTunnelMethod(tunnelMethod: SshTunnel.TunnelMethod, innerAddress: Boolean): JsonNode? {
        val containerAddress =
            if (innerAddress) getInnerContainerAddress(container!!)
            else getOuterContainerAddress(container!!)
        return Jsons.jsonNode(
            mapOf(
                "tunnel_host" to Objects.requireNonNull(containerAddress.left),
                "tunnel_method" to tunnelMethod,
                "tunnel_port" to containerAddress.right,
                "tunnel_user" to SSH_USER,
                "tunnel_user_password" to
                    if (tunnelMethod == SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH) SSH_PASSWORD
                    else "",
                "ssh_key" to
                    if (tunnelMethod == SshTunnel.TunnelMethod.SSH_KEY_AUTH)
                        container!!.execInContainer("cat", "var/bastion/id_rsa").stdout
                    else "",
            )
        )
    }

    @Throws(IOException::class, InterruptedException::class)
    fun getTunnelConfig(
        tunnelMethod: SshTunnel.TunnelMethod,
        builderWithSchema: MutableMap<String, Any?>,
        innerAddress: Boolean
    ): JsonNode? {
        builderWithSchema["tunnel_method"] = getTunnelMethod(tunnelMethod, innerAddress)
        return Jsons.jsonNode(builderWithSchema)
    }

    fun getBasicDbConfigBuider(db: JdbcDatabaseContainer<*>): MutableMap<String, Any?> {
        return getBasicDbConfigBuider(db, db.databaseName)
    }

    fun getBasicDbConfigBuider(
        db: JdbcDatabaseContainer<*>,
        schemas: MutableList<String>
    ): MutableMap<String, Any?> {
        return getBasicDbConfigBuider(db, db.databaseName).also { it["schemas"] = schemas }
    }

    fun getBasicDbConfigBuider(
        db: JdbcDatabaseContainer<*>,
        schemaName: String
    ): MutableMap<String, Any?> {
        return mutableMapOf(
            "host" to Objects.requireNonNull(HostPortResolver.resolveHost(db)),
            "username" to db.username,
            "password" to db.password,
            "port" to HostPortResolver.resolvePort(db),
            "database" to schemaName,
            "ssl" to false,
        )
    }

    fun stopAndCloseContainers(db: JdbcDatabaseContainer<*>) {
        container!!.stop()
        container!!.close()
        db.stop()
        db.close()
    }

    fun stopAndClose() {
        container!!.close()
    }

    override fun close() {
        stopAndClose()
    }

    companion object {
        private val factory: SshBastionContainerFactory? = SshBastionContainerFactory()

        private val SSH_USER: String = "sshuser"
        private val SSH_PASSWORD: String = "secret"

        @JvmStatic
        /**
         * Returns the inner docker network ip address and port of a container. This can be used to
         * reach a container from another container running on the same network
         *
         * @param container container
         * @return a pair of host and port
         */
        fun getInnerContainerAddress(container: Container<*>): ImmutablePair<String, Int> {
            return ImmutablePair.of(
                container.containerInfo.networkSettings.networks.entries.first().value.ipAddress,
                container.exposedPorts.first()
            )
        }

        @JvmStatic
        /**
         * Returns the outer docker network ip address and port of a container. This can be used to
         * reach a container from the host machine
         *
         * @param container container
         * @return a pair of host and port
         */
        fun getOuterContainerAddress(container: Container<*>): ImmutablePair<String, Int> {
            return ImmutablePair.of(container.host, container.firstMappedPort)
        }
    }
}
