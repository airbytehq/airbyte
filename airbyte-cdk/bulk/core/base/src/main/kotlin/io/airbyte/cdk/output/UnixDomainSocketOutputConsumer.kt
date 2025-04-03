package io.airbyte.cdk.output

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.File
import java.io.PrintStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.time.Clock

private const val SOCKET_NAME_TEMPLATE = "ab_socket_%d"
private const val SOCKET_FULL_PATH = "/tmp/$SOCKET_NAME_TEMPLATE"

@Singleton
//@Secondary
class UnixDomainSocketOutputConsumer(
    clock: Clock,
    stdout: PrintStream,
    @Value("\${$CONNECTOR_OUTPUT_PREFIX.buffer-byte-size-threshold-for-flush:4096}")
    bufferByteSizeThresholdForFlush: Int,
) : StdoutOutputConsumer(stdout, clock, bufferByteSizeThresholdForFlush) {
    private val socketNum: Int = 1
    val socketPath = String.format(SOCKET_FULL_PATH, socketNum)
    val sc: SocketChannel

    init {
        val socketFile = File(socketPath)
        if (socketFile.exists()) {
            socketFile.delete()
        }
        val address = UnixDomainSocketAddress.of(socketFile.toPath())
        val serverSocketChannel: ServerSocketChannel =
            ServerSocketChannel.open(StandardProtocolFamily.UNIX)
        serverSocketChannel.bind(address)
        sc = serverSocketChannel.accept()
    }

    override fun withLockFlushRecord() {
        if (buffer.size() > 0) {
            val array: ByteArray = buffer.toByteArray() + "\n".toByteArray(Charsets.UTF_8)
            sc.write(ByteBuffer.wrap(array).order(ByteOrder.LITTLE_ENDIAN))
            buffer.reset()
        }
    }
}
