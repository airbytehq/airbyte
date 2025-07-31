/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import io.airbyte.cdk.output.sockets.SocketDataChannel.SocketStatus.*
import io.airbyte.cdk.util.ThreadRenamingCoroutineName
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import java.io.ByteArrayOutputStream
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

interface SocketDataChannel {
    enum class SocketStatus {
        SOCKET_INITIALIZED,
        SOCKET_WAITING_LISTENER,
        SOCKET_READY,
        SOCKET_CLOSED,
        SOCKET_ERROR,
    }

    suspend fun initialize()
    fun shutdown()
    val status: SocketStatus
    var isBound: Boolean
    fun bind()
    fun unbind()
    var outputStream: OutputStream?
    val isAvailable: Boolean
}

/**
 * A Unix Domain Socket implementation of [SocketDataChannel].
 *
 * @param socketFilePath The path to the Unix domain socket file.
 * @param probePacket A packet used to probe the socket state. The type of the packet is determined
 * by the configured format (JSONL or Protobuf).
 */
class UnixDomainSocketDataChannel(
    private val socketFilePath: String,
    private val probePacket: ProbePacket
) : SocketDataChannel {

    private var socketStatus = AtomicReference(SOCKET_CLOSED)
    private var socketBound = AtomicBoolean(false)

    override var outputStream: OutputStream? = null
    override val status: SocketDataChannel.SocketStatus
        @Synchronized
        get() {
            if (socketStatus.get() == SOCKET_READY && socketBound.get().not()) ensureSocketState()
            return socketStatus.get()
        }
    override val isAvailable: Boolean
        @Synchronized
        get() {
            return socketStatus.get() == SOCKET_READY && socketBound.get().not()
        }

    /**
     * Ensure the socket is still open and writable. We send a probe packet to check the state of
     * the socket.
     */
    private fun ensureSocketState() {
        try {
            outputStream?.write(probePacket)
        } catch (e: Exception) {
            logger.debug(e) { "Failed writing to socket $socketFilePath. Marking SOCKET_ERROR" }
            shutdown()
            socketStatus.set(SOCKET_ERROR)
        }
    }

    @set:Synchronized
    override var isBound: Boolean
        get() = socketBound.get()
        set(value) = socketBound.set(value)

    override suspend fun initialize() = coroutineScope {
        logger.info { "Initializing socket at $socketFilePath" }
        val socketFile = File(socketFilePath)
        if (socketFile.exists()) {
            socketFile.delete()
        }
        val socketAddress: UnixDomainSocketAddress? =
            UnixDomainSocketAddress.of(socketFile.toPath())

        val serverSocketChannel: ServerSocketChannel =
            ServerSocketChannel.open(StandardProtocolFamily.UNIX)
        serverSocketChannel.bind(socketAddress)
        socketStatus.set(SOCKET_INITIALIZED)
        // Socket is initialized and waiting for a listener to connect.
        // In order to let the outer RunBlocking {} to exit immediately,
        // we launch a coroutine as an independent Job() on the IO dispatcher.
        launch(
            ThreadRenamingCoroutineName("socket-data-channel-$socketFilePath--") +
                Dispatchers.IO +
                Job()
        ) {
            socketStatus.set(SOCKET_WAITING_LISTENER)
            logger.info { "Waiting to connect..." }
            // accept blocks until a listener connects
            val socketChannel: SocketChannel = serverSocketChannel.accept()
            // close the server socket channel after accepting a connection
            serverSocketChannel.close()
            socketStatus.set(SOCKET_READY)
            outputStream = Channels.newOutputStream(socketChannel)
            logger.info { "Connected to server socket" }
        }
        Unit
    }

    override fun shutdown() {
        socketStatus.set(SOCKET_CLOSED)
        outputStream?.close()
        outputStream = null
        unbind()
    }

    override fun bind() {
        socketBound.set(true)
    }

    override fun unbind() {
        socketBound.set(false)
    }
}

interface SocketDataChannelFactory {
    fun makeSocket(socketFilePath: String): SocketDataChannel
}

@Singleton
class DefaultSocketDataChannelFactory(private val probePacket: ProbePacket) :
    SocketDataChannelFactory {
    override fun makeSocket(socketFilePath: String): SocketDataChannel =
        UnixDomainSocketDataChannel(socketFilePath, probePacket)
}

private typealias ProbePacket = ByteArray

/**
 * Factory to create a probe packet based on the configured format. JSON format is a single newline
 * character, while Protobuf format is a serialized AirbyteProbeMessageProtobuf. Sending an
 * unexpected packet type will result in an error on the receiving end.
 */
@Factory
private class ProbePacketFactory() {
    @Singleton
    @Requires(property = FORMAT_PROPERTY, value = "JSONL")
    fun simpleProbePacket(): ProbePacket = byteArrayOf('\n'.code.toByte())

    @Singleton
    @Requires(property = FORMAT_PROPERTY, value = "PROTOBUF")
    fun protoProbePacket(): ProbePacket {
        val baos = ByteArrayOutputStream()
        protoProbePacket.writeDelimitedTo(baos)
        return baos.toByteArray()
    }

    companion object {
        val protoProbePacket: AirbyteMessage.AirbyteMessageProtobuf =
            AirbyteMessage.AirbyteMessageProtobuf.newBuilder()
                .setProbe(AirbyteMessage.AirbyteProbeMessageProtobuf.newBuilder().build())
                .build()
    }
}
