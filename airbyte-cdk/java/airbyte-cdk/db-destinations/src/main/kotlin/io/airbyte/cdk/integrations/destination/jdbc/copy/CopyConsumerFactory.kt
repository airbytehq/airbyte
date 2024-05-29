/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.*
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.cdk.integrations.destination.jdbc.constants.GlobalDataSizeConstants
import io.airbyte.cdk.integrations.destination.record_buffer.InMemoryRecordBufferingStrategy
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Consumer
import javax.sql.DataSource

private val LOGGER = KotlinLogging.logger {}

// TODO: Delete this class, this is only used in StarburstGalaxyDestination
object CopyConsumerFactory {

    fun <T> create(
        outputRecordCollector: Consumer<AirbyteMessage>,
        dataSource: DataSource,
        database: JdbcDatabase,
        sqlOperations: SqlOperations,
        namingResolver: StandardNameTransformer,
        config: T,
        catalog: ConfiguredAirbyteCatalog,
        streamCopierFactory: StreamCopierFactory<T>,
        defaultSchema: String
    ): AirbyteMessageConsumer {
        val pairToCopier =
            createWriteConfigs(
                namingResolver,
                config,
                catalog,
                streamCopierFactory,
                defaultSchema,
                database,
                sqlOperations
            )

        val pairToIgnoredRecordCount: MutableMap<AirbyteStreamNameNamespacePair, Long> = HashMap()
        return BufferedStreamConsumer(
            outputRecordCollector = outputRecordCollector,
            onStart = onStartFunction(pairToIgnoredRecordCount),
            bufferingStrategy =
                InMemoryRecordBufferingStrategy(
                    recordWriterFunction(pairToCopier, sqlOperations, pairToIgnoredRecordCount),
                    removeStagingFilePrinter(pairToCopier),
                    GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES.toLong()
                ),
            onClose =
                onCloseFunction(
                    pairToCopier,
                    database,
                    sqlOperations,
                    pairToIgnoredRecordCount,
                    dataSource
                ),
            catalog = catalog,
            isValidRecord = { data: JsonNode? -> sqlOperations.isValidData(data) },
            defaultNamespace = null,
        )
    }

    private fun <T> createWriteConfigs(
        namingResolver: StandardNameTransformer,
        config: T,
        catalog: ConfiguredAirbyteCatalog,
        streamCopierFactory: StreamCopierFactory<T>,
        defaultSchema: String,
        database: JdbcDatabase,
        sqlOperations: SqlOperations
    ): Map<AirbyteStreamNameNamespacePair, StreamCopier> {
        val pairToCopier: MutableMap<AirbyteStreamNameNamespacePair, StreamCopier> = HashMap()
        val stagingFolder = UUID.randomUUID().toString()
        for (configuredStream in catalog.streams) {
            val stream = configuredStream.stream
            val pair = AirbyteStreamNameNamespacePair.fromAirbyteStream(stream)
            val copier =
                streamCopierFactory.create(
                    defaultSchema,
                    config,
                    stagingFolder,
                    configuredStream,
                    namingResolver,
                    database,
                    sqlOperations
                )

            pairToCopier[pair] = copier
        }

        return pairToCopier
    }

    private fun onStartFunction(
        pairToIgnoredRecordCount: MutableMap<AirbyteStreamNameNamespacePair, Long>
    ): OnStartFunction {
        return OnStartFunction { pairToIgnoredRecordCount.clear() }
    }

    private fun recordWriterFunction(
        pairToCopier: Map<AirbyteStreamNameNamespacePair, StreamCopier>,
        sqlOperations: SqlOperations,
        pairToIgnoredRecordCount: MutableMap<AirbyteStreamNameNamespacePair, Long>
    ): RecordWriter<AirbyteRecordMessage> {
        return RecordWriter<AirbyteRecordMessage> {
            pair: AirbyteStreamNameNamespacePair,
            records: List<AirbyteRecordMessage> ->
            val fileName = pairToCopier[pair]!!.prepareStagingFile()
            for (recordMessage in records) {
                val id = UUID.randomUUID()
                if (sqlOperations.isValidData(recordMessage.data)) {
                    // TODO Truncate json data instead of throwing whole record away?
                    // or should we upload it into a special rejected record folder in s3 instead?
                    pairToCopier[pair]!!.write(id, recordMessage, fileName)
                } else {
                    pairToIgnoredRecordCount[pair] =
                        pairToIgnoredRecordCount.getOrDefault(pair, 0L) + 1L
                }
            }
        }
    }

    private fun removeStagingFilePrinter(
        pairToCopier: Map<AirbyteStreamNameNamespacePair, StreamCopier>
    ): CheckAndRemoveRecordWriter {
        return CheckAndRemoveRecordWriter {
            pair: AirbyteStreamNameNamespacePair,
            stagingFileName: String? ->
            val currentFileName = pairToCopier[pair]!!.currentFile
            if (
                stagingFileName != null &&
                    currentFileName != null &&
                    stagingFileName != currentFileName
            ) {
                pairToCopier[pair]!!.closeNonCurrentStagingFileWriters()
            }
            currentFileName
        }
    }

    private fun onCloseFunction(
        pairToCopier: Map<AirbyteStreamNameNamespacePair, StreamCopier>,
        database: JdbcDatabase,
        sqlOperations: SqlOperations,
        pairToIgnoredRecordCount: Map<AirbyteStreamNameNamespacePair, Long>,
        dataSource: DataSource
    ): OnCloseFunction {
        return OnCloseFunction { hasFailed: Boolean, _: Map<StreamDescriptor, StreamSyncSummary> ->
            pairToIgnoredRecordCount.forEach { (pair: AirbyteStreamNameNamespacePair?, count: Long?)
                ->
                LOGGER.warn {
                    "A total of $count record(s) of data from stream $pair were invalid and were ignored."
                }
            }
            closeAsOneTransaction(pairToCopier, hasFailed, database, sqlOperations, dataSource)
        }
    }

    @Throws(Exception::class)
    private fun closeAsOneTransaction(
        pairToCopier: Map<AirbyteStreamNameNamespacePair, StreamCopier>,
        hasFailed: Boolean,
        db: JdbcDatabase,
        sqlOperations: SqlOperations,
        dataSource: DataSource
    ) {
        var failed = hasFailed
        var firstException: Exception? = null
        val streamCopiers: List<StreamCopier> = ArrayList(pairToCopier.values)
        try {
            val queries: MutableList<String> = ArrayList()
            for (copier in streamCopiers) {
                try {
                    copier.closeStagingUploader(failed)
                    if (!failed) {
                        copier.createDestinationSchema()
                        copier.createTemporaryTable()
                        copier.copyStagingFileToTemporaryTable()
                        val destTableName = copier.createDestinationTable()
                        val mergeQuery = copier.generateMergeStatement(destTableName)
                        queries.add(mergeQuery)
                    }
                } catch (e: Exception) {
                    val message = "Failed to finalize copy to temp table due to: $e"
                    LOGGER.error { message }
                    failed = true
                    if (firstException == null) {
                        firstException = e
                    }
                }
            }
            if (!failed) {
                sqlOperations.executeTransaction(db, queries)
            }
        } finally {
            for (copier in streamCopiers) {
                copier.removeFileAndDropTmpTable()
            }

            close(dataSource)
        }
        if (firstException != null) {
            throw firstException
        }
    }
}
