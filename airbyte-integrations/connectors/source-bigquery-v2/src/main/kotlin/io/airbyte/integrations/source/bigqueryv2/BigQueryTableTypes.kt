/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.google.cloud.bigquery.TableDefinition
import io.airbyte.cdk.StreamIdentifier
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * Remembers the [TableDefinition.Type] and the size of every table whose metadata was fetched
 * during the current operation, so that the query generator can tell tables from views and the
 * partition creators can size their work.
 *
 * `TABLESAMPLE` is only legal on base tables: BigQuery rejects it on views (and, per the message,
 * on anything else) with "TABLESAMPLE SYSTEM can only be applied directly to base tables."
 * (verified against the service on 2026-09-14). READ fetches the metadata of every configured
 * stream before creating partitions, so the type is known by the time a sampling query is
 * generated; anything unknown is assumed to be a table.
 */
@Singleton
class BigQueryTableTypes {
    private val facts = ConcurrentHashMap<StreamIdentifier, TableFacts>()

    /** What `tables.get` says about a table's kind and size. */
    data class TableFacts(
        val type: TableDefinition.Type?,
        /** `numBytes` of the table (logical bytes), null when BigQuery does not report it. */
        val numBytes: Long?,
        /** `numRows` of the table, null when BigQuery does not report it. */
        val numRows: Long?,
    )

    fun register(streamID: StreamIdentifier, type: TableDefinition.Type?) {
        register(streamID, TableFacts(type, numBytes = null, numRows = null))
    }

    fun register(streamID: StreamIdentifier, tableFacts: TableFacts) {
        facts[streamID] = tableFacts
    }

    fun typeOf(streamID: StreamIdentifier): TableDefinition.Type? = facts[streamID]?.type

    fun factsOf(streamID: StreamIdentifier): TableFacts? = facts[streamID]

    /** Whether `TABLESAMPLE SYSTEM` may be applied to this stream's source. */
    fun supportsTableSample(streamID: StreamIdentifier): Boolean =
        when (typeOf(streamID)) {
            null,
            TableDefinition.Type.TABLE -> true
            else -> false
        }
}
