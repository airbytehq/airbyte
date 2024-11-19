/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.object_storage.ObjectStorageStreamLoader
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableWriterFactory
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicLong
import org.apache.iceberg.Table

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class IcebergStreamLoader(
    override val stream: DestinationStream,
    private val table: Table,
    private val icebergTableWriterFactory: IcebergTableWriterFactory,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
    private val pipeline: MapperPipeline,
    private val stagingBranchName: String,
    private val mainBranchName: String
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    private val partNumber = AtomicLong(0L)

    override suspend fun start() {
        val state = destinationStateManager.getState(stream)
        val maxPartNumber =
            state.generations
                .filter { it.generationId >= stream.minimumGenerationId }
                .mapNotNull { it.objects.maxOfOrNull { obj -> obj.partNumber } }
                .maxOrNull()
        log.info { "Got max part number from destination state: $maxPartNumber" }
        maxPartNumber?.let { partNumber.set(it + 1L) }
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        val partNumber = partNumber.getAndIncrement()
        val state = destinationStateManager.getState(stream)

        icebergTableWriterFactory.create(table = table).use { writer ->
            log.info { "Writing records to branch $stagingBranchName" }
            state.addObject(stream.generationId, stagingBranchName, partNumber)
            records.forEach { record ->
                val icebergRecord = IcebergUtil.toRecord(
                    record=record,
                    stream=stream,
                    tableSchema = table.schema(),
                    pipeline = pipeline,
                )
                writer.write(icebergRecord)
            }
            val writeResult = writer.complete()
            if(writeResult.deleteFiles().isNotEmpty()) {
                val delta = table.newRowDelta().toBranch(stagingBranchName)
                writeResult.dataFiles().forEach {  delta.addRows(it) }
                writeResult.deleteFiles().forEach { delta.addDeletes(it) }
            } else {
                val append = table.newAppend().toBranch(stagingBranchName)
                writeResult.dataFiles().forEach {  append.appendFile(it) }
            }
            log.info { "Finished writing records to $stagingBranchName" }
        }

        return ObjectStorageStreamLoader.StagedObject(
            remoteObject = stagingBranchName,
            partNumber = partNumber
        )
    }

    override suspend fun processFile(file: DestinationFile): Batch {
        throw NotImplementedError("Destination Iceberg does not support universal file transfer.")
    }

    override suspend fun processBatch(batch: Batch): Batch {
        val stagedObject = batch as ObjectStorageStreamLoader.StagedObject<*>
        log.info { "Moving staged object from $stagingBranchName to $mainBranchName" }
        table.manageSnapshots().fastForwardBranch(mainBranchName, stagingBranchName).commit()

        val state = destinationStateManager.getState(stream)
        state.removeObject(stream.generationId, stagingBranchName)
        state.addObject(stream.generationId, mainBranchName, stagedObject.partNumber)

        val finalizedObject =
            ObjectStorageStreamLoader.FinalizedObject(remoteObject = mainBranchName)
        return finalizedObject
    }
}
