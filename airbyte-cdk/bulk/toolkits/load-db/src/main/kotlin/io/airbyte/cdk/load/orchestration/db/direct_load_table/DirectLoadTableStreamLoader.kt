/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class DirectLoadTableAppendStreamLoader(
    override val stream: DestinationStream,
    private val initialStatus: DirectLoadInitialStatus,
    private val realTableName: TableName,
    private val tempTableName: TableName,
    private val columnNameMapping: ColumnNameMapping,
    private val nativeTableOperations: DirectLoadTableNativeOperations,
    private val sqlTableOperations: DirectLoadTableSqlOperations,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : StreamLoader {
    override suspend fun start() {
        logger.info { "AppendStreamLoader starting for stream: ${stream.descriptor}" }

        nativeTableOperations.ensureSchemaMatches(stream, realTableName, columnNameMapping)

        if (initialStatus.tempTable != null) {
            logger.info { "Processing temp table data: $tempTableName -> $realTableName" }
            nativeTableOperations.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
            sqlTableOperations.copyTable(
                columnNameMapping,
                sourceTableName = tempTableName,
                targetTableName = realTableName,
            )
            sqlTableOperations.dropTable(tempTableName)
        }

        streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(realTableName))
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        // do nothing
    }
}

class DirectLoadTableDedupStreamLoader(
    override val stream: DestinationStream,
    private val initialStatus: DirectLoadInitialStatus,
    private val realTableName: TableName,
    private val tempTableName: TableName,
    private val columnNameMapping: ColumnNameMapping,
    private val nativeTableOperations: DirectLoadTableNativeOperations,
    private val sqlTableOperations: DirectLoadTableSqlOperations,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : StreamLoader {
    override suspend fun start() {
        logger.info { "DedupStreamLoader starting for stream: ${stream.descriptor}" }

        if (initialStatus.tempTable != null) {
            nativeTableOperations.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        } else {
            logger.info { "Creating new temp table: $tempTableName" }
            sqlTableOperations.createTable(stream, tempTableName, columnNameMapping, replace = true)
        }

        streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(tempTableName))
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        nativeTableOperations.ensureSchemaMatches(stream, realTableName, columnNameMapping)
        sqlTableOperations.upsertTable(
            stream,
            columnNameMapping,
            sourceTableName = tempTableName,
            targetTableName = realTableName,
        )
        sqlTableOperations.dropTable(tempTableName)
    }
}

class DirectLoadTableAppendTruncateStreamLoader(
    override val stream: DestinationStream,
    private val initialStatus: DirectLoadInitialStatus,
    private val realTableName: TableName,
    private val tempTableName: TableName,
    private val columnNameMapping: ColumnNameMapping,
    private val nativeTableOperations: DirectLoadTableNativeOperations,
    private val sqlTableOperations: DirectLoadTableSqlOperations,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : StreamLoader {
    // can't use lateinit because of weird kotlin reasons.
    // this field is always overwritten in start().
    private var writingToTempTable: Boolean = false

    override suspend fun start() {
        logger.info { "AppendTruncateStreamLoader starting for stream: ${stream.descriptor}" }

        if (initialStatus.tempTable != null) {
            val generationId = nativeTableOperations.getGenerationId(tempTableName)

            if (initialStatus.tempTable.isEmpty || generationId >= stream.minimumGenerationId) {
                nativeTableOperations.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
            } else {
                logger.info { "Recreating temp table (old generation ID: $generationId)" }
                sqlTableOperations.createTable(
                    stream,
                    tempTableName,
                    columnNameMapping,
                    replace = true
                )
            }
            writingToTempTable = true
            streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(tempTableName))
        } else {
            if (initialStatus.realTable == null) {
                logger.info { "Creating new real table: $realTableName" }
                sqlTableOperations.createTable(
                    stream,
                    realTableName,
                    columnNameMapping,
                    replace = true
                )
                writingToTempTable = false
            } else if (
                initialStatus.realTable.isEmpty ||
                    nativeTableOperations.getGenerationId(realTableName) >=
                        stream.minimumGenerationId
            ) {
                nativeTableOperations.ensureSchemaMatches(stream, realTableName, columnNameMapping)
                writingToTempTable = false
            } else {
                logger.info { "Creating temp table (real table has old generation ID)" }
                sqlTableOperations.createTable(
                    stream,
                    tempTableName,
                    columnNameMapping,
                    replace = true
                )
                writingToTempTable = true
            }
        }

        logger.info { "Target table: ${if (writingToTempTable) tempTableName else realTableName}" }
        if (writingToTempTable) {
            streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(tempTableName))
        } else {
            streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(realTableName))
        }
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null && writingToTempTable) {
            sqlTableOperations.overwriteTable(
                sourceTableName = tempTableName,
                targetTableName = realTableName
            )
        }
    }
}

class DirectLoadTableDedupTruncateStreamLoader(
    override val stream: DestinationStream,
    private val initialStatus: DirectLoadInitialStatus,
    private val realTableName: TableName,
    private val tempTableName: TableName,
    private val columnNameMapping: ColumnNameMapping,
    private val nativeTableOperations: DirectLoadTableNativeOperations,
    private val sqlTableOperations: DirectLoadTableSqlOperations,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : StreamLoader {
    // can't use lateinit because of weird kotlin reasons.
    // this field is always overwritten in start().
    private var finalTableMaybeCorrectGeneration: Boolean = false

    override suspend fun start() {
        logger.info { "DedupTruncateStreamLoader starting for stream: ${stream.descriptor}" }

        if (initialStatus.tempTable != null) {
            val generationId = nativeTableOperations.getGenerationId(tempTableName)

            if (initialStatus.tempTable.isEmpty || generationId >= stream.minimumGenerationId) {
                nativeTableOperations.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
            } else {
                logger.info { "Recreating temp table (old generation ID: $generationId)" }
                sqlTableOperations.createTable(
                    stream,
                    tempTableName,
                    columnNameMapping,
                    replace = true
                )
            }
            finalTableMaybeCorrectGeneration = false
        } else {
            logger.info { "Creating new temp table: $tempTableName" }
            sqlTableOperations.createTable(stream, tempTableName, columnNameMapping, replace = true)
            finalTableMaybeCorrectGeneration = true
        }

        streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(tempTableName))
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        if (finalTableMaybeCorrectGeneration) {
            if (initialStatus.realTable == null) {
                logger.info { "Creating real table and upserting data" }
                sqlTableOperations.createTable(
                    stream,
                    realTableName,
                    columnNameMapping,
                    replace = true
                )

                sqlTableOperations.upsertTable(
                    stream,
                    columnNameMapping,
                    sourceTableName = tempTableName,
                    targetTableName = realTableName,
                )

                sqlTableOperations.dropTable(tempTableName)
                return
            } else if (
                initialStatus.realTable.isEmpty ||
                    nativeTableOperations.getGenerationId(realTableName) >=
                        stream.minimumGenerationId
            ) {
                logger.info { "Upserting to existing real table" }
                sqlTableOperations.upsertTable(
                    stream,
                    columnNameMapping,
                    sourceTableName = tempTableName,
                    targetTableName = realTableName
                )

                sqlTableOperations.dropTable(tempTableName)
                return
            }
        }

        if (streamFailure == null) {
            val tempTempTable = tempTableName.asTempTable()
            sqlTableOperations.createTable(stream, tempTempTable, columnNameMapping, replace = true)
            sqlTableOperations.upsertTable(
                stream,
                columnNameMapping,
                sourceTableName = tempTableName,
                targetTableName = tempTempTable
            )
            sqlTableOperations.overwriteTable(
                sourceTableName = tempTempTable,
                targetTableName = realTableName
            )
        }
    }
}
