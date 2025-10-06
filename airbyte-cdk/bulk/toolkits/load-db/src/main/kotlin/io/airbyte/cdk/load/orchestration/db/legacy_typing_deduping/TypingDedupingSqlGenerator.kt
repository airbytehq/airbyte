/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.TableNames.Companion.SOFT_RESET_SUFFIX
import java.time.Instant

interface TypingDedupingSqlGenerator {
    /**
     * Generate a SQL statement to create a fresh table to match the given stream.
     *
     * The generated SQL should throw an exception if the table already exists and `replace` is
     * false.
     *
     * @param finalTableSuffix A suffix to add to the stream name. Useful for full refresh overwrite
     * syncs, where we write the entire sync to a temp table.
     * @param replace If true, will overwrite an existing table. If false, will throw an exception
     * if the table already exists. If you're passing a non-empty prefix, you likely want to set
     * this to true.
     */
    fun createFinalTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        replace: Boolean
    ): Sql

    /**
     * Whether [updateFinalTable] actually generates different SQL when `useExpensiveSaferCasting`
     * is enabled. Some destinations don't have this distinction, and should override this field to
     * `false`.
     */
    val supportsExpensiveSaferCasting: Boolean
        get() = true

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
     * @param finalTableSuffix the suffix of the final table to write to. If empty string, writes to
     * the final table directly. Useful for full refresh overwrite syncs, where we write the entire
     * sync to a temp table and then swap it into the final table at the end.
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
    fun updateFinalTable(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        maxProcessedTimestamp: Instant?,
        useExpensiveSaferCasting: Boolean,
    ): Sql

    /**
     * Drop the previous final table, and rename the new final table to match the old final table.
     *
     * This method may assume that the stream is an OVERWRITE stream, and that the final suffix is
     * non-empty. Callers are responsible for verifying those are true.
     */
    fun overwriteFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        finalTableSuffix: String,
    ): Sql

    fun clearLoadedAt(stream: DestinationStream, rawTableName: TableName): Sql

    /** Typically we need to create a soft reset temporary table and clear loaded at values */
    fun prepareTablesForSoftReset(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
    ): Sql {
        val createTempTable =
            createFinalTable(
                stream,
                tableNames.finalTableName!!,
                columnNameMapping,
                SOFT_RESET_SUFFIX,
                replace = true
            )
        val clearLoadedAt = clearLoadedAt(stream, tableNames.rawTableName!!)
        return Sql.concat(createTempTable, clearLoadedAt)
    }
}

/**
 * We are switching all destinations away from T+D, to use direct-load tables instead. However, some
 * destinations will continue to provide a "legacy raw tables" mode, which writes the raw table
 * format of T+D, but with the actual T+D disabled.
 *
 * This sqlgenerator supports that, by simply doing nothing.
 */
object NoopTypingDedupingSqlGenerator : TypingDedupingSqlGenerator {
    override fun createFinalTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        replace: Boolean
    ) = Sql.empty()

    override fun updateFinalTable(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        maxProcessedTimestamp: Instant?,
        useExpensiveSaferCasting: Boolean
    ) = Sql.empty()

    override fun overwriteFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        finalTableSuffix: String
    ) = Sql.empty()

    override fun clearLoadedAt(stream: DestinationStream, rawTableName: TableName) = Sql.empty()
}
