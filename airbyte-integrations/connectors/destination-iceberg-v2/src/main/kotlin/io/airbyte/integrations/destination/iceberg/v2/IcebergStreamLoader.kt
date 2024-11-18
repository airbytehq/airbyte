/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.iceberg_parquet.IcebergParquetWriter
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.object_storage.ObjectStorageStreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.UUID
import java.util.concurrent.atomic.AtomicLong
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Table
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.parquet.GenericParquetWriter
import org.apache.iceberg.parquet.Parquet

class IcebergStreamLoader(
    override val stream: DestinationStream,
    private val table: Table,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
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
        val metadata = ObjectStorageDestinationState.metadataFor(stream)
        val partNumber = partNumber.getAndIncrement()
        val state = destinationStateManager.getState(stream)

        val location =
            table.locationProvider().newDataLocation(UUID.randomUUID().toString() + ".parquet")
        val outputFile = table.io().newOutputFile(location)
        val builder =
            Parquet.writeData(outputFile)
                .schema(table.schema())
                .createWriterFunc(GenericParquetWriter::buildWriter)
                .overwrite()
                .withSpec(PartitionSpec.unpartitioned())
        metadata.forEach { (k, v) -> builder.meta(k, v) }
        val dataWriter = builder.build<GenericRecord>()

        val icebergParquetWriter =
            IcebergWriter(stream, true, IcebergParquetWriter(dataWriter), table.schema())

        log.info { "Writing records to branch $stagingBranchName" }
        state.addObject(stream.generationId, stagingBranchName, partNumber)
        records.forEach { icebergParquetWriter.accept(it) }
        log.info { "Finished writing records to $stagingBranchName" }
        icebergParquetWriter.close()

        table.newAppend().toBranch(stagingBranchName).appendFile(dataWriter.toDataFile()).commit()

        return ObjectStorageStreamLoader.StagedObject(
            remoteObject = stagingBranchName,
            partNumber = partNumber
        )
    }

    override suspend fun processBatch(batch: Batch): Batch {
        val stagedObject = batch as ObjectStorageStreamLoader.StagedObject<String>
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
