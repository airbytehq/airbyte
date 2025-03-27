package io.airbyte.integrations.source.e2e_test

import com.fasterxml.jackson.core.util.MinimalPrettyPrinter
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.io.BufferedOutputStream
import java.io.File
import java.io.OutputStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.util.concurrent.CompletableFuture.runAsync
import java.util.concurrent.Executors

class JavaImprovedSocketWriter {

    private val executor = Executors.newFixedThreadPool(8)

    companion object {
        const val RECORD =
            """{"type":"RECORD","record":{"stream":"stream1","data":{"field1":"valuevaluevaluevaluevalue1","field3":"valuevaluevaluevaluevalue1","field2":"valuevaluevaluevaluevalue1","field5":"valuevaluevaluevaluevalue1","field4":"valuevaluevaluevaluevalue1"},"emitted_at":1742801071589}}"""

        val array: ByteArray = (RECORD + "\n").toByteArray(Charsets.UTF_8)
    }


    fun startJavaUnixSocketWriter() {
        println("SOURCE SERIALISED 2")
        val listOf = listOf(
            runAsync(
                {
                    start("sock0")
                },
                executor,
            ),
            runAsync(
                {
                    start("sock1")
                },
                executor,
            ),
            runAsync(
                {
                    start("sock2")
                },
                executor,
            ),
            runAsync(
                {
                    start("sock3")
                },
                executor,
            ),
            runAsync(
                {
                    start("sock4")
                },
                executor,
            ),
            runAsync(
                {
                    start("sock5")
                },
                executor,
            ),
            runAsync(
                {
                    start("sock6")
                },
                executor,
            ),
            runAsync(
                {
                    start("sock7")
                },
                executor,
            ),
        )

        listOf.forEach { it.join() }
    }

    private fun start(sock: String) {
        val socketFile = File("/var/run/sockets/source.$sock")
        if (socketFile.exists()) {
            socketFile.delete()
        }
        val address = UnixDomainSocketAddress.of(socketFile.toPath())

        // Open a server channel for Unix domain sockets
        val serverSocketChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)
        serverSocketChannel.bind(address)
        println("Source $sock : Server socket bound at ${socketFile.absolutePath}")

        // Accept a client connection (blocking call)
        val socketChannel: SocketChannel = serverSocketChannel.accept()
        println("Source $sock : Client connected $sock")

        val outputStream: OutputStream = Channels.newOutputStream(socketChannel)
        val bufferedOutputStream = BufferedOutputStream(outputStream)
        writeSerialised(bufferedOutputStream)

        println("Source $sock : Finished writing to socket $sock")
        bufferedOutputStream.close()
        outputStream.close()
        socketChannel.close()
        serverSocketChannel.close()
    }

    private fun writeSerialised(outputStream: OutputStream) {
        var records: Long = 0
        DummyIterator().use { dummyIterator ->
            DummyIterator.OBJECT_MAPPER
                .writerFor(AirbyteMessage::class.java)
                .with(MinimalPrettyPrinter(System.lineSeparator()))
                .writeValues(outputStream).use { seq ->
                    dummyIterator.forEachRemaining { message ->
                        seq.write(message)
                        records++
                        if (records == 100_000L) {
                            outputStream.flush()
                            records = 0
                        }
                    }
                }
        }
    }

    private fun writeFromOneThread(outputStream: OutputStream) {
        var records: Long = 0
        DummyIterator().use {
            it.forEachRemaining {
                outputStream.write(array)
                records++
                if (records == 100_000L) {
                    outputStream.flush()
                    records = 0
                }
            }
        }
    }
}
