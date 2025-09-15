/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.testcontainers

import java.net.InetSocketAddress
import org.testcontainers.containers.Container

const val DOCKER_HOST_FROM_WITHIN_CONTAINER = "host.testcontainers.internal"

/**
 * Returns the inner docker network address of a container. This can be used to reach a container
 * from another container running on the same network.
 */
fun Container<*>.innerAddress(): InetSocketAddress =
    InetSocketAddress.createUnresolved(
        containerInfo.networkSettings.networks.entries.first().value.ipAddress!!,
        exposedPorts.first(),
    )

/**
 * Returns the outer docker network address of a container. This can be used to reach a container
 * from the host machine
 */
fun Container<*>.outerAddress(): InetSocketAddress =
    InetSocketAddress.createUnresolved(host, firstMappedPort)
