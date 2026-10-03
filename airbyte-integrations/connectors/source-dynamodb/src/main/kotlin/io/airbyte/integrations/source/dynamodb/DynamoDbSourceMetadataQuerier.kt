/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.Operation
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
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
import java.util.concurrent.atomic.AtomicBoolean
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.DescribeTableRequest
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException
import software.amazon.awssdk.services.dynamodb.model.KeyType
import software.amazon.awssdk.services.dynamodb.model.ListTablesRequest
import software.amazon.awssdk.services.dynamodb.model.ListTablesResponse
import software.amazon.awssdk.services.dynamodb.model.ScanRequest
import software.amazon.awssdk.services.dynamodb.model.ScanResponse
import software.amazon.awssdk.services.dynamodb.model.TableDescription

private val log = KotlinLogging.logger {}

/**
 * DynamoDB implementation of [MetadataQuerier].
 *
 * There are no namespaces: the streams are the tables of the account and region the credentials
 * give access to. Fields are discovered by sampling items, the same way the legacy
 * `source-dynamodb` connector did.
 */
class DynamoDbSourceMetadataQuerier(
    val configuration: DynamoDbSourceConfiguration,
    val client: DynamoDbClient,
    /**
     * When true, [fields] returns an empty list without sampling. CHECK only calls [fields] to
     * probe that a stream is queryable; the legacy connector's `check` was a bare `ListTables`.
     */
    private val skipFieldDiscovery: Boolean = false,
    /**
     * Fields to serve from [fields] instead of sampling, keyed by stream. READ validates the
     * configured catalog against [fields] at start-up (`StateManagerFactory`): sampling again would
     * drop a stream whenever a configured attribute happens to be missing from the new sample, so
     * during READ the fields are the configured stream's own properties.
     */
    private val configuredFields: Map<StreamIdentifier, List<EmittedField>> = emptyMap(),
) : MetadataQuerier {

    private val tableNames: List<String> by lazy { listTables() }
    private val tableDescriptions = ConcurrentHashMap<String, TableDescription>()

    /** Tables are sampled concurrently; DISCOVER itself calls [fields] one stream at a time. */
    private val executorDelegate: Lazy<ExecutorService> = lazy {
        Executors.newFixedThreadPool(DISCOVER_PARALLELISM)
    }
    private val executor: ExecutorService by executorDelegate
    private val fieldsByStream = ConcurrentHashMap<StreamIdentifier, Future<List<EmittedField>>>()
    private val prefetched = AtomicBoolean(false)

    override fun streamNamespaces(): List<String> = emptyList()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        if (streamNamespace != null) {
            return emptyList()
        }
        return tableNames.map { tableName: String ->
            StreamIdentifier.from(StreamDescriptor().withName(tableName))
        }
    }

    /** All table names, following `LastEvaluatedTableName` (100 tables per page). */
    fun listTables(): List<String> {
        val names = ArrayList<String>()
        var request: ListTablesRequest = ListTablesRequest.builder().build()
        while (true) {
            val response: ListTablesResponse = client.listTables(request)
            names.addAll(response.tableNames())
            val last: String = response.lastEvaluatedTableName() ?: break
            request = request.toBuilder().exclusiveStartTableName(last).build()
        }
        return names
    }

    /**
     * Fields of the table, discovered by sampling its items; empty for an empty table, which
     * DISCOVER then omits from the catalog.
     *
     * The first call schedules the sampling of every table so that DISCOVER, which calls this
     * method once per stream, runs them concurrently.
     */
    override fun fields(streamID: StreamIdentifier): List<EmittedField> {
        if (skipFieldDiscovery) {
            return emptyList()
        }
        configuredFields[streamID]?.let {
            return it
        }
        if (prefetched.compareAndSet(false, true)) {
            for (otherStreamID in streamNames(null)) {
                scheduleFieldDiscovery(otherStreamID)
            }
        }
        return try {
            scheduleFieldDiscovery(streamID).get()
        } catch (e: ExecutionException) {
            throw e.cause ?: e
        }
    }

    private fun scheduleFieldDiscovery(streamID: StreamIdentifier): Future<List<EmittedField>> =
        fieldsByStream.computeIfAbsent(streamID) {
            executor.submit(Callable { discoverFields(it) })
        }

    /**
     * Samples the table and maps the union of the top-level attributes to [DynamoDbFieldType]s.
     *
     * Like the legacy connector, a table whose `Scan` is denied is skipped (no fields, so DISCOVER
     * drops the stream) when `ignore_missing_read_permissions_tables` is set; the check is on the
     * message because the service reports a missing permission as a generic `DynamoDbException`.
     */
    internal fun discoverFields(streamID: StreamIdentifier): List<EmittedField> {
        val items: List<Map<String, AttributeValue>> =
            try {
                sampleItems(streamID.name)
            } catch (e: DynamoDbException) {
                if (
                    configuration.ignoreMissingReadPermissionsTables &&
                        e.message?.contains(NOT_AUTHORIZED) == true
                ) {
                    log.warn(e) {
                        "Connector doesn't have READ access for the table ${streamID.name}"
                    }
                    return emptyList()
                }
                throw e
            }
        // Same merge as the legacy connector: top-level attributes only, later items override
        // earlier ones when an attribute appears with different types.
        val merged = LinkedHashMap<String, AttributeValue>()
        for (item in items) {
            merged.putAll(item)
        }
        return merged.mapNotNull { (name: String, value: AttributeValue) ->
            DynamoDbFieldType.of(value)?.let { EmittedField(name, it) }
        }
    }

    /**
     * Reads up to `discover_sample_size` items, one page of that size at a time; a page is never
     * cut short, so slightly more items may be returned when a page is smaller than 1 MB but the
     * previous ones were not (same behavior as the legacy connector, which always sampled 1000).
     */
    private fun sampleItems(tableName: String): List<Map<String, AttributeValue>> {
        val sampleSize: Int = configuration.discoverSampleSize
        val request: ScanRequest =
            ScanRequest.builder().tableName(tableName).limit(sampleSize).build()
        val items = ArrayList<Map<String, AttributeValue>>()
        var scanned = 0
        for (page: ScanResponse in client.scanPaginator(request)) {
            if (scanned >= sampleSize) {
                break
            }
            scanned += page.count()
            items.addAll(page.items())
        }
        return items
    }

    /**
     * The table's partition (HASH) key only. The legacy connector left the sort (RANGE) key out of
     * the primary key; kept for catalog parity.
     */
    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> {
        val hashKeys: List<String> =
            describeTable(streamID.name)
                .keySchema()
                .filter { it.keyType() == KeyType.HASH }
                .map { it.attributeName() }
        return listOf(hashKeys)
    }

    fun describeTable(tableName: String): TableDescription =
        tableDescriptions.computeIfAbsent(tableName) {
            client.describeTable(DescribeTableRequest.builder().tableName(it).build()).table()
        }

    /** The legacy `check` was `ListTables` only, which [streamNames] already ran. */
    override fun extraChecks() {}

    override fun close() {
        if (executorDelegate.isInitialized()) {
            executor.shutdownNow()
        }
        client.close()
    }

    /** DynamoDB implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory
    @Inject
    constructor(
        @Value("\${${Operation.PROPERTY}:discover}") private val operation: String = "discover",
        /** Empty for every operation but READ. */
        private val configuredCatalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog(),
    ) : MetadataQuerier.Factory<DynamoDbSourceConfiguration> {
        /**
         * The [DynamoDbSourceConfiguration] is deliberately not injected in order to support tests.
         */
        override fun session(config: DynamoDbSourceConfiguration): MetadataQuerier =
            DynamoDbSourceMetadataQuerier(
                config,
                DynamoDbClientFactory.create(config),
                skipFieldDiscovery = operation == CHECK_OPERATION,
                configuredFields =
                    if (operation == READ_OPERATION) fieldsFromConfiguredCatalog(configuredCatalog)
                    else emptyMap(),
            )
    }

    companion object {
        private const val CHECK_OPERATION = "check"
        private const val READ_OPERATION = "read"

        /**
         * The fields of each configured stream, taken from its JSON schema: one [DynamoDbFieldType]
         * per property, carrying the property's own schema.
         */
        fun fieldsFromConfiguredCatalog(
            configuredCatalog: ConfiguredAirbyteCatalog,
        ): Map<StreamIdentifier, List<EmittedField>> =
            configuredCatalog.streams.associate { configuredStream: ConfiguredAirbyteStream ->
                val properties: JsonNode? = configuredStream.stream.jsonSchema?.get("properties")
                val fields: List<EmittedField> =
                    properties?.properties()?.map { (name: String, schema: JsonNode) ->
                        EmittedField(
                            name,
                            DynamoDbFieldType.fromJsonSchema(
                                schema as? ObjectNode ?: Jsons.objectNode()
                            ),
                        )
                    }
                        ?: emptyList()
                StreamIdentifier.from(configuredStream.stream) to fields
            }
        /**
         * Fragment of the service's AccessDeniedException message, as matched by the legacy
         * connector.
         */
        const val NOT_AUTHORIZED = "not authorized"

        /**
         * Bounded so that discovery does not consume the read capacity of many tables at once; the
         * legacy connector sampled tables sequentially.
         */
        const val DISCOVER_PARALLELISM = 4
    }
}
