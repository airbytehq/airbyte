/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.ssh

import io.airbyte.cdk.testcontainers.innerAddress
import io.airbyte.cdk.testcontainers.outerAddress
import io.airbyte.cdk.testutils.ContainerFactory
import jakarta.inject.Singleton
import org.testcontainers.Testcontainers
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.Network
import org.testcontainers.images.builder.ImageFromDockerfile
import org.testcontainers.utility.DockerImageName

/**
 * Wraps a container which runs an SSH bastion, a.k.a. jump server. This is useful to test SSH
 * tunneling features.
 */
@Singleton
@JvmInline
value class SshBastionContainer
private constructor(
    val container: GenericContainer<*>,
) : AutoCloseable {

    constructor(
        network: Network? = null,
        tunnelingToHostPort: Int? = null
    ) : this(SshBastionContainerFactory.exclusive(network, tunnelingToHostPort))

    val key: String
        get() = container.execInContainer("cat", "var/bastion/id_rsa").stdout

    val innerKeyAuthTunnelMethod: SshKeyAuthTunnelMethod
        get() =
            container.innerAddress().let {
                SshKeyAuthTunnelMethod(it.hostName, it.port, SSH_USER, key)
            }

    val outerKeyAuthTunnelMethod: SshKeyAuthTunnelMethod
        get() =
            container.outerAddress().let {
                SshKeyAuthTunnelMethod(it.hostName, it.port, SSH_USER, key)
            }

    val innerPasswordAuthTunnelMethod: SshPasswordAuthTunnelMethod
        get() =
            container.innerAddress().let {
                SshPasswordAuthTunnelMethod(it.hostName, it.port, SSH_USER, SSH_PASSWORD)
            }

    val outerPasswordAuthTunnelMethod: SshPasswordAuthTunnelMethod
        get() =
            container.outerAddress().let {
                SshPasswordAuthTunnelMethod(it.hostName, it.port, SSH_USER, SSH_PASSWORD)
            }

    override fun close() {
        container.close()
    }

    data object SshBastionContainerFactory : ContainerFactory<GenericContainer<*>>() {
        override fun createNewContainer(imageName: DockerImageName?): GenericContainer<*> {
            val image: ImageFromDockerfile =
                ImageFromDockerfile("bastion-test")
                    .withFileFromClasspath("Dockerfile", "bastion/Dockerfile")
            return GenericContainer<Nothing>(image).withExposedPorts(22)
        }

        fun exclusive(network: Network?, tunnelingToHostPort: Int?): GenericContainer<*> {
            if (tunnelingToHostPort != null) {
                Testcontainers.exposeHostPorts(tunnelingToHostPort)
            }
            val mods = ArrayList<NamedContainerModifier<GenericContainer<*>>>()
            if (network != null) {
                mods.add(NamedContainerModifierImpl("withNetwork") { it.withNetwork(network) })
            }
            return super.exclusive("bastion-test", mods)
        }
    }

    companion object {
        const val SSH_USER: String = "sshuser"
        const val SSH_PASSWORD: String = "secret"
    }
}
