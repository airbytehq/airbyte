package io.airbyte.cdk.output.sockets

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.OutputStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference
import javax.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch


private val logger = KotlinLogging.logger {}

interface SocketWrapper {
    enum class SocketStatus {
        SOCKET_INITIALIZED,
        SOCKET_WAITING_LISTENER,
        SOCKET_READY,
        SOCKET_CLOSING,
        SOCKET_CLOSED,
        SOCKET_ERROR,
    }

    suspend fun initializeSocket()
    suspend fun shutdownSocket()
    val status: SocketStatus
    var bound: Boolean
    fun bindSocket()
    fun unbindSocket()
    var outputStream: OutputStream?
}

class UnixDomainSocketWrapper(private val socketFilePath: String): SocketWrapper {

    private var socketStatus = AtomicReference<SocketWrapper.SocketStatus>(SocketWrapper.SocketStatus.SOCKET_CLOSED)
    private var socketBound = AtomicBoolean(false)

    override var outputStream: OutputStream? = null
    override val status: SocketWrapper.SocketStatus
        get() = socketStatus.get()

    override var bound: Boolean
        get() = socketBound.get()
        set(value) = socketBound.set(value)

    override suspend fun initializeSocket() = coroutineScope {
        logger.info { "Initializing socket at $socketFilePath" }
        val socketFile = File(socketFilePath)
        if (socketFile.exists()) {
            socketFile.delete()
        }
        val socketAddress: UnixDomainSocketAddress? = UnixDomainSocketAddress.of(socketFile.toPath())

        val serverSocketChannel: ServerSocketChannel =
            ServerSocketChannel.open(StandardProtocolFamily.UNIX)
        serverSocketChannel.bind(socketAddress)
        socketStatus.set(SocketWrapper.SocketStatus.SOCKET_INITIALIZED)
        launch(Dispatchers.IO + Job()) {
            socketStatus.set(SocketWrapper.SocketStatus.SOCKET_WAITING_LISTENER)
            logger.info { "Waiting for $socketFilePath to connect..." }
            // accept blocks until a listener connects
            val socketChannel: SocketChannel = serverSocketChannel.accept()
            socketStatus.set(SocketWrapper.SocketStatus.SOCKET_READY)
            outputStream = Channels.newOutputStream(socketChannel)
            logger.info { "connected to server socket at $socketFilePath" }
        }
        Unit
    }

    override suspend fun shutdownSocket() {
        socketStatus.set(SocketWrapper.SocketStatus.SOCKET_CLOSING)
        outputStream?.close()
        socketStatus.set(SocketWrapper.SocketStatus.SOCKET_CLOSED)
        unbindSocket()
    }

    override fun bindSocket() {
        socketBound.set(true)
    }
    override fun unbindSocket() {
        socketBound.set(false)
    }
}

interface SocketWrapperFactory {
    fun makeSocket(socketFilePath: String): SocketWrapper
}

@Singleton
class DefaultSocketWrapperFactory: SocketWrapperFactory {
    override fun makeSocket(socketFilePath: String): SocketWrapper =
        UnixDomainSocketWrapper(socketFilePath)
}
