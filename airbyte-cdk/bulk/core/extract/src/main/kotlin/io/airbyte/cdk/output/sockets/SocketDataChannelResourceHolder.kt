package io.airbyte.cdk.output.sockets

import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

const val DATA_CHANNEL_PROPERTY_PREFIX = "airbyte.connector.data-channel"
const val MEDIUM_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.medium"
const val FORMAT_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.format"

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
    socketFactory: SocketDataChannelFactory,) {

    val sockets: List<SocketDataChannel>
    init {
        sockets = List(socketPaths.size) {
            socketFactory.makeSocket(socketPaths[it])
        }
        runBlocking {
            sockets.forEach { socket -> socket.initializeSocket() }
        }
    }

    @Synchronized
     fun bindFreeSocket(): SocketDataChannel? =
         sockets.firstOrNull { it.available }?.also { it.bindSocket() }
}



const val EXTRACT_PROPERTY_PREFIX = "airbyte.connector.extract"
const val SPEED_MODE_PROPERTY = "${EXTRACT_PROPERTY_PREFIX}.speed-mode"
