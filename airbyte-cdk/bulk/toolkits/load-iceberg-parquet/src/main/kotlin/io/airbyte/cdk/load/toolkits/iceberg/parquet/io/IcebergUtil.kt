/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergRecord
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.inject.Singleton
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.SortOrder
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties.DEFAULT_FILE_FORMAT
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.SupportsNamespaces
import org.apache.iceberg.data.Record
import org.apache.iceberg.exceptions.AlreadyExistsException

private val logger = KotlinLogging.logger {}

const val AIRBYTE_CDC_DELETE_COLUMN = "_ab_cdc_deleted_at"

@Singleton
class IcebergUtil(private val tableIdGenerator: TableIdGenerator) {
    class InvalidFormatException(message: String) : Exception(message)

    private val generationIdRegex = Regex("""ab-generation-id-\d+-e""")

    fun assertGenerationIdSuffixIsOfValidFormat(generationId: String) {
        if (!generationIdRegex.matches(generationId)) {
            throw InvalidFormatException(
                "Invalid format: $generationId. Expected format is 'ab-generation-id-<number>-e'",
            )
        }
    }

    fun constructGenerationIdSuffix(stream: DestinationStream): String {
        return constructGenerationIdSuffix(stream.generationId)
    }

    fun constructGenerationIdSuffix(generationId: Long): String {
        if (generationId < 0) {
            throw IllegalArgumentException(
                "GenerationId must be non-negative. Provided: $generationId",
            )
        }
        return "ab-generation-id-${generationId}-e"
    }
    /**
     * Builds an Iceberg [Catalog].
     *
     * @param catalogName The name of the catalog.
     * @param properties The map of catalog configuration properties.
     * @return The configured Iceberg [Catalog].
     */
    fun createCatalog(catalogName: String, properties: Map<String, String>): Catalog {
        return CatalogUtil.buildIcebergCatalog(catalogName, properties, Configuration())
    }

    /** Create the namespace if it doesn't already exist. */
    fun createNamespace(streamDescriptor: DestinationStream.Descriptor, catalog: Catalog) {
        val tableIdentifier = tableIdGenerator.toTableIdentifier(streamDescriptor)
        synchronized(tableIdentifier.namespace()) {
            if (
                catalog is SupportsNamespaces &&
                    !catalog.namespaceExists(tableIdentifier.namespace())
            ) {
                try {
                    catalog.createNamespace(tableIdentifier.namespace())
                    logger.info { "Created namespace '${tableIdentifier.namespace()}'." }
                } catch (e: AlreadyExistsException) {
                    // This exception occurs when multiple threads attempt to write to the same
                    // namespace in parallel.
                    // One thread may create the namespace successfully, causing the other threads
                    // to encounter this exception
                    // when they also try to create the namespace.
                    logger.info {
                        "Namespace '${tableIdentifier.namespace()}' was likely created by another thread during parallel operations."
                    }
                }
            }
        }
    }

    /**
     * Builds (if necessary) an Iceberg [Table]. This includes creating the table's namespace if it
     * does not already exist. If the [Table] already exists, it is loaded from the [Catalog].
     *
     * @param streamDescriptor The [DestinationStream.Descriptor] that contains the Airbyte stream's
     * namespace and name.
     * @param catalog The Iceberg [Catalog] that contains the [Table] or should contain it once
     * created.
     * @param schema The Iceberg [Schema] associated with the [Table].
     * @param properties The [Table] configuration properties derived from the [Catalog].
     * @return The Iceberg [Table], created if it does not yet exist.
     */
    fun createTable(
        streamDescriptor: DestinationStream.Descriptor,
        catalog: Catalog,
        schema: Schema,
        properties: Map<String, String>
    ): Table {
        val tableIdentifier = tableIdGenerator.toTableIdentifier(streamDescriptor)
        return if (!catalog.tableExists(tableIdentifier)) {
            logger.info { "Creating Iceberg table '$tableIdentifier'...." }
            catalog
                .buildTable(tableIdentifier, schema)
                .withProperties(properties)
                .withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase())
                .withSortOrder(getSortOrder(schema = schema))
                .create()
        } else {
            logger.info { "Loading Iceberg table $tableIdentifier ..." }
            catalog.loadTable(tableIdentifier)
        }
    }

    /**
     * Converts an Airbyte [DestinationRecordAirbyteValue] into an Iceberg [Record]. The converted
     * record will be wrapped to include [Operation] information, which is used by the writer to
     * determine how to write the data to the underlying Iceberg files.
     *
     * @param record The Airbyte [DestinationRecordAirbyteValue] record to be converted for writing
     * by Iceberg.
     * @param stream The Airbyte [DestinationStream] that contains information about the stream.
     * @param tableSchema The Iceberg [Table] [Schema].
     * @param pipeline The [MapperPipeline] used to convert the Airbyte record to an Iceberg record.
     * @return An Iceberg [Record] representation of the Airbyte [DestinationRecordAirbyteValue].
     */
    fun toRecord(
        record: DestinationRecordAirbyteValue,
        stream: DestinationStream,
        tableSchema: Schema,
        pipeline: MapperPipeline
    ): Record {
        val dataMapped =
            pipeline
                .map(record.data, record.meta?.changes)
                .withAirbyteMeta(stream, record.emittedAtMs, true)
        // TODO figure out how to detect the actual operation value
        return RecordWrapper(
            delegate = dataMapped.toIcebergRecord(tableSchema),
            operation = getOperation(record = record, importType = stream.importType)
        )
    }

    fun toIcebergSchema(stream: DestinationStream, pipeline: MapperPipeline): Schema {
        val primaryKeys =
            when (stream.importType) {
                is Dedupe -> (stream.importType as Dedupe).primaryKey
                else -> emptyList()
            }
        return pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(primaryKeys)
    }

    private fun getSortOrder(schema: Schema): SortOrder {
        val builder = SortOrder.builderFor(schema)
        schema.identifierFieldNames().forEach { builder.asc(it) }
        return builder.build()
    }

    private fun getOperation(
        record: DestinationRecordAirbyteValue,
        importType: ImportType,
    ): Operation =
        if (
            record.data is ObjectValue &&
                (record.data as ObjectValue).values[AIRBYTE_CDC_DELETE_COLUMN] != null &&
                (record.data as ObjectValue).values[AIRBYTE_CDC_DELETE_COLUMN] !is NullValue
        ) {
            Operation.DELETE
        } else if (importType is Dedupe) {
            Operation.UPDATE
        } else {
            Operation.INSERT
        }
}
