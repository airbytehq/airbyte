/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriter
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.OutputStream

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartFormatter<T : OutputStream>(
    private val pathFactory: PathFactory,
    private val catalog: DestinationCatalog,
    private val writerFactory: BufferedFormattingWriterFactory<T>,
    private val client: ObjectStorageClient<*>,
    private val loader: ObjectLoader,
    // TODO: This doesn't need to be "DestinationState", just a couple of utility classes
    private val stateManager: DestinationStateManager<ObjectStorageDestinationState>,
    @Value("\${airbyte.destination.core.record-batch-size-override:null}")
    val batchSizeOverride: Long? = null,
) :
    BatchAccumulator<
        ObjectLoaderPartFormatter.State<T>,
        StreamKey,
        DestinationRecordRaw,
        ObjectLoaderPartFormatter.FormattedPart
    > {
    private val log = KotlinLogging.logger {}

    private val objectSizeBytes = loader.objectSizeBytes
    private val partSizeBytes = loader.partSizeBytes

    data class State<T : OutputStream>(
        val stream: DestinationStream,
        val writer: BufferedFormattingWriter<T>,
        val partFactory: PartFactory
    ) : AutoCloseable {
        override fun close() {
            writer.close()
        }
    }

    @JvmInline value class FormattedPart(val part: Part)

    private suspend fun newState(stream: DestinationStream): State<T> {
        // Determine unique file name.
        val pathOnly = pathFactory.getFinalDirectory(stream)
        val state = stateManager.getState(stream)
        val fileNo = state.getPartIdCounter(pathOnly).incrementAndGet()
        val fileName = state.ensureUnique(pathFactory.getPathToFile(stream, fileNo))

        // Initialize the part factory and writer.
        val partFactory = PartFactory(fileName, fileNo)
        log.info { "Starting part generation for $fileName (${stream.descriptor})" }
        return State(stream, writerFactory.create(stream), partFactory)
    }

    private fun makePart(state: State<T>, forceFinish: Boolean = false): FormattedPart {
        state.writer.flush()
        val newSize = state.partFactory.totalSize + state.writer.bufferSize
        val isFinal =
            forceFinish ||
                newSize >= objectSizeBytes ||
                batchSizeOverride != null // HACK: This is a hack to force a flush
        val bytes =
            if (isFinal) {
                state.writer.finish()
            } else {
                state.writer.takeBytes()
            }
        val part = state.partFactory.nextPart(bytes, isFinal)
        log.info { "Creating part $part" }
        return FormattedPart(part)
    }

    override suspend fun start(key: StreamKey, part: Int): State<T> {
        val stream = catalog.getStream(key.stream)
        return newState(stream)
    }

    override suspend fun accept(
        input: DestinationRecordRaw,
        state: State<T>
    ): BatchAccumulatorResult<State<T>, FormattedPart> {
        state.writer.accept(input.asDestinationRecordAirbyteValue())
        val dataSufficient = state.writer.bufferSize >= partSizeBytes || batchSizeOverride != null
        return if (dataSufficient) {
            val part = makePart(state)
            if (part.part.isFinal) {
                FinalOutput(part)
            } else {
                IntermediateOutput(state, part)
            }
        } else {
            NoOutput(state)
        }
    }

    override suspend fun finish(state: State<T>): FinalOutput<State<T>, FormattedPart> {
        return FinalOutput(makePart(state, true))
    }
}
