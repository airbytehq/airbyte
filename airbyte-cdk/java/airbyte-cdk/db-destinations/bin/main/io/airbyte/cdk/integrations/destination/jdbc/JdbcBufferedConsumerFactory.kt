/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.deser.IdentityDataTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.concurrent.Executors
import java.util.function.Consumer
import java.util.function.Function

private val LOGGER = KotlinLogging.logger {}
/**
 * Strategy:
 *
 * 1. Create a final table for each stream
 *
 * 2. Accumulate records in a buffer. One buffer per stream
 *
 * 3. As records accumulate write them in batch to the database. We set a minimum numbers of records
 * before writing to avoid wasteful record-wise writes. In the case with slow syncs this will be
 * superseded with a periodic record flush from [BufferedStreamConsumer.periodicBufferFlush]
 *
 * 4. Once all records have been written to buffer, flush the buffer and write any remaining records
 * to the database (regardless of how few are left)
 */
object JdbcBufferedConsumerFactory {

    const val DEFAULT_OPTIMAL_BATCH_SIZE_FOR_FLUSH = 25 * 1024 * 1024L

    /** @param parsedCatalog Nullable for v1 destinations. Required for v2 destinations. */
    fun createAsync(
        outputRecordCollector: Consumer<AirbyteMessage>,
        database: JdbcDatabase,
        sqlOperations: SqlOperations,
        generationIdHandler: JdbcGenerationHandler,
        namingResolver: NamingConventionTransformer,
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        defaultNamespace: String,
        typerDeduper: TyperDeduper,
        dataTransformer: StreamAwareDataTransformer = IdentityDataTransformer(),
        optimalBatchSizeBytes: Long = DEFAULT_OPTIMAL_BATCH_SIZE_FOR_FLUSH,
        parsedCatalog: ParsedCatalog,
    ): SerializedAirbyteMessageConsumer {
        if (sqlOperations.isSchemaRequired) {
            Preconditions.checkState(
                config.has("schema"),
                "jdbc destinations must specify a schema."
            )
        }
        val writeConfigs = mutableListOf<WriteConfig>()

        return AsyncStreamConsumer(
            outputRecordCollector,
            onStartFunction(
                database,
                sqlOperations,
                generationIdHandler,
                writeConfigs,
                typerDeduper,
                namingResolver,
                parsedCatalog
            ),
            onCloseFunction(
                database,
                sqlOperations,
                generationIdHandler,
                parsedCatalog,
                typerDeduper
            ),
            JdbcInsertFlushFunction(
                defaultNamespace,
                recordWriterFunction(database, sqlOperations, writeConfigs, catalog),
                optimalBatchSizeBytes
            ),
            catalog,
            BufferManager(defaultNamespace, (Runtime.getRuntime().maxMemory() * 0.2).toLong()),
            FlushFailure(),
            Executors.newFixedThreadPool(2),
            AirbyteMessageDeserializer(dataTransformer)
        )
    }

    private fun createWriteConfigs(
        database: JdbcDatabase,
        generationIdHandler: JdbcGenerationHandler,
        namingResolver: NamingConventionTransformer,
        parsedCatalog: ParsedCatalog,
    ): List<WriteConfig> {
        return parsedCatalog.streams.map {
            val rawSuffix: String =
                if (
                    it.minimumGenerationId == 0L ||
                        generationIdHandler.getGenerationIdInTable(
                            database,
                            it.id.rawNamespace,
                            it.id.rawName
                        ) == it.generationId
                ) {
                    AbstractStreamOperation.NO_SUFFIX
                } else {
                    AbstractStreamOperation.TMP_TABLE_SUFFIX
                }
            parsedStreamToWriteConfig(namingResolver, rawSuffix).apply(it)
        }
    }

    private fun parsedStreamToWriteConfig(
        namingResolver: NamingConventionTransformer,
        rawTableSuffix: String,
    ): Function<StreamConfig, WriteConfig> {
        return Function { streamConfig: StreamConfig ->
            // TODO We should probably replace WriteConfig with StreamConfig?
            // The only thing I'm not sure about is the tmpTableName thing,
            // but otherwise it's a strict improvement (avoids people accidentally
            // recomputing the table names, instead of just treating the output of
            // CatalogParser as canonical).
            WriteConfig(
                streamConfig.id.originalName,
                streamConfig.id.originalNamespace,
                streamConfig.id.rawNamespace,
                @Suppress("deprecation")
                namingResolver.getTmpTableName(streamConfig.id.rawNamespace),
                streamConfig.id.rawName,
                streamConfig.postImportAction,
                streamConfig.syncId,
                streamConfig.generationId,
                streamConfig.minimumGenerationId,
                rawTableSuffix,
            )
        }
    }

    /**
     * Sets up destination storage through:
     *
     * 1. Creates Schema (if not exists)
     *
     * 2. Creates airybte_raw table (if not exists)
     *
     * 3. <Optional>Truncates table if sync mode is in OVERWRITE
     *
     * @param database JDBC database to connect to
     * @param sqlOperations interface for execution SQL queries
     * @param writeConfigs settings for each stream </Optional>
     */
    private fun onStartFunction(
        database: JdbcDatabase,
        sqlOperations: SqlOperations,
        generationIdHandler: JdbcGenerationHandler,
        writeConfigs: MutableList<WriteConfig>,
        typerDeduper: TyperDeduper,
        namingResolver: NamingConventionTransformer,
        parsedCatalog: ParsedCatalog,
    ): OnStartFunction {
        return OnStartFunction {
            typerDeduper.prepareSchemasAndRunMigrations()
            writeConfigs.addAll(
                createWriteConfigs(database, generationIdHandler, namingResolver, parsedCatalog)
            )
            LOGGER.info {
                "Preparing raw tables in destination started for ${writeConfigs.size} streams"
            }
            val queryList: MutableList<String> = ArrayList()
            for (writeConfig in writeConfigs) {
                val schemaName = writeConfig.rawNamespace
                val dstTableName = writeConfig.rawTableName
                LOGGER.info {
                    "Preparing raw table in destination started for stream ${writeConfig.streamName}. schema: $schemaName, table name: $dstTableName"
                }
                sqlOperations.createSchemaIfNotExists(database, schemaName)
                sqlOperations.createTableIfNotExists(database, schemaName, dstTableName)
                // if rawSuffix is empty, this is a no-op
                sqlOperations.createTableIfNotExists(
                    database,
                    schemaName,
                    dstTableName + writeConfig.rawTableSuffix
                )
                when (writeConfig.minimumGenerationId) {
                    0L -> {}
                    writeConfig.generationId ->
                        if (
                            generationIdHandler.getGenerationIdInTable(
                                database,
                                schemaName,
                                dstTableName + writeConfig.rawTableSuffix
                            ) != writeConfig.generationId
                        ) {
                            queryList.add(
                                sqlOperations.truncateTableQuery(
                                    database,
                                    schemaName,
                                    dstTableName + writeConfig.rawTableSuffix,
                                )
                            )
                        }
                    else ->
                        throw IllegalStateException(
                            "Invalid minimumGenerationId ${writeConfig.minimumGenerationId} for stream ${writeConfig.streamName}. generationId=${writeConfig.generationId}"
                        )
                }
            }
            sqlOperations.executeTransaction(database, queryList)
            LOGGER.info { "Preparing raw tables in destination completed." }
            typerDeduper.prepareFinalTables()
        }
    }

    /**
     * Writes [AirbyteRecordMessage] to JDBC database's airbyte_raw table
     *
     * @param database JDBC database to connect to
     * @param sqlOperations interface of SQL queries to execute
     * @param writeConfigs settings for each stream
     * @param catalog catalog of all streams to sync
     */
    private fun recordWriterFunction(
        database: JdbcDatabase,
        sqlOperations: SqlOperations,
        writeConfigs: List<WriteConfig>,
        catalog: ConfiguredAirbyteCatalog,
    ): RecordWriter<PartialAirbyteMessage> {
        var pairToWriteConfig: Map<AirbyteStreamNameNamespacePair, WriteConfig> = emptyMap()

        return RecordWriter {
            pair: AirbyteStreamNameNamespacePair,
            records: List<PartialAirbyteMessage> ->
            if (!pairToWriteConfig.containsKey(pair)) {
                synchronized(JdbcBufferedConsumerFactory) {
                    pairToWriteConfig = writeConfigs.associateBy { toNameNamespacePair(it) }
                }
            }
            require(pairToWriteConfig.containsKey(pair)) {
                String.format(
                    "Message contained record from a stream that was not in the catalog. \ncatalog: %s, \nstream identifier: %s\nkeys: %s",
                    Jsons.serialize(catalog),
                    pair,
                    pairToWriteConfig.keys
                )
            }
            val writeConfig = pairToWriteConfig.getValue(pair)
            sqlOperations.insertRecords(
                database,
                ArrayList(records),
                writeConfig.rawNamespace,
                writeConfig.rawTableName + writeConfig.rawTableSuffix,
                writeConfig.syncId,
                writeConfig.generationId,
            )
        }
    }

    /** Tear down functionality */
    private fun onCloseFunction(
        database: JdbcDatabase,
        sqlOperations: SqlOperations,
        generationIdHandler: JdbcGenerationHandler,
        catalog: ParsedCatalog,
        typerDeduper: TyperDeduper
    ): OnCloseFunction {
        return OnCloseFunction {
            _: Boolean,
            streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary> ->
            try {
                catalog.streams.forEach {
                    if (
                        it.minimumGenerationId != 0L &&
                            generationIdHandler.getGenerationIdInTable(
                                database,
                                it.id.rawNamespace,
                                it.id.rawName
                            ) != it.generationId &&
                            streamSyncSummaries
                                .getValue(it.id.asStreamDescriptor())
                                .terminalStatus ==
                                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                    ) {
                        sqlOperations.overwriteRawTable(database, it.id.rawNamespace, it.id.rawName)
                    }
                }
                typerDeduper.typeAndDedupe(streamSyncSummaries)
                typerDeduper.commitFinalTables(streamSyncSummaries)
                typerDeduper.cleanup()
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }
    }

    private fun toNameNamespacePair(config: WriteConfig): AirbyteStreamNameNamespacePair {
        return AirbyteStreamNameNamespacePair(config.streamName, config.namespace)
    }
}
