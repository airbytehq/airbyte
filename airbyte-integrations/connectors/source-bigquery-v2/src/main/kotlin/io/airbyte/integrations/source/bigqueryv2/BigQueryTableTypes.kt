/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.google.cloud.bigquery.TableDefinition
import io.airbyte.cdk.StreamIdentifier
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * Remembers the [TableDefinition.Type] of every table whose metadata was fetched during the current
 * operation, so that the query generator can tell tables from views.
 *
 * `TABLESAMPLE` is only legal on tables: BigQuery rejects it on views, materialized views and
 * external tables ("TABLESAMPLE is not supported on ..."). READ fetches the metadata of every
 * configured stream before creating partitions, so the type is known by the time a sampling query
 * is generated; anything unknown is assumed to be a table.
 */
@Singleton
class BigQueryTableTypes {
    private val types = ConcurrentHashMap<StreamIdentifier, TableDefinition.Type>()

    fun register(streamID: StreamIdentifier, type: TableDefinition.Type?) {
        if (type != null) types[streamID] = type
    }

    fun typeOf(streamID: StreamIdentifier): TableDefinition.Type? = types[streamID]

    /** Whether `TABLESAMPLE SYSTEM` may be applied to this stream's source. */
    fun supportsTableSample(streamID: StreamIdentifier): Boolean =
        when (types[streamID]) {
            null,
            TableDefinition.Type.TABLE,
            TableDefinition.Type.SNAPSHOT -> true
            else -> false
        }
}
