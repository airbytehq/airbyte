/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergRecord
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.EnrichedDestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigDecimal
import java.math.BigInteger
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
     * Converts an Airbyte [EnrichedDestinationRecordAirbyteValue] into an Iceberg [Record]. The
     * converted record will be wrapped to include [Operation] information, which is used by the
     * writer to determine how to write the data to the underlying Iceberg files.
     *
     * @param record The Airbyte [EnrichedDestinationRecordAirbyteValue] record to be converted for
     * writing by Iceberg.
     * @param stream The Airbyte [DestinationStream] that contains information about the stream.
     * @param tableSchema The Iceberg [Table] [Schema].
     * @return An Iceberg [Record] representation of the [EnrichedDestinationRecordAirbyteValue].
     */
    fun toRecord(
        record: EnrichedDestinationRecordAirbyteValue,
        stream: DestinationStream,
        tableSchema: Schema,
    ): Record {
        record.declaredFields.forEach { (_, value) ->
            value.transformValueRecursingIntoArrays { element, elementType ->
                when (elementType) {
                    // Convert complex types to string
                    // (note that schemaless arrays are stringified, but schematized arrays are not)
                    ArrayTypeWithoutSchema,
                    is ObjectType,
                    ObjectTypeWithEmptySchema,
                    ObjectTypeWithoutSchema,
                    is UnionType,
                    is UnknownType ->
                        // serializing to string is a non-lossy operation, so don't generate a
                        // Meta.Change object.
                        ChangedValue(
                            StringValue(element.serializeToString()),
                            changeDescription = null
                        )

                    // Null out numeric values that exceed int64/float64
                    is NumberType -> nullOutOfRangeNumber(element)
                    is IntegerType -> nullOutOfRangeInt(element)

                    // otherwise, don't change anything
                    else -> null
                }
            }
        }

        return RecordWrapper(
            delegate = record.allTypedFields.toIcebergRecord(tableSchema),
            operation = getOperation(record = record, importType = stream.importType)
        )
    }

    private fun nullOutOfRangeInt(numberValue: AirbyteValue): ChangedValue? {
        return if (
            BigInteger.valueOf(Long.MIN_VALUE) <= (numberValue as IntegerValue).value &&
                numberValue.value <= BigInteger.valueOf(Long.MAX_VALUE)
        ) {
            null
        } else {
            ChangedValue(
                NullValue,
                ChangeDescription(Change.NULLED, Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            )
        }
    }

    private fun nullOutOfRangeNumber(numberValue: AirbyteValue): ChangedValue? {
        return if (
            BigDecimal(Double.MIN_VALUE) <= (numberValue as NumberValue).value &&
                numberValue.value <= BigDecimal(Double.MAX_VALUE)
        ) {
            null
        } else {
            ChangedValue(
                NullValue,
                ChangeDescription(Change.NULLED, Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            )
        }
    }

    fun toIcebergSchema(stream: DestinationStream): Schema {
        val primaryKeys =
            when (stream.importType) {
                is Dedupe -> (stream.importType as Dedupe).primaryKey
                else -> emptyList()
            }
        return stream.schema.withAirbyteMeta(true).toIcebergSchema(primaryKeys)
    }

    private fun getSortOrder(schema: Schema): SortOrder {
        val builder = SortOrder.builderFor(schema)
        schema.identifierFieldNames().forEach { builder.asc(it) }
        return builder.build()
    }

    private fun getOperation(
        record: EnrichedDestinationRecordAirbyteValue,
        importType: ImportType,
    ): Operation =
        if (
            record.declaredFields[AIRBYTE_CDC_DELETE_COLUMN] != null &&
                record.declaredFields[AIRBYTE_CDC_DELETE_COLUMN]!!.value !is NullValue
        ) {
            Operation.DELETE
        } else if (importType is Dedupe) {
            Operation.UPDATE
        } else {
            Operation.INSERT
        }
}

/**
 * Our Airbyte<>Iceberg schema conversion generates strongly-typed arrays.
 *
 * This function applies a function to every non-array-typed value, recursing into arrays as needed.
 * [transformer] may assume that the AirbyteValue is a valid value for the AirbyteType. For example,
 * if [transformer] is called with a [NumberType], it is safe to cast the value to [NumberValue].
 */
fun EnrichedAirbyteValue.transformValueRecursingIntoArrays(
    transformer: (AirbyteValue, AirbyteType) -> ChangedValue?
) {
    /**
     * Recurse through ArrayValues, until we find a non-ArrayType field, coercing to ArrayValue as
     * needed, then apply [transformer]. If [transformer] returns a [ChangedValue], modify the
     * original ArrayValue's element (and populate [EnrichedAirbyteValue.changes] if needed).
     */
    fun recurseArray(
        currentValue: AirbyteValue,
        currentType: AirbyteType,
        path: String,
    ): AirbyteValue {
        if (currentValue == NullValue) {
            return NullValue
        } else if (currentType is ArrayType) {
            // If the type is another array, we recurse deeper.
            val coercedArray = AirbyteValueCoercer.coerceArray(currentValue)
            if (coercedArray == null) {
                changes.add(
                    Meta.Change(path, Change.NULLED, Reason.DESTINATION_SERIALIZATION_ERROR),
                )
                return NullValue
            }
            return ArrayValue(
                coercedArray.values.mapIndexed { index, element ->
                    val newPath = "$path.$index"
                    recurseArray(element, currentType.items.type, newPath)
                }
            )
        } else {
            // If we're at a leaf node, call the transformer.
            val transformedValue = transformer(currentValue, currentType) ?: return currentValue
            val (newValue, changeDescription) = transformedValue
            changeDescription?.let { (change, reason) ->
                changes.add(Meta.Change(path, change, reason))
            }
            return newValue
        }
    }

    value = recurseArray(value, type, name)
}

data class ChangeDescription(val change: Change, val reason: Reason)

data class ChangedValue(val newValue: AirbyteValue, val changeDescription: ChangeDescription?)
