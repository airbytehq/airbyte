/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.MapperFeature.*
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.smile.databind.SmileMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationMessage
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
import io.airbyte.protocol.Protocol

class SocketInputFlow(
    private val config: DestinationConfiguration,
    private val catalog: DestinationCatalog,
    private val part: Int,
    private val completions: Array<CompletableDeferred<Unit>>,
    private val streamCompletionCounts:
        ConcurrentHashMap<DestinationStream.Descriptor, AtomicInteger>,
    private val syncManager: SyncManager
) : Flow<PipelineEvent<StreamKey, DestinationRecordRaw>> {
    private val log = KotlinLogging.logger {}
    private val factory = DestinationMessageFactory(catalog, false)

    private fun initMapper(): ObjectMapper = configure(ObjectMapper())

    private fun initSmileMapper(): ObjectMapper = configure(SmileMapper())

    private val mapper =
        if (config.inputSerializationFormat == DestinationConfiguration.InputSerializationFormat.SMILE) {
            initSmileMapper()
        } else {
            initMapper()
        }

    private fun configure(objectMapper: ObjectMapper): ObjectMapper {
        objectMapper
            .enable(ACCEPT_CASE_INSENSITIVE_ENUMS)
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
            .configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
            .registerModule(JavaTimeModule())
            .registerModule(AfterburnerModule())
        return objectMapper
    }

    override suspend fun collect(
        collector: FlowCollector<PipelineEvent<StreamKey, DestinationRecordRaw>>
    ) {
        val socketName = "${config.socketPrefix}$part"
        log.info { "About to read from socket file $socketName" }

        readSocket(socketName, collector, config.socketWaitTimeoutSeconds)

        completions[part].complete(Unit)

        // If I'm master, finish up
        if (part == 0) {
            completions.forEach { completion -> completion.await() }
            syncManager.markInputConsumed()
            syncManager.markCheckpointsProcessed()
        }
    }

    private suspend fun readSocket(
        socketName: String,
        collector: FlowCollector<PipelineEvent<StreamKey, DestinationRecordRaw>>,
        timeoutSeconds: Int
    ) {
        val socketFile = File(socketName)
        var timeoutRemaining = timeoutSeconds
        while (!socketFile.exists()) {
            log.info { "Waiting for socket file $socketName to be created" }
            delay(1000L)
            timeoutRemaining -= 1
            if (timeoutRemaining <= 0) {
                log.error { "Socket file $socketName not created in time" }
                return
            }
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
        val parser = Protocol.AirbyteMessage.parser()
        socketChannel.use { channel ->
            Channels.newInputStream(channel).buffered().use { bufferedInputStream ->
                val streamRecordCounts =
                    catalog.streams.associate { it.descriptor to 0L }.toMutableMap()
                when (config.inputSerializationFormat) {
                    DestinationConfiguration.InputSerializationFormat.JSONL,
                    DestinationConfiguration.InputSerializationFormat.SMILE ->
                        mapper
                            .readerFor(AirbyteMessage::class.java)
                            .readValues<AirbyteMessage>(bufferedInputStream)
                            .forEach {
                                val destinationMessage = factory.fromAirbyteMessage(it, "")
                                handleDestinationMessage(destinationMessage, streamRecordCounts, collector)
                            }
                    DestinationConfiguration.InputSerializationFormat.PROTOBUF -> {
                        while (true) {
                            val protoMessage =
                                parser.parseDelimitedFrom(bufferedInputStream) ?: break
                            val destinationMessage = factory.fromProtobufAirbyteMessage(protoMessage, initMapper())
                            handleDestinationMessage(destinationMessage, streamRecordCounts, collector)
                        }
                    }
                }
            }
        }
    }

    private suspend fun handleDestinationMessage(
        destinationMessage: DestinationMessage,
        streamRecordCounts: MutableMap<DestinationStream.Descriptor, Long>,
        collector: FlowCollector<PipelineEvent<StreamKey, DestinationRecordRaw>>
    ) {
        when (destinationMessage) {
            is DestinationRecord -> {
                streamRecordCounts.merge(destinationMessage.stream.descriptor, 1) { old, _ ->
                    old + 1
                }
                collector.emit(
                    PipelineMessage(
                        mapOf(CheckpointId(0) to 1),
                        StreamKey(destinationMessage.stream.descriptor),
                        destinationMessage.asDestinationRecordRaw()
                    )
                )
            }

            is DestinationRecordStreamComplete -> {
                log.info {
                    "Stream complete message received for ${destinationMessage.stream.descriptor}"
                }
                val myCounts = streamRecordCounts[destinationMessage.stream.descriptor] ?: 0L
                syncManager
                    .getStreamManager(destinationMessage.stream.descriptor)
                    .incrementReadCount(myCounts)
                // Everybody sends end-of-stream, but only the last guy completes.
                if (
                    streamCompletionCounts[destinationMessage.stream.descriptor]
                        ?.decrementAndGet() == 0
                ) {
                    log.info { "Closing stream ${destinationMessage.stream.descriptor}" }
                    syncManager
                        .getStreamManager(destinationMessage.stream.descriptor)
                        .markEndOfStream(true)
                }
                collector.emit(PipelineEndOfStream(destinationMessage.stream.descriptor))
            }

            is GlobalCheckpoint,
            is StreamCheckpoint -> {
                log.warn { "Ignoring state message " }
            }

            else ->
                throw IllegalStateException(
                    "Unsupported message type ${destinationMessage::class.java}"
                )
        }
    }
}
