package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.SocketInputFlow
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.WriteOpOverride
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.fold

@Singleton
class S3V2DirectLoadOverride(
    @Named("socketInputFlows") private val socketInputFlows: Array<SocketInputFlow>,
    private val writerFactory: BufferedFormattingWriterFactory<*>,
    private val catalog: DestinationCatalog,
    private val s3Config: S3V2Configuration<*>,
    private val s3Client: S3Client,
): WriteOpOverride {
    override val terminalCondition: TerminalCondition = SelfTerminating

    data class State(
        var numFileBytes: Long = 0,
        var partIndex: Int = 1,
        var fileNumber: Long = 0,
        var multipartUpload: StreamingUpload<S3Object>? = null
    )

    override suspend fun execute(): Unit = coroutineScope {
        socketInputFlows.map { socketInputFlow ->
            async(Dispatchers.IO) {
                val writers =
                    catalog.streams.associate { it.descriptor to writerFactory.create(it) }
                socketInputFlow.fold(State()) { state, pipelineEvent ->
                    when (pipelineEvent) {
                        is PipelineMessage -> {
                            val writer = writers[pipelineEvent.key.stream]!!
                            writer.accept(pipelineEvent.value)
                            val nextFileSize = state.numFileBytes + writer.bufferSize
                            val (bytes, isFinal) = if (nextFileSize >= s3Config.objectSizeBytes) {
                                state.numFileBytes = 0
                                writer.flush()
                                Pair(writer.takeBytes(), true)
                            } else if (writer.bufferSize >= s3Config.partSizeBytes) {
                                writer.flush()
                                val bytes = writer.takeBytes()
                                state.numFileBytes += bytes?.size ?: 0
                                Pair(bytes, false)
                            } else {
                                Pair(null, false)
                            }

                            if (bytes != null) {
                                if (state.partIndex == 1) {
                                    state.multipartUpload =
                                        s3Client.startStreamingUpload("${state.fileNumber}.json")
                                }
                                state.multipartUpload?.uploadPart(bytes, state.partIndex)
                                state.partIndex++
                                if (isFinal) {
                                    state.multipartUpload?.complete()
                                    state.multipartUpload = null
                                    state.partIndex = 1
                                    state.fileNumber++
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
