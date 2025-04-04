/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test

import java.io.BufferedOutputStream
import java.io.File
import java.io.OutputStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.util.concurrent.CompletableFuture.runAsync

class JavaSocketWriter {

    companion object {
        const val RECORD =
            """{"type":"RECORD","record":{"stream":"stream1","data":{"field1":"valuevaluevaluevaluevalue1","field3":"valuevaluevaluevaluevalue1","field2":"valuevaluevaluevaluevalue1","field5":"valuevaluevaluevaluevalue1","field4":"valuevaluevaluevaluevalue1"},"emitted_at":1742801071589}}"""

        val array: ByteArray = (RECORD + "\n").toByteArray(Charsets.UTF_8)

        const val RECORD2 =
            """{"type":"RECORD","record":{"stream":"xxxxxx2","data":{"field5":"bbbbbxxxxxccccctttttqqqqq5","field6":"bbbbbxxxxxccccctttttqqqqq5","field7":"bbbbbxxxxxccccctttttqqqqq5","field8":"bbbbbxxxxxccccctttttqqqqq5","field9":"bbbbbxxxxxccccctttttqqqqq5"},"emitted_at":2853911182690}}"""
        val array2: ByteArray = (RECORD2 + "\n").toByteArray(Charsets.UTF_8)
    }

    fun startJavaUnixSocketWriter() {
        val socketFile = File("/var/run/sockets/source.sock")
        if (socketFile.exists()) {
            socketFile.delete()
        }
        val address = UnixDomainSocketAddress.of(socketFile.toPath())

        // Open a server channel for Unix domain sockets
        val serverSocketChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)
        serverSocketChannel.bind(address)
        println("Source: Server socket bound at ${socketFile.absolutePath}")

        // Accept a client connection (blocking call)
        val socketChannel: SocketChannel = serverSocketChannel.accept()
        println("Source: Client connected")

        val outputStream: OutputStream = Channels.newOutputStream(socketChannel)
        val bufferedOutputStream = BufferedOutputStream(outputStream)

        val listOf =
            listOf(
                runAsync { writeFromOneThread(bufferedOutputStream) },
                runAsync { writeFromOneThread2(bufferedOutputStream) },
            )
        listOf.forEach { it.join() }

        println("Source: Finished writing to socket")
        outputStream.close()
        socketChannel.close()
        serverSocketChannel.close()
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

    private fun writeFromOneThread2(outputStream: OutputStream) {
        var records: Long = 0
        DummyIterator().use {
            it.forEachRemaining {
                outputStream.write(array2)
                records++
                if (records == 100_000L) {
                    outputStream.flush()
                    records = 0
                }
            }
        }
    }
}
