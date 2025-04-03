/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels
import java.nio.channels.SocketChannel
import java.nio.file.Files
import java.nio.file.attribute.PosixFilePermissions
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector

class SocketInputFlow(
    private val catalog: DestinationCatalog,
    private val part: Int,
    private val completions: Array<CompletableDeferred<Unit>>,
    private val streamCompletionCounts:
        ConcurrentHashMap<DestinationStream.Descriptor, AtomicInteger>,
    private val syncManager: SyncManager
) : Flow<PipelineEvent<StreamKey, DestinationRecordRaw>> {
    private val log = KotlinLogging.logger {}

    override suspend fun collect(
        collector: FlowCollector<PipelineEvent<StreamKey, DestinationRecordRaw>>
    ) {
        // val socketName = "/Users/jschmidt/.sockets/ab_socket_$part"
        val socketName = "/var/run/sockets/ab_socket_$part"
        log.info { "About to read from socket file $socketName" }
        val socketFile = File(socketName)
        while (!socketFile.exists()) {
            log.info { "Waiting for socket file $socketName to be created" }
            delay(1000L)
        }
        Files.setPosixFilePermissions(
            socketFile.toPath(),
            PosixFilePermissions.fromString("rwxrwxrwx")
        )
        val address = UnixDomainSocketAddress.of(socketFile.toPath())
        val socketChannel = SocketChannel.open(StandardProtocolFamily.UNIX)
        log.info { "Socket opened" }
        if (!socketChannel.connect(address)) {
            throw IllegalStateException("Failed to connect to socket")
        }
        log.info { "Connected" }
        socketChannel.use { channel ->
            Channels.newInputStream(channel).bufferedReader(Charsets.UTF_8).use { reader ->
                val factory = DestinationMessageFactory(catalog, false)
                val streamRecordCounts =
                    catalog.streams.associate { it.descriptor to 0L }.toMutableMap()
                reader.lineSequence().forEach { line ->
                    val airbyteMessage = line.deserializeToClass(AirbyteMessage::class.java)
                    when (val dMessage = factory.fromAirbyteMessage(airbyteMessage, line)) {
                        is DestinationRecord -> {
                            streamRecordCounts.merge(dMessage.stream.descriptor, 1) { old, _ ->
                                old + 1
                            }
                            collector.emit(
                                PipelineMessage(
                                    mapOf(CheckpointId(0) to 1),
                                    StreamKey(dMessage.stream.descriptor),
                                    dMessage.asDestinationRecordRaw()
                                )
                            )
                        }
                        is DestinationRecordStreamComplete -> {
                            log.info {
                                "Stream complete message received for ${dMessage.stream.descriptor}"
                            }
                            val myCounts = streamRecordCounts[dMessage.stream.descriptor] ?: 0L
                            syncManager
                                .getStreamManager(dMessage.stream.descriptor)
                                .incrementReadCount(myCounts)
                            // Everybody sends end-of-stream, but only the last guy completes.
                            if (
                                streamCompletionCounts[dMessage.stream.descriptor]
                                    ?.decrementAndGet() == 0
                            ) {
                                log.info { "Closing stream ${dMessage.stream.descriptor}" }
                                syncManager
                                    .getStreamManager(dMessage.stream.descriptor)
                                    .markEndOfStream(true)
                            }
                            collector.emit(PipelineEndOfStream(dMessage.stream.descriptor))
                        }
                        is GlobalCheckpoint,
                        is StreamCheckpoint -> {
                            log.warn { "Ignoring state message " }
                        }
                        else ->
                            throw IllegalStateException(
                                "Unsupported message type ${airbyteMessage.type}"
                            )
                    }
                }

                completions[part].complete(Unit)

                // If I'm master, finish up
                if (part == 0) {
                    completions.forEach { completion -> completion.await() }
                    syncManager.markInputConsumed()
                    syncManager.markCheckpointsProcessed()
                }
            }
        }
    }
}
