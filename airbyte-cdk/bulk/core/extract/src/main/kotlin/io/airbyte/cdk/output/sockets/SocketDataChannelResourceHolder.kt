/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import io.airbyte.cdk.TransientErrorException
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

const val DATA_CHANNEL_PROPERTY_PREFIX = "airbyte.connector.data-channel"
const val MEDIUM_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.medium"
const val FORMAT_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.format"
const val SOCKET_PATHS_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.socket-paths"


private val log = KotlinLogging.logger {}

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

    val onSocketStatusChange: (() -> Unit) = {
        log.info { "*** Socket status changed" }
        if (sockets.filter { it.status != SocketDataChannel.SocketStatus.SOCKET_ERROR }.isEmpty()) {
            log.info { "*** All sockets are in error state. Shutting down" }
            throw IllegalStateException("All sockets are in error state")
        }
    }

    val sockets: List<SocketDataChannel>
    init {
        sockets = List(socketPaths.size) { socketFactory.makeSocket(socketPaths[it], onSocketStatusChange) /*{
            log.info { "*** Socket status changed to $it" }
            if (sockets.filter { it.status != SocketDataChannel.SocketStatus.SOCKET_ERROR }.size == 0) {
                log.info { "*** All sockets are in error state. Shutting down" }
                throw IllegalStateException("All sockets are in error state")
            }
        }*/ }
        runBlocking { sockets.forEach { socket -> socket.initialize() } }
    }

    @Synchronized
    fun acquireSocketDataChannel(): SocketDataChannel? {
        onSocketStatusChange()
        return sockets.firstOrNull { it.isAvailable }?.also { it.bind() }
    }
}
