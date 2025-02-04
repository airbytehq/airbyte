/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg.parquet.IcebergParquetPipelineFactory
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeTableCleaner
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeTableWriterFactory
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference
import org.apache.iceberg.Table

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3DataLakeStreamLoader(
    private val icebergConfiguration: S3DataLakeConfiguration,
    override val stream: DestinationStream,
    private val s3DataLakeTableSynchronizer: S3DataLakeTableSynchronizer,
    val s3DataLakeTableWriterFactory: S3DataLakeTableWriterFactory,
    val s3DataLakeUtil: S3DataLakeUtil,
    val stagingBranchName: String,
    private val mainBranchName: String
) : StreamLoader {
    val table: AtomicReference<Table> = AtomicReference(null)
    val pipeline = IcebergParquetPipelineFactory().create(stream)

    @SuppressFBWarnings(
        "RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE",
        "something about the `table` lateinit var is confusing spotbugs"
    )
    override suspend fun start() {
        val properties = s3DataLakeUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog = s3DataLakeUtil.createCatalog(DEFAULT_CATALOG_NAME, properties)
        val incomingSchema = s3DataLakeUtil.toIcebergSchema(stream = stream, pipeline = pipeline)
        table.set(
            s3DataLakeUtil.createTable(
                streamDescriptor = stream.descriptor,
                catalog = catalog,
                schema = incomingSchema,
                properties = properties
            )
        )

        s3DataLakeTableSynchronizer.applySchemaChanges(table.get(), incomingSchema)

        try {
            logger.info {
                "maybe creating branch $DEFAULT_STAGING_BRANCH for stream ${stream.descriptor}"
            }
            table.get().manageSnapshots().createBranch(DEFAULT_STAGING_BRANCH).commit()
        } catch (e: IllegalArgumentException) {
            logger.info {
                "branch $DEFAULT_STAGING_BRANCH already exists for stream ${stream.descriptor}"
            }
        }
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        s3DataLakeTableWriterFactory
            .create(
                table = table.get(),
                generationId = s3DataLakeUtil.constructGenerationIdSuffix(stream),
                importType = stream.importType
            )
            .use { writer ->
                logger.info { "Writing records to branch $stagingBranchName" }
                records.forEach { record ->
                    val icebergRecord =
                        s3DataLakeUtil.toRecord(
                            record = record,
                            stream = stream,
                            tableSchema = table.get().schema(),
                            pipeline = pipeline,
                        )
                    writer.write(icebergRecord)
                }
                val writeResult = writer.complete()
                if (writeResult.deleteFiles().isNotEmpty()) {
                    val delta = table.get().newRowDelta().toBranch(stagingBranchName)
                    writeResult.dataFiles().forEach { delta.addRows(it) }
                    writeResult.deleteFiles().forEach { delta.addDeletes(it) }
                    delta.commit()
                } else {
                    val append = table.get().newAppend().toBranch(stagingBranchName)
                    writeResult.dataFiles().forEach { append.appendFile(it) }
                    append.commit()
                }
                logger.info { "Finished writing records to $stagingBranchName" }
            }

        return SimpleBatch(Batch.State.COMPLETE)
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            // Doing it first to make sure that data coming in the current batch is written to the
            // main branch
            logger.info {
                "No stream failure detected. Committing changes from staging branch '$stagingBranchName' to main branch '$mainBranchName."
            }
            table
                .get()
                .manageSnapshots()
                .fastForwardBranch(mainBranchName, stagingBranchName)
                .commit()
            if (stream.minimumGenerationId > 0) {
                logger.info {
                    "Detected a minimum generation ID (${stream.minimumGenerationId}). Preparing to delete obsolete generation IDs."
                }
                val generationIdsToDelete =
                    (0 until stream.minimumGenerationId).map(
                        s3DataLakeUtil::constructGenerationIdSuffix
                    )
                val s3DataLakeTableCleaner = S3DataLakeTableCleaner(s3DataLakeUtil = s3DataLakeUtil)
                s3DataLakeTableCleaner.deleteGenerationId(
                    table.get(),
                    stagingBranchName,
                    generationIdsToDelete
                )
                //  Doing it again to push the deletes from the staging to main branch
                logger.info {
                    "Deleted obsolete generation IDs up to ${stream.minimumGenerationId - 1}. " +
                        "Pushing these updates to the '$mainBranchName' branch."
                }
                table
                    .get()
                    .manageSnapshots()
                    .fastForwardBranch(mainBranchName, stagingBranchName)
                    .commit()
            }
        }
    }
}
