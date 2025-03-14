/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.iceberg.parquet.IcebergParquetPipelineFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter

@Singleton
class S3DataLakeDirectLoaderFactory(
    private val catalog: DestinationCatalog,
    private val config: S3DataLakeConfiguration,
    private val streamStateStore: StreamStateStore<S3DataLakeStreamState>,
    private val icebergTableWriterFactory: IcebergTableWriterFactory,
    private val icebergUtil: IcebergUtil,
) : DirectLoaderFactory<S3DataLakeDirectLoader> {
    private val log = KotlinLogging.logger {}

    override val inputPartitions: Int = config.numProcessRecordsWorkers

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): S3DataLakeDirectLoader {
        log.info { "Creating direct loader for stream $streamDescriptor" }

        val state = streamStateStore.get(streamDescriptor)!!
        val stream = catalog.getStream(streamDescriptor)
        val writer =
            icebergTableWriterFactory.create(
                table = state.table,
                generationId = icebergUtil.constructGenerationIdSuffix(stream),
                importType = stream.importType,
                schema = state.schema
            )

        return S3DataLakeDirectLoader(
            batchSize = config.recordBatchSizeBytes,
            stream = stream,
            table = state.table,
            schema = state.schema,
            stagingBranchName = DEFAULT_STAGING_BRANCH,
            writer = writer,
            icebergUtil = icebergUtil,
            pipeline = IcebergParquetPipelineFactory().create(stream)
        )
    }
}

class S3DataLakeDirectLoader(
    private val stream: DestinationStream,
    private val table: Table,
    private val schema: Schema,
    private val stagingBranchName: String,
    private val batchSize: Long,
    private val writer: BaseTaskWriter<Record>,
    private val icebergUtil: IcebergUtil,
    private val pipeline: MapperPipeline
) : DirectLoader {
    private val log = KotlinLogging.logger {}
    private var dataSize = 0L

    companion object {
        val commitLock: Any = Any()
    }

    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val recordAirbyteValue = record.asDestinationRecordAirbyteValue()

        val icebergRecord =
            icebergUtil.toRecord(
                record = recordAirbyteValue,
                stream = stream,
                tableSchema = schema,
                pipeline = pipeline
            )
        writer.write(icebergRecord)

        dataSize +=
            recordAirbyteValue.serializedSizeBytes // TODO: use icebergRecord.size() instead?
        if (dataSize < batchSize) {
            return DirectLoader.Incomplete
        }

        finish()

        return DirectLoader.Complete
    }

    override fun finish() {
        log.info { "Finishing writing to $stagingBranchName" }
        val writeResult = writer.complete()
        if (writeResult.deleteFiles().isNotEmpty()) {
            val delta = table.newRowDelta().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { delta.addRows(it) }
            writeResult.deleteFiles().forEach { delta.addDeletes(it) }
            synchronized(commitLock) { delta.commit() }
        } else {
            val append = table.newAppend().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { append.appendFile(it) }
            synchronized(commitLock) { append.commit() }
        }
        log.info { "Finished writing records to $stagingBranchName" }
    }

    override fun close() {
        log.info { "Closing writer for $stagingBranchName" }
        writer.close()
    }
}
