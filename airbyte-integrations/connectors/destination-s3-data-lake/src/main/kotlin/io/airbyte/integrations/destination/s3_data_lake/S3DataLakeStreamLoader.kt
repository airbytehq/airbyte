/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeTableCleaner
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeTableWriterFactory
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.Table

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3DataLakeStreamLoader(
    override val stream: DestinationStream,
    private val table: Table,
    private val s3DataLakeTableWriterFactory: S3DataLakeTableWriterFactory,
    private val s3DataLakeUtil: S3DataLakeUtil,
    private val pipeline: MapperPipeline,
    private var stagingBranchName: String,
    private val mainBranchName: String
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    init {
        stagingBranchName = mainBranchName
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        s3DataLakeTableWriterFactory
            .create(
                table = table,
                generationId = s3DataLakeUtil.constructGenerationIdSuffix(stream),
                importType = stream.importType
            )
            .use { writer ->
                log.info { "Writing records to branch $stagingBranchName" }
                records.forEach { record ->
                    val icebergRecord =
                        s3DataLakeUtil.toRecord(
                            record = record,
                            stream = stream,
                            tableSchema = table.schema(),
                            pipeline = pipeline,
                        )
                    writer.write(icebergRecord)
                }
                val writeResult = writer.complete()
                if (writeResult.deleteFiles().isNotEmpty()) {
                    val delta = table.newRowDelta().toBranch(stagingBranchName)
                    writeResult.dataFiles().forEach { delta.addRows(it) }
                    writeResult.deleteFiles().forEach { delta.addDeletes(it) }
                    delta.commit()
                } else {
                    val append = table.newAppend().toBranch(stagingBranchName)
                    writeResult.dataFiles().forEach { append.appendFile(it) }
                    append.commit()
                }
                log.info { "Finished writing records to $stagingBranchName" }
            }

        return SimpleBatch(Batch.State.COMPLETE)
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            // Doing it first to make sure that data coming in the current batch is written to the
            // main branch
            log.info {
                "No stream failure detected. Committing changes from staging branch '$stagingBranchName' to main branch '$mainBranchName."
            }
            table.manageSnapshots().fastForwardBranch(mainBranchName, stagingBranchName).commit()
            if (stream.minimumGenerationId > 0) {
                log.info {
                    "Detected a minimum generation ID (${stream.minimumGenerationId}). Preparing to delete obsolete generation IDs."
                }
                val generationIdsToDelete =
                    (0 until stream.minimumGenerationId).map(
                        s3DataLakeUtil::constructGenerationIdSuffix
                    )
                val s3DataLakeTableCleaner = S3DataLakeTableCleaner(s3DataLakeUtil = s3DataLakeUtil)
                s3DataLakeTableCleaner.deleteGenerationId(
                    table,
                    stagingBranchName,
                    generationIdsToDelete
                )
                //  Doing it again to push the deletes from the staging to main branch
                log.info {
                    "Deleted obsolete generation IDs up to ${stream.minimumGenerationId - 1}. " +
                        "Pushing these updates to the '$mainBranchName' branch."
                }
                table
                    .manageSnapshots()
                    .fastForwardBranch(mainBranchName, stagingBranchName)
                    .commit()
            }
        }
    }
}
