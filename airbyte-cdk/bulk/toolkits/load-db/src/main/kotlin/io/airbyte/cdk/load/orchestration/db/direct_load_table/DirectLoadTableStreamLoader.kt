/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

/**
 * Stream loader implementation for append mode.
 *
 * This loader handles the simplest case of appending data to an existing target table. If a
 * temporary table exists, it copies its data to the real table then drops the temp table. All
 * processing writes directly to the real table, without any deduplication.
 */
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
        logger.info {
            "AppendStreamLoader starting for stream ${stream.descriptor.toPrettyString()}"
        }
        if (initialStatus.realTable == null) {
            sqlTableOperations.createTable(stream, realTableName, columnNameMapping, replace = true)
        } else {
            nativeTableOperations.ensureSchemaMatches(stream, realTableName, columnNameMapping)
        }
        if (initialStatus.tempTable != null) {
            logger.info {
                "Processing temp table data: ${tempTableName.toPrettyString()} -> ${realTableName.toPrettyString()} for stream ${stream.descriptor.toPrettyString()}"
            }
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

/**
 * Stream loader implementation for deduplication mode.
 *
 * This loader ensures uniqueness by writing to a temporary table first, then using an upsert
 * operation to update the real table with deduplicated data. It handles cases where the temporary
 * table may already exist from a previous run, and ensures that the schema of both tables is
 * properly maintained.
 */
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
            logger.info {
                "Creating new temp table: ${tempTableName.toPrettyString()} for stream: ${stream.descriptor}"
            }
            sqlTableOperations.createTable(stream, tempTableName, columnNameMapping, replace = true)
        }

        streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(tempTableName))
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        if (initialStatus.realTable != null) {
            nativeTableOperations.ensureSchemaMatches(stream, realTableName, columnNameMapping)
        } else {
            sqlTableOperations.createTable(stream, realTableName, columnNameMapping, replace = true)
        }
        sqlTableOperations.upsertTable(
            stream,
            columnNameMapping,
            sourceTableName = tempTableName,
            targetTableName = realTableName,
        )
        sqlTableOperations.dropTable(tempTableName)
    }
}

/**
 * Stream loader implementation for append + truncate mode.
 *
 * This loader combines append and truncate behaviors, allowing for overwriting data in the target
 * table. It conditionally uses either a temporary table or the real table depending on generation
 * IDs and initial status. When using a temporary table, it overwrites the real table with the
 * temporary table's data during close.
 *
 * Generation IDs are used to determine whether existing tables can be reused or need to be
 * recreated to ensure data consistency.
 */
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
    /**
     * Indicates whether we're writing to the temporary table or directly to the real table. This is
     * determined during start() based on table states and generation IDs.
     * - true: Writing to temp table, will need to copy/overwrite to real table later
     * - false: Writing directly to real table, no additional action needed at close
     */
    private var isWritingToTemporaryTable: Boolean = false

    override suspend fun start() {
        logger.info {
            "AppendTruncateStreamLoader starting for stream ${stream.descriptor.toPrettyString()}"
        }

        if (initialStatus.tempTable != null) {
            if (initialStatus.tempTable.isEmpty) {
                nativeTableOperations.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
            } else {
                val generationId = nativeTableOperations.getGenerationId(tempTableName)
                if (generationId >= stream.minimumGenerationId) {
                    nativeTableOperations.ensureSchemaMatches(
                        stream,
                        tempTableName,
                        columnNameMapping
                    )
                } else {
                    logger.info {
                        "Recreating temp table ${tempTableName.toPrettyString()} (old generation ID: $generationId) for stream ${stream.descriptor.toPrettyString()}"
                    }
                    sqlTableOperations.createTable(
                        stream,
                        tempTableName,
                        columnNameMapping,
                        replace = true
                    )
                }
            }
            isWritingToTemporaryTable = true
            streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(tempTableName))
        } else {
            if (initialStatus.realTable == null) {
                logger.info {
                    "Creating new real table: ${realTableName.toPrettyString()} for stream ${stream.descriptor.toPrettyString()}"
                }
                sqlTableOperations.createTable(
                    stream,
                    realTableName,
                    columnNameMapping,
                    replace = true
                )
                isWritingToTemporaryTable = false
            } else if (
                initialStatus.realTable.isEmpty ||
                    nativeTableOperations.getGenerationId(realTableName) >=
                        stream.minimumGenerationId
            ) {
                nativeTableOperations.ensureSchemaMatches(stream, realTableName, columnNameMapping)
                isWritingToTemporaryTable = false
            } else {
                logger.info {
                    "Creating temp table ${tempTableName.toPrettyString()} (real table has old generation ID) for stream ${stream.descriptor.toPrettyString()}"
                }
                sqlTableOperations.createTable(
                    stream,
                    tempTableName,
                    columnNameMapping,
                    replace = true
                )
                isWritingToTemporaryTable = true
            }
        }

        val targetTableName = if (isWritingToTemporaryTable) tempTableName else realTableName
        logger.info {
            "Target table: ${targetTableName.toPrettyString()} for stream ${stream.descriptor.toPrettyString()}"
        }
        streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(targetTableName))
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null && isWritingToTemporaryTable) {
            logger.info {
                "Overwriting ${tempTableName.toPrettyString()} with ${realTableName.toPrettyString()} for stream ${stream.descriptor.toPrettyString()}"
            }
            sqlTableOperations.overwriteTable(
                sourceTableName = tempTableName,
                targetTableName = realTableName
            )
        }
    }
}

/**
 * Stream loader implementation for deduplication + truncate mode.
 *
 * This loader provides the most complex functionality, combining both deduplication and table
 * truncation. It writes to a temporary table first, then depending on generation IDs and table
 * status, follows different strategies:
 *
 * 1. May upsert directly to the real table if appropriate
 * 2. May create a real table and upsert into it
 * 3. May use a temp-temp table approach to ensure proper deduplication before overwriting the real
 * table
 *
 * This strategy ensures optimal performance while maintaining data integrity across various
 * scenarios, including interrupted syncs and schema changes.
 */
class DirectLoadTableDedupTruncateStreamLoader(
    override val stream: DestinationStream,
    private val initialStatus: DirectLoadInitialStatus,
    private val realTableName: TableName,
    private val tempTableName: TableName,
    private val columnNameMapping: ColumnNameMapping,
    private val nativeTableOperations: DirectLoadTableNativeOperations,
    private val sqlTableOperations: DirectLoadTableSqlOperations,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : StreamLoader {
    // can't use lateinit because of weird kotlin reasons.
    /**
     * Indicates whether the real table potentially has the correct generation ID. This is
     * determined during start() based on whether we had a temp table initially.
     * - true: Real table may have correct generation, will check in close() before deciding final
     * approach
     * - false: Real table definitely has incorrect generation, will use temp-temp approach in
     * close()
     */
    private var shouldCheckRealTableGeneration: Boolean = false

    override suspend fun start() {
        logger.info {
            "DedupTruncateStreamLoader starting for stream ${stream.descriptor.toPrettyString()}"
        }

        if (initialStatus.tempTable != null) {
            if (initialStatus.tempTable.isEmpty) {
                nativeTableOperations.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
            } else {
                val generationId = nativeTableOperations.getGenerationId(tempTableName)
                if (generationId >= stream.minimumGenerationId) {
                    nativeTableOperations.ensureSchemaMatches(
                        stream,
                        tempTableName,
                        columnNameMapping
                    )
                } else {
                    logger.info {
                        "Recreating temp table ${tempTableName.toPrettyString()} (old generation ID: $generationId) for stream ${stream.descriptor.toPrettyString()}"
                    }
                    sqlTableOperations.createTable(
                        stream,
                        tempTableName,
                        columnNameMapping,
                        replace = true
                    )
                }
            }
            shouldCheckRealTableGeneration = false
        } else {
            logger.info {
                "Creating new temp table: ${tempTableName.toPrettyString()} for stream ${stream.descriptor.toPrettyString()}"
            }
            sqlTableOperations.createTable(stream, tempTableName, columnNameMapping, replace = true)
            shouldCheckRealTableGeneration = true
        }

        streamStateStore.put(stream.descriptor, DirectLoadTableExecutionConfig(tempTableName))
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            if (shouldCheckRealTableGeneration && shouldUpsertDirectly()) {
                // Direct upsert path for simpler cases
                logger.info {
                    "Upserting directly to real table for stream ${stream.descriptor.toPrettyString()}"
                }
                performDirectUpsert()
            } else {
                // Needs temp table and overwrite approach
                logger.info {
                    "Upserting to temp temp table for stream ${stream.descriptor.toPrettyString()}"
                }
                performUpsertWithTemporaryTable()
            }
        }
    }

    /** Determines if we can directly upsert without additional processing */
    private suspend fun shouldUpsertDirectly(): Boolean {
        return when {
            // Case 1: Real table doesn't exist yet
            initialStatus.realTable == null -> true

            // Case 2: Real table exists but is empty or has correct generation ID
            initialStatus.realTable.isEmpty ||
                nativeTableOperations.getGenerationId(realTableName) >=
                    stream.minimumGenerationId -> true

            // Case 3: Real table exists with data - needs more stringent approach
            else -> false
        }
    }

    /** Performs direct upsert from temp table to real table */
    private suspend fun performDirectUpsert() {
        // Create or ensure schema of real table
        if (initialStatus.realTable == null) {
            sqlTableOperations.createTable(stream, realTableName, columnNameMapping, replace = true)
        } else {
            nativeTableOperations.ensureSchemaMatches(stream, realTableName, columnNameMapping)
        }

        // Upsert data from temp to real table
        sqlTableOperations.upsertTable(
            stream,
            columnNameMapping,
            sourceTableName = tempTableName,
            targetTableName = realTableName
        )

        // Clean up temporary table
        sqlTableOperations.dropTable(tempTableName)
    }

    /** Performs upsert using an additional temporary table for safer operation */
    private suspend fun performUpsertWithTemporaryTable() {
        val tempTempTable = tempTableNameGenerator.generate(tempTableName)

        // Create temporary table for intermediate operations
        sqlTableOperations.createTable(stream, tempTempTable, columnNameMapping, replace = true)

        // Upsert from temp to temp-temp table
        sqlTableOperations.upsertTable(
            stream,
            columnNameMapping,
            sourceTableName = tempTableName,
            targetTableName = tempTempTable
        )

        // Overwrite real table with final data
        sqlTableOperations.overwriteTable(
            sourceTableName = tempTempTable,
            targetTableName = realTableName
        )
    }
}
