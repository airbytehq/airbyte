/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream
import org.apache.commons.io.FileUtils

/**
 * Async flushing logic. Flushing async prevents backpressure and is the superior flushing strategy.
 */
private val logger = KotlinLogging.logger {}

internal class AsyncFlush(
    private val streamDescToWriteConfig: Map<StreamDescriptor, WriteConfig>,
    private val stagingOperations: StagingOperations?,
    private val database: JdbcDatabase?,
    private val catalog: ConfiguredAirbyteCatalog?,
    // In general, this size is chosen to improve the performance of lower memory
    // connectors. With 1 Gi
    // of
    // resource the connector will usually at most fill up around 150 MB in a single queue. By
    // lowering
    // the batch size, the AsyncFlusher will flush in smaller batches which allows for memory to be
    // freed earlier similar to a sliding window effect
    override val optimalBatchSizeBytes: Long,
    private val destinationColumns: JavaBaseConstants.DestinationColumns
) : DestinationFlushFunction {

    @Throws(Exception::class)
    override fun flush(streamDescriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        val writer: CsvSerializedBuffer
        try {
            writer =
                CsvSerializedBuffer(
                    FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
                    StagingDatabaseCsvSheetGenerator(destinationColumns),
                    true
                )

            // reassign as lambdas require references to be final.
            stream.forEach { record: PartialAirbyteMessage ->
                try {
                    // todo (cgardens) - most writers just go ahead and re-serialize the contents of
                    // the record message.
                    // we should either just pass the raw string or at least have a way to do that
                    // and create a default
                    // impl that maintains backwards compatible behavior.
                    writer.accept(
                        record.serialized!!,
                        Jsons.serialize(record.record!!.meta),
                        // Destinations that want to use generations should switch to the new
                        // structure (e.g. StagingStreamOperations)
                        0,
                        record.record!!.emittedAt
                    )
                } catch (e: Exception) {
                    throw RuntimeException(e)
                }
            }
        } catch (e: Exception) {
            throw RuntimeException(e)
        }

        writer.flush()
        logger.info {
            "Flushing CSV buffer for stream ${streamDescriptor.name} (${FileUtils.byteCountToDisplaySize(writer.byteCount)}) to staging"
        }
        require(streamDescToWriteConfig.containsKey(streamDescriptor)) {
            String.format(
                "Message contained record from a stream that was not in the catalog. \ncatalog: %s",
                Jsons.serialize(catalog)
            )
        }

        val writeConfig: WriteConfig = streamDescToWriteConfig.getValue(streamDescriptor)
        val schemaName: String = writeConfig.rawNamespace
        val stageName = stagingOperations!!.getStageName(schemaName, writeConfig.rawTableName)
        val stagingPath =
            stagingOperations.getStagingPath(
                GeneralStagingFunctions.RANDOM_CONNECTION_ID,
                schemaName,
                writeConfig.streamName,
                writeConfig.rawTableName,
                writeConfig.writeDatetime
            )
        try {
            val stagedFile =
                stagingOperations.uploadRecordsToStage(
                    database,
                    writer,
                    schemaName,
                    stageName,
                    stagingPath
                )
            GeneralStagingFunctions.copyIntoTableFromStage(
                database,
                stageName,
                stagingPath,
                listOf(stagedFile),
                writeConfig.rawTableName,
                schemaName,
                stagingOperations,
            )
        } catch (e: Exception) {
            logger.error(e) {
                "Failed to flush and commit buffer data into destination's raw table"
            }
            throw RuntimeException("Failed to upload buffer to stage and commit to destination", e)
        }

        writer.close()
    }
}
