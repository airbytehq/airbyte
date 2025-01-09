/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableCleaner
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableWriterFactory
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.Table

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class IcebergStreamLoader(
    override val stream: DestinationStream,
    private val table: Table,
    private val icebergTableWriterFactory: IcebergTableWriterFactory,
    private val icebergUtil: IcebergUtil,
    private val pipeline: MapperPipeline,
    private val stagingBranchName: String,
    private val mainBranchName: String
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        icebergTableWriterFactory
            .create(
                table = table,
                generationId = icebergUtil.constructGenerationIdSuffix(stream),
                importType = stream.importType
            )
            .use { writer ->
                log.info { "Writing records to branch $stagingBranchName" }
                records.forEach { record ->
                    val icebergRecord =
                        icebergUtil.toRecord(
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
                        icebergUtil::constructGenerationIdSuffix
                    )
                val icebergTableCleaner = IcebergTableCleaner(icebergUtil = icebergUtil)
                icebergTableCleaner.deleteGenerationId(
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
