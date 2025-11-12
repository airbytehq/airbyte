/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.dataflow

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.iceberg.parquet.AirbyteValueToIcebergRecord
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.Operation
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.airbyte.cdk.load.util.serializeToString
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigInteger
import java.time.ZoneOffset
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types

private val logger = KotlinLogging.logger {}

class GcsDataLakeAggregate(
    private val stream: DestinationStream,
    private val table: Table,
    private val schema: Schema,
    private val stagingBranchName: String,
    private val writer: BaseTaskWriter<Record>,
) : Aggregate {
    companion object {
        val converter = AirbyteValueToIcebergRecord()
    }

    private val operationType =
        if (stream.importType is Dedupe) {
            Operation.UPDATE
        } else {
            Operation.INSERT
        }

    // Cache schema fields to avoid repeated calls to schema.asStruct().fields()
    // which may create new collections on each invocation
    private val schemaFields = schema.asStruct().fields()

    // Pre-compute which fields need special transformations to avoid repeated type checks
    private val longFields =
        schemaFields.filter { it.type().typeId() == Type.TypeID.LONG }.map { it.name() }.toSet()
    private val stringFields =
        schemaFields.filter { it.type().typeId() == Type.TypeID.STRING }.map { it.name() }.toSet()

    override fun accept(record: RecordDTO) {
        // Convert RecordDTO to Iceberg Record
        // Note: ValueCoercer has already nulled out-of-range integers in Parse stage
        // Here we handle Iceberg-schema-specific conversions that depend on field types
        val icebergRecord = GenericRecord.create(schema)
        val recordFields = record.fields

        // Use cached schemaFields instead of calling schema.asStruct().fields() repeatedly
        schemaFields.forEach { field ->
            // Schema has mapped column names, record.fields also has mapped names
            val airbyteValue = recordFields[field.name()]
            if (airbyteValue != null) {
                // Apply Iceberg-schema-dependent transformations
                val transformedValue = transformForIcebergSchema(airbyteValue, field)
                val convertedValue = converter.convert(transformedValue, field.type())
                icebergRecord.setField(field.name(), convertedValue)
            }
        }

        val wrappedRecord = RecordWrapper(delegate = icebergRecord, operation = operationType)
        writer.write(wrappedRecord)
    }

    /**
     * Transform AirbyteValue based on Iceberg schema field type. These transformations require
     * knowledge of the Iceberg schema, so they can't happen in ValueCoercer (which operates in
     * Parse stage).
     *
     * Note: Union stringification is handled by ValueCoercer (during Parse stage). Here we only
     * handle Object/Array stringification for STRING fields.
     */
    private fun transformForIcebergSchema(
        value: AirbyteValue,
        field: Types.NestedField
    ): AirbyteValue {
        val fieldName = field.name()

        return when {
            // Timestamp → Integer for LONG fields (_airbyte_extracted_at)
            // Use cached set lookup instead of repeated typeId() calls
            fieldName in longFields &&
                (value is TimestampWithTimezoneValue || value is TimestampWithoutTimezoneValue) -> {
                val millis =
                    when (value) {
                        is TimestampWithTimezoneValue -> value.value.toInstant().toEpochMilli()
                        is TimestampWithoutTimezoneValue ->
                            value.value.atOffset(ZoneOffset.UTC).toInstant().toEpochMilli()
                        else -> 0L
                    }
                IntegerValue(BigInteger.valueOf(millis))
            }
            // Object/Array → String for STRING fields (for stringifySchemalessObjects behavior)
            // Note: Union values are already stringified by ValueCoercer
            // Use cached set lookup instead of repeated typeId() calls
            fieldName in stringFields && value is ObjectValue ->
                StringValue(value.serializeToString())
            fieldName in stringFields && value is ArrayValue ->
                StringValue(value.serializeToString())
            else -> value
        }
    }

    override suspend fun flush() {
        logger.info {
            "Flushing aggregate to staging branch $stagingBranchName for stream ${stream.mappedDescriptor}"
        }

        val writeResult = writer.complete()

        if (writeResult.deleteFiles().isNotEmpty()) {
            // Use row delta for updates/deletes (APPEND_DEDUP mode)
            val delta = table.newRowDelta().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { delta.addRows(it) }
            writeResult.deleteFiles().forEach { delta.addDeletes(it) }
            delta.commit()
        } else {
            // Use append for simple appends
            val append = table.newAppend().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { append.appendFile(it) }
            append.commit()
        }

        logger.info { "Flushed records to staging branch $stagingBranchName" }
    }
}
