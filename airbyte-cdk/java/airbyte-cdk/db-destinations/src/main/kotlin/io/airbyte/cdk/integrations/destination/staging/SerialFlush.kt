/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.cdk.integrations.destination.record_buffer.FlushBufferFunction
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import kotlin.collections.HashMap
import kotlin.collections.HashSet
import org.apache.commons.io.FileUtils

private val log = KotlinLogging.logger {}

/**
 * Serial flushing logic. Though simpler, this causes unnecessary backpressure and slows down the
 * entire pipeline.
 *
 * Note: This class should be re-written so that is implements the [FlushBufferFunction] interface,
 * instead of return an anonymous function implementing this interface for clarity. As of this
 * writing, we avoid doing so to simplify the migration to async flushing.
 */
object SerialFlush {
    val RANDOM_CONNECTION_ID: UUID = UUID.randomUUID()
    /**
     * Logic handling how destinations with staging areas (aka bucket storages) will flush their
     * buffer
     *
     * @param database database used for syncing
     * @param stagingOperations collection of SQL queries necessary for writing data into a staging
     * area
     * @param writeConfigs configuration settings for all destination connectors needed to write
     * @param catalog collection of configured streams (e.g. API endpoints or database tables)
     * @return
     */
    @VisibleForTesting
    fun function(
        database: JdbcDatabase?,
        stagingOperations: StagingOperations,
        writeConfigs: List<WriteConfig>,
        catalog: ConfiguredAirbyteCatalog,
    ): FlushBufferFunction {
        // TODO: (ryankfu) move this block of code that executes before the lambda to
        // #onStartFunction
        val conflictingStreams: MutableSet<WriteConfig> = HashSet()
        val pairToWriteConfig: MutableMap<AirbyteStreamNameNamespacePair, WriteConfig> = HashMap()
        for (config in writeConfigs) {
            val streamIdentifier = toNameNamespacePair(config)
            if (pairToWriteConfig.containsKey(streamIdentifier)) {
                conflictingStreams.add(config)
                val existingConfig = pairToWriteConfig.getValue(streamIdentifier)
                // The first conflicting stream won't have any problems, so we need to explicitly
                // add it here.
                conflictingStreams.add(existingConfig)
            } else {
                pairToWriteConfig[streamIdentifier] = config
            }
        }
        if (!conflictingStreams.isEmpty()) {
            val message =
                String.format(
                    "You are trying to write multiple streams to the same table. Consider switching to a custom namespace format using \${SOURCE_NAMESPACE}, or moving one of them into a separate connection with a different stream prefix. Affected streams: %s",
                    conflictingStreams.joinToString(", ") { config: WriteConfig ->
                        config.namespace + "." + config.streamName
                    }
                )
            throw ConfigErrorException(message)
        }
        return FlushBufferFunction {
            pair: AirbyteStreamNameNamespacePair,
            writer: SerializableBuffer ->
            log.info {
                "Flushing buffer for stream ${pair.name} (${FileUtils.byteCountToDisplaySize(writer.byteCount)}) to staging"
            }
            require(pairToWriteConfig.containsKey(pair)) {
                String.format(
                    "Message contained record from a stream that was not in the catalog. \ncatalog: %s",
                    Jsons.serialize(catalog)
                )
            }

            val writeConfig = pairToWriteConfig.getValue(pair)
            val schemaName = writeConfig.rawNamespace
            val stageName = stagingOperations.getStageName(schemaName, writeConfig.rawTableName)
            val stagingPath =
                stagingOperations.getStagingPath(
                    RANDOM_CONNECTION_ID,
                    schemaName,
                    writeConfig.streamName,
                    writeConfig.rawTableName,
                    writeConfig.writeDatetime
                )
            try {
                writer.use {
                    writer.flush()
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
                }
            } catch (e: Exception) {
                log.error(e) {
                    "Failed to flush and commit buffer data into destination's raw table"
                }
                throw RuntimeException(
                    "Failed to upload buffer to stage and commit to destination",
                    e
                )
            }
        }
    }

    private fun toNameNamespacePair(config: WriteConfig): AirbyteStreamNameNamespacePair {
        return AirbyteStreamNameNamespacePair(config.streamName, config.namespace)
    }
}
