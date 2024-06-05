/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.time.Instant
import java.util.*

interface SqlGenerator {
    fun buildStreamId(namespace: String, name: String, rawNamespaceOverride: String): StreamId

    fun buildColumnId(name: String): ColumnId {
        return buildColumnId(name, "")
    }

    fun buildColumnId(name: String, suffix: String?): ColumnId

    /**
     * Generate a SQL statement to create a fresh table to match the given stream.
     *
     * The generated SQL should throw an exception if the table already exists and `force` is false.
     *
     * @param suffix A suffix to add to the stream name. Useful for full refresh overwrite syncs,
     * where we write the entire sync to a temp table.
     * @param force If true, will overwrite an existing table. If false, will throw an exception if
     * the table already exists. If you're passing a non-empty prefix, you likely want to set this
     * to true.
     */
    fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql

    /**
     * TODO delete this; superseded by [DestinationHandler.createNamespaces]
     *
     * @param schema the schema to create
     * @return SQL to create the schema if it does not exist
     */
    fun createSchema(schema: String): Sql

    /**
     * Generate a SQL statement to copy new data from the raw table into the final table.
     *
     * Responsible for:
     *
     * * Pulling new raw records from a table (i.e. records with null _airbyte_loaded_at)
     * * Extracting the JSON fields and casting to the appropriate types
     * * Handling errors in those casts
     * * Merging those typed records into an existing table
     * * Updating the raw records with SET _airbyte_loaded_at = now()
     *
     * Implementing classes are recommended to break this into smaller methods, which can be tested
     * in isolation. However, this interface only requires a single mega-method.
     *
     * @param finalSuffix the suffix of the final table to write to. If empty string, writes to the
     * final table directly. Useful for full refresh overwrite syncs, where we write the entire sync
     * to a temp table and then swap it into the final table at the end.
     *
     * @param minRawTimestamp The latest _airbyte_extracted_at for which all raw records with that
     * timestamp have already been typed+deduped. Implementations MAY use this value in a
     * `_airbyte_extracted_at > minRawTimestamp` filter on the raw table to improve query
     * performance.
     * @param useExpensiveSaferCasting often the data coming from the source can be faithfully
     * represented in the destination without issue, and using a "CAST" expression works fine,
     * however sometimes we get badly typed data. In these cases we can use a more expensive query
     * which handles casting exceptions.
     */
    fun updateTable(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql

    /**
     * Drop the previous final table, and rename the new final table to match the old final table.
     *
     * This method may assume that the stream is an OVERWRITE stream, and that the final suffix is
     * non-empty. Callers are responsible for verifying those are true.
     */
    fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql

    /**
     * Creates a sql query which will create a v2 raw table from the v1 raw table, then performs a
     * soft reset.
     *
     * @param streamId the stream to migrate
     * @param namespace the namespace of the v1 raw table
     * @param tableName name of the v2 raw table
     * @return a string containing the necessary sql to migrate
     */
    fun migrateFromV1toV2(streamId: StreamId, namespace: String, tableName: String): Sql

    /**
     * Typically we need to create a soft reset temporary table and clear loaded at values
     *
     * @return
     */
    fun prepareTablesForSoftReset(stream: StreamConfig): Sql {
        val createTempTable = createTable(stream, TyperDeduperUtil.SOFT_RESET_SUFFIX, true)
        val clearLoadedAt = clearLoadedAt(stream.id)
        return Sql.Companion.concat(createTempTable, clearLoadedAt)
    }

    fun clearLoadedAt(streamId: StreamId): Sql

    /**
     * Implementation specific if there is no option to retry again with safe casted SQL or the
     * specific cause of the exception can be retried or not.
     *
     * @return true if the exception should be retried with a safer query
     */
    fun shouldRetry(e: Exception?): Boolean {
        return true
    }
}
