/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.DatasetId
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.Table
import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableInfo
import io.airbyte.cdk.Operation
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.concurrent.Callable
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ExecutionException
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.Future

private val log = KotlinLogging.logger {}

/**
 * BigQuery implementation of [MetadataQuerier].
 *
 * Namespaces are datasets and streams are the tables, views, materialized views, external tables
 * and snapshots they contain, like the legacy `source-bigquery` connector. Metadata is read with
 * the native BigQuery API (`datasets.list`, `tables.list`, `tables.get`) rather than through the
 * JDBC driver's `DatabaseMetaData`: the `tables.get` response is the only source of the nested
 * schema of `STRUCT`/`ARRAY` columns and of the primary key constraints. Each `tables.get` response
 * is reduced to a [TableMetadata] as soon as it arrives, so the per-operation cache stays
 * proportional to the catalog rather than to the size of the API objects. The JDBC connection of
 * [base] is used for the `check` queries and, later, for reading.
 */
class BigQuerySourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
    val bigquery: BigQuery,
    val config: BigQuerySourceConfiguration,
    /**
     * When true, the first [fields] call for a dataset fetches the metadata of all its tables
     * concurrently, since DISCOVER calls [fields] for each of them in turn. CHECK only needs one.
     */
    private val prefetchNamespaces: Boolean = true,
    /** Receives the type (table, view, ...) of every fetched table, for the query generator. */
    private val tableTypes: BigQueryTableTypes = BigQueryTableTypes(),
) : MetadataQuerier {

    private val executorDelegate: Lazy<ExecutorService> = lazy {
        Executors.newFixedThreadPool(METADATA_FETCH_PARALLELISM)
    }
    private val executor: ExecutorService by executorDelegate
    private val metadataByStream = ConcurrentHashMap<StreamIdentifier, Future<TableMetadata?>>()
    private val prefetchedNamespaces: MutableSet<String> = ConcurrentHashMap.newKeySet()
    private val streamNamesByNamespace = ConcurrentHashMap<String, List<StreamIdentifier>>()

    private val datasets: List<String> by lazy {
        if (config.namespaces.isNotEmpty()) {
            config.namespaces.toList()
        } else {
            bigquery
                .listDatasets(config.projectId)
                .iterateAll()
                .map { it.datasetId.dataset }
                .sorted()
        }
    }

    override fun streamNamespaces(): List<String> = datasets

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        if (streamNamespace == null) {
            return emptyList()
        }
        return streamNamesByNamespace.computeIfAbsent(streamNamespace) { dataset: String ->
            bigquery
                .listTables(DatasetId.of(config.projectId, dataset))
                .iterateAll()
                .filter { isSupportedTable(it) }
                .map { it.tableId.table }
                .sorted()
                .map { tableName: String ->
                    StreamIdentifier.from(
                        StreamDescriptor().withName(tableName).withNamespace(dataset)
                    )
                }
        }
    }

    /**
     * Top-level columns of the table, mapped with [BigQueryFieldTypes.fromField]. Empty when the
     * table has no schema (which DISCOVER then omits from the catalog).
     */
    override fun fields(streamID: StreamIdentifier): List<EmittedField> {
        val namespace: String = streamID.namespace ?: return emptyList()
        if (prefetchNamespaces && prefetchedNamespaces.add(namespace)) {
            for (otherStreamID in streamNames(namespace)) {
                scheduleTableFetch(otherStreamID)
            }
        }
        return metadata(streamID)?.fields ?: emptyList()
    }

    /** Columns of the (unenforced) `PRIMARY KEY` constraint, if the table declares one. */
    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> =
        metadata(streamID)?.primaryKey ?: emptyList()

    override fun extraChecks() {
        base.extraChecks()
    }

    override fun close() {
        if (executorDelegate.isInitialized()) {
            executor.shutdownNow()
        }
        base.close()
    }

    private fun metadata(streamID: StreamIdentifier): TableMetadata? =
        try {
            scheduleTableFetch(streamID).get()
        } catch (e: ExecutionException) {
            throw e.cause ?: e
        }

    private fun scheduleTableFetch(streamID: StreamIdentifier): Future<TableMetadata?> =
        metadataByStream.computeIfAbsent(streamID) {
            executor.submit(Callable { fetchTableMetadata(it) })
        }

    /**
     * `tables.get`, which returns the full schema (`tables.list` only returns partial objects),
     * reduced right away to what discovery needs. Null when the table no longer exists.
     */
    internal fun fetchTableMetadata(streamID: StreamIdentifier): TableMetadata? {
        val tableId = TableId.of(config.projectId, streamID.namespace, streamID.name)
        log.info { "Fetching metadata of table $tableId." }
        val table: Table = bigquery.getTable(tableId) ?: return null
        val metadata: TableMetadata = TableMetadata.from(table)
        tableTypes.register(
            streamID,
            BigQueryTableTypes.TableFacts(metadata.type, metadata.numBytes, metadata.numRows),
        )
        return metadata
    }

    /**
     * What discovery keeps of a `tables.get` response, cached per stream for the whole operation.
     *
     * A full [Table] weighs tens of KiB (every column's description and policy tags, labels, ETag,
     * self link, ...): caching one per stream measured 1.4 GiB at 31k tables on a project
     * discovered without a `dataset_id`. The columns and the primary key are all that [fields] and
     * [primaryKey] return, and the table type has already gone to [BigQueryTableTypes].
     */
    internal data class TableMetadata(
        val fields: List<EmittedField>,
        val primaryKey: List<List<String>>,
        /** Table, view, external table, ...; what the partition creators key their choices on. */
        val type: TableDefinition.Type? = null,
        /** Logical size in bytes, as reported by `tables.get` (null for views). */
        val numBytes: Long? = null,
        /** Row count, as reported by `tables.get` (null for views). */
        val numRows: Long? = null,
    ) {
        companion object {
            fun from(table: TableInfo): TableMetadata {
                val definition: TableDefinition = table.getDefinition<TableDefinition>()
                val schemaFields: List<Field> = definition.schema?.fields ?: emptyList()
                val primaryKeyColumns: List<String> =
                    table.tableConstraints?.primaryKey?.columns ?: emptyList()
                return TableMetadata(
                    fields =
                        schemaFields.map {
                            EmittedField(it.name, BigQueryFieldTypes.fromField(it))
                        },
                    primaryKey = primaryKeyColumns.map { listOf(it) },
                    type = definition.type,
                    numBytes = table.numBytes,
                    numRows = table.numRows?.toLong(),
                )
            }
        }
    }

    /** BigQuery implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory
    @Inject
    constructor(
        val constants: DefaultJdbcConstants,
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
        val checkQueries: JdbcCheckQueries,
        val tableTypes: BigQueryTableTypes,
        @Value("\${${Operation.PROPERTY}:discover}") private val operation: String = "discover",
    ) : MetadataQuerier.Factory<BigQuerySourceConfiguration> {
        /**
         * The [BigQuerySourceConfiguration] is deliberately not injected in order to support tests.
         */
        override fun session(config: BigQuerySourceConfiguration): MetadataQuerier {
            val base =
                JdbcMetadataQuerier(
                    constants,
                    config,
                    selectQueryGenerator,
                    fieldTypeMapper,
                    checkQueries,
                    JdbcConnectionFactory(config),
                )
            return BigQuerySourceMetadataQuerier(
                base,
                BigQueryClientFactory.create(config),
                config,
                prefetchNamespaces = operation != CHECK_OPERATION,
                tableTypes = tableTypes,
            )
        }
    }

    companion object {
        private const val CHECK_OPERATION = "check"

        /** Same default as the JDBC driver's `MetaDataFetchThreadCount`. */
        const val METADATA_FETCH_PARALLELISM = 32

        /** Everything `tables.list` returns can be queried with SELECT, except ML models. */
        fun isSupportedTable(table: Table): Boolean =
            table.getDefinition<TableDefinition>().type != TableDefinition.Type.MODEL
    }
}
