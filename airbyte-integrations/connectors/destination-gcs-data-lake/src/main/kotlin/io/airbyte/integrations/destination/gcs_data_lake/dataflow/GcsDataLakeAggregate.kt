/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.dataflow

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.Operation
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter
import java.math.BigInteger
import java.time.ZoneOffset

private val logger = KotlinLogging.logger {}

class GcsDataLakeAggregate(
    private val stream: DestinationStream,
    private val table: Table,
    private val schema: Schema,
    private val stagingBranchName: String,
    private val writer: BaseTaskWriter<Record>,
) : Aggregate {
    companion object {
        val commitLock: Any = Any()
    }

    override fun accept(record: RecordDTO) {
        // Use toolkit's AirbyteValueToIcebergRecord converter directly
        val converter = io.airbyte.cdk.load.data.iceberg.parquet.AirbyteValueToIcebergRecord()
        val icebergRecord = org.apache.iceberg.data.GenericRecord.create(schema)

        schema.asStruct().fields().forEach { field ->
            val airbyteValue = record.fields[field.name()]
            if (airbyteValue != null) {
                // Coerce TimestampValue to IntegerValue for fields with LONG type
                // This handles _airbyte_extracted_at which is timestamp-as-milliseconds
                val coercedValue = if (field.type().typeId() == org.apache.iceberg.types.Type.TypeID.LONG &&
                    (airbyteValue is TimestampWithTimezoneValue || airbyteValue is TimestampWithoutTimezoneValue)) {
                    // Convert timestamp to milliseconds since epoch
                    val millis = when (airbyteValue) {
                        is TimestampWithTimezoneValue -> airbyteValue.value.toInstant().toEpochMilli()
                        is TimestampWithoutTimezoneValue -> airbyteValue.value.atOffset(ZoneOffset.UTC).toInstant().toEpochMilli()
                        else -> 0L
                    }
                    IntegerValue(BigInteger.valueOf(millis))
                } else {
                    airbyteValue
                }

                val convertedValue = converter.convert(coercedValue, field.type())
                icebergRecord.setField(field.name(), convertedValue)
            }
        }

        val wrappedRecord = RecordWrapper(
            delegate = icebergRecord,
            operation = Operation.INSERT
        )
        writer.write(wrappedRecord)
    }

    override suspend fun flush() {
        logger.info { "Flushing aggregate to staging branch $stagingBranchName for stream ${stream.mappedDescriptor}" }

        val writeResult = writer.complete()

        if (writeResult.deleteFiles().isNotEmpty()) {
            // Use row delta for updates/deletes (APPEND_DEDUP mode)
            val delta = table.newRowDelta().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { delta.addRows(it) }
            writeResult.deleteFiles().forEach { delta.addDeletes(it) }
            synchronized(commitLock) { delta.commit() }
        } else {
            // Use append for simple appends
            val append = table.newAppend().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { append.appendFile(it) }
            synchronized(commitLock) { append.commit() }
        }

        logger.info { "Flushed records to staging branch $stagingBranchName" }
    }
}
