package io.airbyte.cdk.output.sockets

import io.airbyte.cdk.command.Configuration
import io.airbyte.cdk.command.SourceConfiguration
import io.micronaut.context.annotation.Requires
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

@Singleton
@Requires(bean = SourceConfiguration::class, beanProperty = "boostedMode", value = "true")
class SocketManager(private val socketPaths: List<String>, socketFactory: SocketWrapperFactory) {
    @Inject constructor(socketFactory: SocketWrapperFactory, config: SourceConfiguration) :
        this(List(config.numSockets) { config.socketFilePathBase.replace("#", "$it") }, socketFactory) // TEMP: read paths from env var

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
