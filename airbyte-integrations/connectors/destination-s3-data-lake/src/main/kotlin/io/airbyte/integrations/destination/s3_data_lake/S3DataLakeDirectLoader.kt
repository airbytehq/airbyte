/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

@Singleton
class S3DataLakeDirectLoaderFactory(
    private val config: S3DataLakeConfiguration,
    private val streamStateStore: StreamStateStore<S3DataLakeStreamLoader>,
    @Value("\${airbyte.destination.core.record-batch-size-override}")
    val recordBatchSizeOverride: Long? = null,
) : DirectLoaderFactory<S3DataLakeDirectLoader>() {
    private val log = KotlinLogging.logger {}

    override fun create(stream: DestinationStream.Descriptor, part: Int): S3DataLakeDirectLoader {
        log.info { "Creating direct loader for stream $stream" }

        val loader = streamStateStore.get(stream)!!

        return S3DataLakeDirectLoader(
            batchSize = recordBatchSizeOverride ?: config.recordBatchSizeBytes,
            stream = loader.stream,
            loader = loader,
            stagingBranchName = loader.stagingBranchName,
        )
    }
}

class S3DataLakeDirectLoader(
    private val batchSize: Long,
    private val stream: DestinationStream,
    private val loader: S3DataLakeStreamLoader,
    private val stagingBranchName: String,
) : DirectLoader {
    private val log = KotlinLogging.logger {}
    private var dataSize = 0L
    private val writer =
        loader.s3DataLakeTableWriterFactory.create(
            table = loader.table.get(),
            generationId = loader.s3DataLakeUtil.constructGenerationIdSuffix(stream),
            importType = stream.importType
        )

    override fun accept(record: DestinationRecordAirbyteValue): DirectLoader.DirectLoadResult {
        log.info { "Writing records to branch $stagingBranchName" }
        val icebergRecord =
            loader.s3DataLakeUtil.toRecord(
                record = record,
                stream = stream,
                tableSchema = loader.table.get().schema(),
                pipeline = loader.pipeline,
            )
        writer.write(icebergRecord)

        dataSize += record.serializedSizeBytes // TODO: use icebergRecord.size() instead?
        if (dataSize < batchSize) {
            return DirectLoader.Incomplete
        }

        return finish()
    }

    override fun finish(): DirectLoader.Complete {
        val writeResult = writer.complete()
        if (writeResult.deleteFiles().isNotEmpty()) {
            val delta = loader.table.get().newRowDelta().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { delta.addRows(it) }
            writeResult.deleteFiles().forEach { delta.addDeletes(it) }
            delta.commit()
        } else {
            val append = loader.table.get().newAppend().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { append.appendFile(it) }
            append.commit()
        }
        log.info { "Finished writing records to $stagingBranchName" }

        return DirectLoader.Complete(persisted = true)
    }

    override fun close() {
        writer.close()
    }
}
