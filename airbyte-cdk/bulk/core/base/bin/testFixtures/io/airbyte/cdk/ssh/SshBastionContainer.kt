/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.ssh

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.cdk.testcontainers.innerAddress
import io.airbyte.cdk.testcontainers.outerAddress
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
        tunnelingToHostPort: Int? = null,
    ) : this(exclusive(network, tunnelingToHostPort))

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

    companion object {
        init {
            TestContainerFactory.register("bastion-test") { _: DockerImageName ->
                val image: ImageFromDockerfile =
                    ImageFromDockerfile("bastion-test")
                        .withFileFromClasspath("Dockerfile", "bastion/Dockerfile")
                GenericContainer<_>(image).withExposedPorts(22)
            }
        }

        fun exclusive(
            network: Network?,
            tunnelingToHostPort: Int?,
        ): GenericContainer<*> {
            val imageName: DockerImageName = DockerImageName.parse("bastion-test")
            if (tunnelingToHostPort != null) {
                Testcontainers.exposeHostPorts(tunnelingToHostPort)
            }
            if (network == null) {
                return TestContainerFactory.exclusive(imageName)
            }
            return TestContainerFactory.exclusive(
                imageName,
                TestContainerFactory.newModifier("withNetwork") { it.withNetwork(network) },
            )
        }

        const val SSH_USER: String = "sshuser"
        const val SSH_PASSWORD: String = "secret"
    }
}
