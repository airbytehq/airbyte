/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

const val DATA_CHANNEL_PROPERTY_PREFIX = "airbyte.connector.data-channel"
const val MEDIUM_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.medium"
const val FORMAT_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.format"
const val SOCKET_PATHS_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.socket-paths"
/**
 * A [SocketDataChannelResourceHolder] holds a list of [SocketDataChannel] instances that are
 * initialized and once connected can be bound to for data transfer.
 *
 * It is tasked with maintaining a list of and atomically assigning sockets upon resource request.
 */
@Singleton
@Requires(property = MEDIUM_PROPERTY, value = "SOCKET")
class SocketDataChannelResourceHolder(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}") socketPaths: List<String>,
    socketFactory: SocketDataChannelFactory,
) {

    val sockets: List<SocketDataChannel>
    init {
        sockets = List(socketPaths.size) { socketFactory.makeSocket(socketPaths[it]) }
        runBlocking { sockets.forEach { socket -> socket.initialize() } }
    }

    @Synchronized
    fun acquireSocketDataChannel(): SocketDataChannel? =
        sockets.firstOrNull { it.isAvailable }?.also { it.bind() }
}
