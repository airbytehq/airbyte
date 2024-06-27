/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import java.util.*
import org.testcontainers.containers.GenericContainer

object HostPortResolver {
    @JvmStatic
    fun resolveHost(container: GenericContainer<*>): String {
        return getIpAddress(container)
    }

    @JvmStatic
    fun resolvePort(container: GenericContainer<*>): Int {
        return container.exposedPorts.first()
    }

    fun resolveIpAddress(container: GenericContainer<*>): String {
        return getIpAddress(container)
    }

    private fun getIpAddress(container: GenericContainer<*>): String {
        // Weird double bang here. If I remove the Object.requireNotNull, there's a type error...
        return Objects.requireNonNull(
            container.containerInfo.networkSettings.networks.entries.first().value.ipAddress
        )!!
    }
}
