package io.airbyte.cdk.output

import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.File
import java.io.PrintStream
import java.lang.module.Configuration
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.time.Clock

private const val SOCKET_NAME_TEMPLATE = "ab_socket_%d"
private const val SOCKET_FULL_PATH = "/var/run/sockets/$SOCKET_NAME_TEMPLATE"
//private const val SOCKET_FULL_PATH = "/tmp/$SOCKET_NAME_TEMPLATE"
private val logger = KotlinLogging.logger {}
@Singleton
class UnixDomainSocketOutputConsumer(
    clock: Clock,
    stdout: PrintStream,
    @Value("\${$CONNECTOR_OUTPUT_PREFIX.buffer-byte-size-threshold-for-flush}")
    bufferByteSizeThresholdForFlush: Int,
) : StdoutOutputConsumer(stdout, clock, bufferByteSizeThresholdForFlush) {
    private var socketNum: Int = -1
    var sc: SocketChannel? = null
    lateinit var ll: List<UnixDomainSocketOutputConsumer>

    fun setSocketNum(num: Int) {
        socketNum = num
    }

    override fun withLockFlushRecord() {
        synchronized(this) {
            sc ?: let {
                val socketPath = String.format(SOCKET_FULL_PATH, socketNum)
                logger.info { "Using socket..." }
                val socketFile = File(socketPath)
                logger.info { "Socket File path $socketPath" }
                if (socketFile.exists()) {
                    socketFile.delete()
                }
                val address = UnixDomainSocketAddress.of(socketFile.toPath())
                val serverSocketChannel: ServerSocketChannel =
                    ServerSocketChannel.open(StandardProtocolFamily.UNIX)
                serverSocketChannel.bind(address)
                logger.info { "Source : Server socket bound at ${socketFile.absolutePath}" }
                sc = serverSocketChannel.accept()
            }
        }
        if (buffer.size() > 0) {
            val array: ByteArray = buffer.toByteArray() + "\n".toByteArray(Charsets.UTF_8)
            sc?.write(ByteBuffer.wrap(array).order(ByteOrder.LITTLE_ENDIAN))
            buffer.reset()
        }
    }

    override fun close() {
        super.close()
        sc?.close()
    }

    override fun getS(num: Int): List<OutputConsumer>? {
        synchronized(this) {
            if (!::ll.isInitialized) {
                ll = List(num) { index ->
                    val udsoc = UnixDomainSocketOutputConsumer(clock, stdout, bufferByteSizeThresholdForFlush)
                    udsoc.setSocketNum(index)
                    udsoc
                }
            }
        }
        return ll
    }
}
