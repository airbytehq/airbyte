package io.airbyte.cdk.output.sockets

import io.micronaut.context.annotation.Requires
import io.micronaut.core.annotation.Creator
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

@Singleton
@Requires(property = SPEED_MODE_PROPERTY, value = "boosted")
class SocketManager(private val socketPaths: List<String>, socketFactory: SocketWrapperFactory) {
    val sockets: List<SocketWrapper>
    init {
        sockets = List(socketPaths.size) {
            socketFactory.makeSocket(socketPaths[it])
        }
        runBlocking {
            sockets.forEach { socket -> socket.initializeSocket() }
        }
    }


    fun getFree(): SocketWrapper? {
        synchronized(sockets) {
            val maybeSocket: SocketWrapper? = sockets.filter { it.status == SocketWrapper.SocketStatus.SOCKET_READY && it.bound.not() }.firstOrNull()
            maybeSocket?.bound = true
            return maybeSocket
        }
    }

    /*companion object {
        @Creator // TEMP
        fun getInstance(socketFactory: SocketWrapperFactory) : SocketManager {
            return SocketManager(List(10) { "/tmp/tmp-socket-$it" }, socketFactory )
        }
    }*/
}



const val EXTRACT_PROPERTY_PREFIX = "airbyte.connector.extract"
const val SPEED_MODE_PROPERTY = "${EXTRACT_PROPERTY_PREFIX}.speed-mode"
