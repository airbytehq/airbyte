/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import java.util.*
import org.testcontainers.containers.GenericContainer

object HostPortResolver {
    @JvmStatic
    fun resolveHost(container: GenericContainer<*>?): String? {
        return getIpAddress(container)
    }

    @JvmStatic
    fun resolvePort(container: GenericContainer<*>?): Int {
        return container!!.exposedPorts.stream().findFirst().get()
    }

    fun resolveIpAddress(container: GenericContainer<*>?): String? {
        return getIpAddress(container)
    }

    private fun getIpAddress(container: GenericContainer<*>?): String? {
        return Objects.requireNonNull(
            container!!
                .containerInfo
                .networkSettings
                .networks
                .entries
                .stream()
                .findFirst()
                .get()
                .value
                .ipAddress
        )
    }
}
