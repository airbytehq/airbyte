/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.dataflow

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.starrocks.http.StreamLoadClient
import io.airbyte.integrations.destination.starrocks.spec.LoadCompression
import io.airbyte.integrations.destination.starrocks.spec.StarrocksConfiguration
import io.airbyte.integrations.destination.starrocks.tunnel.StarrocksSshTunnel
import io.airbyte.integrations.destination.starrocks.version.StarrocksVersionGate
import io.airbyte.integrations.destination.starrocks.write.load.CsvRowInsertBuffer
import io.airbyte.integrations.destination.starrocks.write.load.JsonRowInsertBuffer
import io.airbyte.integrations.destination.starrocks.write.load.RowInsertBuffer
import io.airbyte.integrations.destination.starrocks.write.load.SqlRowInsertBuffer
import io.micronaut.context.annotation.Factory

/** Wraps a [RowInsertBuffer]: each accepted record is buffered; [flush] issues Stream Load. */
class StarrocksAggregate(
    internal val buffer: RowInsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}

@Factory
class StarrocksAggregateFactory(
    private val catalog: DestinationCatalog,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val streamLoadClient: StreamLoadClient,
    private val config: StarrocksConfiguration,
    private val capabilities: StarrocksVersionGate.Capabilities,
    private val tunnel: StarrocksSshTunnel,
) : AggregateFactory {

    override fun create(key: DestinationStream.Descriptor): Aggregate {
        val tableName =
            requireNotNull(streamStateStore.get(key)) {
                    "No Stream Load execution config for stream '${key.name}'"
                }
                .tableName
        val stream = catalog.getStream(key)
        val cdcDelete = cdcDeleteEnabled(stream)

        require(
            !opColumnCollides(
                cdcDelete,
                config.loadAsSql,
                stream.tableSchema.columnSchema.finalSchema.keys
            ),
        ) {
            "Stream '${key.name}' has a column named '${CsvRowInsertBuffer.OP_COLUMN}', which collides " +
                "with the CDC operation column StarRocks uses for load-time delete/upsert. Rename it at the source."
        }

        val columns = finalColumns(stream)
        val buffer: RowInsertBuffer =
            when {
                // SQL load (#68): batched INSERT/DELETE over the (tunneled/TLS) JDBC connection.
                config.loadAsSql ->
                    SqlRowInsertBuffer(
                        tableName,
                        columns,
                        cdcDelete,
                        primaryKeyColumns(stream),
                        // rewriteBatchedStatements -> one multi-row INSERT per batch;
                        // useServerPrepStmts
                        // =false keeps client-side prep (StarRocks rejects MySQL server-prepared
                        // stmts).
                        config.jdbcUrlFor(tunnel.jdbcHost, tunnel.jdbcPort) +
                            "&rewriteBatchedStatements=true&useServerPrepStmts=false",
                        config.username,
                        config.password,
                        config.cdcSoftDelete,
                    )
                config.loadAsJson -> {
                    // Compress only when requested AND the detected version supports request-body
                    // compression (>= 3.3.2); `check` already fails fast otherwise.
                    val compression =
                        if (
                            LoadCompression.isEnabled(config.compression) &&
                                capabilities.compression
                        ) {
                            config.compression
                        } else {
                            null
                        }
                    JsonRowInsertBuffer(
                        tableName,
                        columns,
                        cdcDelete,
                        streamLoadClient,
                        config.cdcSoftDelete,
                        compression = compression,
                    )
                }
                else ->
                    CsvRowInsertBuffer(
                        tableName,
                        columns,
                        cdcDelete,
                        streamLoadClient,
                        config.cdcSoftDelete
                    )
            }
        return StarrocksAggregate(buffer)
    }

    companion object {
        private val META_COLUMNS =
            listOf(
                COLUMN_NAME_AB_RAW_ID,
                COLUMN_NAME_AB_EXTRACTED_AT,
                COLUMN_NAME_AB_META,
                COLUMN_NAME_AB_GENERATION_ID,
            )

        /**
         * Final column order for the CSV/`columns` header: Airbyte meta columns then user columns.
         */
        fun finalColumns(stream: DestinationStream): List<String> =
            META_COLUMNS + stream.tableSchema.columnSchema.finalSchema.keys

        /** True only for Dedupe streams whose final schema carries the CDC deleted-at column. */
        fun cdcDeleteEnabled(stream: DestinationStream): Boolean =
            stream.tableSchema.importType is Dedupe &&
                stream.tableSchema.columnSchema.finalSchema.containsKey(CDC_DELETED_AT_COLUMN)

        /**
         * PRIMARY KEY columns for a Dedupe stream (for the SQL CDC `DELETE` predicate); else empty.
         */
        fun primaryKeyColumns(stream: DestinationStream): List<String> =
            (stream.tableSchema.importType as? Dedupe)?.primaryKey?.map { it.single() }
                ?: emptyList()

        /**
         * True when the Stream Load CDC delete path would collide with a user column named `__op`.
         * That path appends an `__op` column (reserved in StarRocks >= 3.3.6) for load-time
         * delete/upsert; a source column of the same name corrupts the load (#45). The SQL load
         * path uses INSERT/DELETE (no `__op`), so the collision only applies when NOT loading via
         * SQL.
         */
        fun opColumnCollides(
            cdcDelete: Boolean,
            loadAsSql: Boolean,
            finalColumnNames: Set<String>,
        ): Boolean = cdcDelete && !loadAsSql && CsvRowInsertBuffer.OP_COLUMN in finalColumnNames
    }
}
