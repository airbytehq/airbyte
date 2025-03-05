package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.SocketTestConfig
import io.airbyte.cdk.load.file.SocketInputFlow
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.WriteOpOverride
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.fold
import kotlinx.coroutines.launch

abstract class ObjectStorageDirectLoadOverride(
    @Named("socketInputFlows") private val socketInputFlows: Array<SocketInputFlow>,
    private val writerFactory: BufferedFormattingWriterFactory<*>,
    private val catalog: DestinationCatalog,
    private val config: SocketTestConfig,
    private val client: ObjectStorageClient<*>,
    private val pathFactory: ObjectStoragePathFactory
): WriteOpOverride {
    val log = KotlinLogging.logger { }
    override val terminalCondition: TerminalCondition = SelfTerminating

    data class State(
        var numFileBytes: Long = 0,
        var partIndex: Int = 0,
        var fileNumber: Long = 0,
        var multipartUpload: StreamingUpload<*>? = null,
        val completes: Channel<Unit> = Channel(Channel.UNLIMITED),
        var completed: CompletableDeferred<String> = CompletableDeferred(),
    )

    companion object {
        private val PART_SIZE_BYTES = 20L * 1024 * 1024
        private val FILE_SIZE_BYTES = 200L * 1024 * 1024
    }

    override suspend fun execute(): Unit = coroutineScope {
        log.info { "Starting override with client $client" }
        socketInputFlows.mapIndexed { socketNum, socketInputFlow ->
            log.info { "Starting to read from socket $socketNum" }
            async(Dispatchers.IO) {
                val writers =
                    catalog.streams.associate { it.descriptor to writerFactory.create(it) }
                socketInputFlow.fold(State(fileNumber = socketNum.toLong())) { state, pipelineEvent ->
                    when (pipelineEvent) {
                        is PipelineMessage -> {
                            val writer = writers[pipelineEvent.key.stream]!!
                            writer.accept(pipelineEvent.value)
                            val nextFileSize = state.numFileBytes + writer.bufferSize
                            val (bytes, isFinal) = if (nextFileSize >= FILE_SIZE_BYTES) {
                                state.numFileBytes = 0
                                writer.flush()
                                Pair(writer.takeBytes(), true)
                            } else if (writer.bufferSize >= PART_SIZE_BYTES) {
                                writer.flush()
                                val bytes = writer.takeBytes()
                                state.numFileBytes += bytes?.size ?: 0
                                Pair(bytes, false)
                            } else {
                                Pair(null, false)
                            }

                            if (bytes != null) {
                                if (state.partIndex == 1) {
                                    val stream = catalog.getStream(pipelineEvent.key.stream)
                                    val fileName = pathFactory.getPathToFile(stream, state.fileNumber)
                                    log.info { "Starting multipart upload for file $fileName" }
                                    state.multipartUpload =
                                        client.startStreamingUpload(fileName)
                                }
                                state.partIndex++
                                val partIndex = state.partIndex
                                launch {
                                    state.multipartUpload?.uploadPart(bytes, state.partIndex)
                                    state.completes.send(Unit)
                                    if (isFinal) {
                                        repeat(partIndex) {
                                            state.completes.receive()
                                        }
                                        val key = state.multipartUpload!!.complete().key
                                        state.completed.complete(key)
                                    }
                                }
                                if (isFinal) {
                                    val key = state.completed.await()
                                    log.info { "Completed multipart upload for file $key" }
                                    state.completed = CompletableDeferred()
                                    state.multipartUpload = null
                                    state.partIndex = 0
                                    state.fileNumber += config.numSockets
                                }
                            }

                            state
                        }

                        else -> {
                            state
                        }
                    }
                }
            }
        }.awaitAll()
    }
}
