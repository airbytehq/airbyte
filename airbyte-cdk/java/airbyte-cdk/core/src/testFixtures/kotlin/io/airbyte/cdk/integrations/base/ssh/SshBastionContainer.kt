/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.ssh

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.util.HostPortResolver
import io.airbyte.cdk.testutils.ContainerFactory
import io.airbyte.commons.json.Jsons
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
                super.exclusive(
                    "bastion-test",
                    NamedContainerModifierImpl("withNetwork", imageModifier)
                )
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
            ImmutableMap.builder<Any?, Any?>()
                .put("tunnel_host", Objects.requireNonNull(containerAddress!!.left))
                .put("tunnel_method", tunnelMethod)
                .put("tunnel_port", containerAddress.right)
                .put("tunnel_user", SSH_USER)
                .put(
                    "tunnel_user_password",
                    if (tunnelMethod == SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH) SSH_PASSWORD
                    else ""
                )
                .put(
                    "ssh_key",
                    if (tunnelMethod == SshTunnel.TunnelMethod.SSH_KEY_AUTH)
                        container!!.execInContainer("cat", "var/bastion/id_rsa").stdout
                    else ""
                )
                .build()
        )
    }

    @Throws(IOException::class, InterruptedException::class)
    fun getTunnelConfig(
        tunnelMethod: SshTunnel.TunnelMethod,
        builderWithSchema: ImmutableMap.Builder<Any, Any>,
        innerAddress: Boolean
    ): JsonNode? {
        return Jsons.jsonNode(
            builderWithSchema
                .put("tunnel_method", getTunnelMethod(tunnelMethod, innerAddress))
                .build()
        )
    }

    fun getBasicDbConfigBuider(db: JdbcDatabaseContainer<*>): ImmutableMap.Builder<Any, Any> {
        return getBasicDbConfigBuider(db, db.databaseName)
    }

    fun getBasicDbConfigBuider(
        db: JdbcDatabaseContainer<*>,
        schemas: MutableList<String>
    ): ImmutableMap.Builder<Any, Any> {
        return getBasicDbConfigBuider(db, db.databaseName).put("schemas", schemas)
    }

    fun getBasicDbConfigBuider(
        db: JdbcDatabaseContainer<*>,
        schemaName: String
    ): ImmutableMap.Builder<Any, Any> {
        return ImmutableMap.builder<Any, Any>()
            .put("host", Objects.requireNonNull(HostPortResolver.resolveHost(db)))
            .put("username", db.username)
            .put("password", db.password)
            .put("port", HostPortResolver.resolvePort(db))
            .put("database", schemaName)
            .put("ssl", false)
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
