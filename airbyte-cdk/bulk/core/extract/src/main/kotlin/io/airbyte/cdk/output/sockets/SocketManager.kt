package io.airbyte.cdk.output.sockets

import io.airbyte.cdk.command.Configuration
import io.airbyte.cdk.command.SourceConfiguration
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

const val DATA_CHANNEL_PROPERTY_PREFIX = "airbyte.connector.data-channel"
const val MEDIUM_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.medium"
const val FORMAT_PROPERTY = "$DATA_CHANNEL_PROPERTY_PREFIX.format"
//const val SOCKET_PATHS_PROPERTY = "${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths"

@Singleton
@Requires(property = MEDIUM_PROPERTY, value = "SOCKET")
class SocketManager(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}") socketPaths: List<String>,
    socketFactory: SocketWrapperFactory,) {

    val sockets: List<SocketWrapper>
    init {
        sockets = List(socketPaths.size) {
            socketFactory.makeSocket(socketPaths[it])
        }
        runBlocking {
            sockets.forEach { socket -> socket.initializeSocket() }
        }
    }


     fun bindFreeSocket(): SocketWrapper? {
        synchronized(sockets) {
            val maybeSocket: SocketWrapper? =
                sockets.firstOrNull {
                    it.status == SocketWrapper.SocketStatus.SOCKET_READY && it.bound.not() }
                    ?.also { it.bindSocket() }
            return maybeSocket
        }
    }

    /*companion object {
        @Creator
        fun getInstance(socketFactory: SocketWrapperFactory) : SocketManager {
            return SocketManager(List(10) { "/tmp/tmp-socket-$it" }, socketFactory )
        }
    }*/
}



const val EXTRACT_PROPERTY_PREFIX = "airbyte.connector.extract"
const val SPEED_MODE_PROPERTY = "${EXTRACT_PROPERTY_PREFIX}.speed-mode"
