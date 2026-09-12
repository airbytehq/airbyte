/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.DatasetId
import com.google.cloud.bigquery.Table
import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TableId
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
 * schema of `STRUCT`/`ARRAY` columns and of the primary key constraints. The JDBC connection of
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
) : MetadataQuerier {

    private val executorDelegate: Lazy<ExecutorService> = lazy {
        Executors.newFixedThreadPool(METADATA_FETCH_PARALLELISM)
    }
    private val executor: ExecutorService by executorDelegate
    private val tablesByStream = ConcurrentHashMap<StreamIdentifier, Future<Table?>>()
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
        val table: Table = table(streamID) ?: return emptyList()
        val fields = table.getDefinition<TableDefinition>().schema?.fields ?: return emptyList()
        return fields.map { EmittedField(it.name, BigQueryFieldTypes.fromField(it)) }
    }

    /** Columns of the (unenforced) `PRIMARY KEY` constraint, if the table declares one. */
    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> {
        val table: Table = table(streamID) ?: return emptyList()
        val columns: List<String> =
            table.tableConstraints?.primaryKey?.columns ?: return emptyList()
        return columns.map { listOf(it) }
    }

    override fun extraChecks() {
        base.extraChecks()
    }

    override fun close() {
        if (executorDelegate.isInitialized()) {
            executor.shutdownNow()
        }
        base.close()
    }

    private fun table(streamID: StreamIdentifier): Table? =
        try {
            scheduleTableFetch(streamID).get()
        } catch (e: ExecutionException) {
            throw e.cause ?: e
        }

    private fun scheduleTableFetch(streamID: StreamIdentifier): Future<Table?> =
        tablesByStream.computeIfAbsent(streamID) { executor.submit(Callable { fetchTable(it) }) }

    /** `tables.get`, which returns the full schema (`tables.list` only returns partial objects). */
    internal fun fetchTable(streamID: StreamIdentifier): Table? {
        val tableId = TableId.of(config.projectId, streamID.namespace, streamID.name)
        log.info { "Fetching metadata of table $tableId." }
        return bigquery.getTable(tableId)
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
