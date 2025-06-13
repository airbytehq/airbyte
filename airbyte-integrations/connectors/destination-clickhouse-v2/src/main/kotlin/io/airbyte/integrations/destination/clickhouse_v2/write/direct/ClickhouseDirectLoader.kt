/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.RowBinaryFormatWriter
import com.clickhouse.data.ClickHouseFormat
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.config.ClickhouseColumnNameGenerator
import io.airbyte.integrations.destination.clickhouse_v2.config.ClickhouseFinalTableNameGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import kotlinx.coroutines.future.await

private val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class ClickhouseDirectLoader(
    private val descriptor: DestinationStream.Descriptor,
    private val clickhouseClient: Client,
    private val columnMapper: ClickhouseColumnNameGenerator,
    tableNameResolver: ClickhouseFinalTableNameGenerator,
) : DirectLoader {
    // Initialize the buffer
    private val tableName = tableNameResolver.getTableName(descriptor)
    private val buffer = InputOutputBuffer()
    private val schema = clickhouseClient.getTableSchema(tableName.name, tableName.namespace)
    private val writer = RowBinaryFormatWriter(buffer, schema, ClickHouseFormat.RowBinary)
    // the sum of serialized json bytes we've accumulated
    private var jsonBytesProcessed = 0L

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        // accumulate the record
        accumulateRecord(record)
        jsonBytesProcessed += record.serializedSizeBytes

        // determine whether we're complete
        if (writer.rowCount >= Constants.MAX_BATCH_SIZE_RECORDS || jsonBytesProcessed >= Constants.MAX_BATCH_SIZE_BYTES) {
            // upload
            flush()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
    }

    // only calls this on force complete
    override suspend fun finish() {
        flush()
    }

    // this is always called on complete
    override fun close() {}

    private fun writeAirbyteValue(columnName: String, abValue: AirbyteValue) {
        when (abValue) {
            is NullValue -> writer.setValue(columnName, null)
            is ObjectValue -> writer.setValue(columnName, abValue.values.serializeToString())
            is ArrayValue -> writer.setValue(columnName, abValue.values.serializeToString())
            is BooleanValue -> writer.setValue(columnName, abValue.value)
            is IntegerValue -> writer.setValue(columnName, abValue.value)
            is NumberValue -> writer.setValue(columnName, abValue.value)
            is StringValue -> writer.setValue(columnName, abValue.value)
            is DateValue -> writer.setValue(columnName, abValue.value)
            is TimeWithTimezoneValue -> writer.setValue(columnName, abValue.value)
            is TimeWithoutTimezoneValue -> writer.setValue(columnName, abValue.value)
            is TimestampWithTimezoneValue -> writer.setValue(columnName, abValue.value)
            is TimestampWithoutTimezoneValue -> writer.setValue(columnName, abValue.value)
        }
    }

    private fun accumulateRecord(record: DestinationRecordRaw) {
        // coerces and munges record to schema, adding any changes to the meta
        val enriched = record.asEnrichedDestinationRecordAirbyteValue(
            extractedAtAsTimestampWithTimezone = true
        )
        val cols = enriched.allTypedFields
        cols.forEach {
            val column = columnMapper.getColumnName(it.key)
            writeAirbyteValue(column.canonicalName, it.value.abValue)
        }

        writer.commitRow()
    }

    private suspend fun flush() {
        log.info { "Beginning insert into ${descriptor.name}" }

        val insertResult =
            clickhouseClient
                .insert(
                    "`${descriptor.namespace ?: "default"}`.`${descriptor.name}`",
                    buffer.toInputStream(),
                    ClickHouseFormat.RowBinary
                )
                .await()

        log.info { "Finished insert of ${insertResult.writtenRows} rows into ${descriptor.name}" }
    }

    object Constants {
        // CH recommends 10k-100k batch sizes — since we block on IO we aim on the high side
        // to amortize the overheads.
        const val MAX_BATCH_SIZE_RECORDS = 100000
        // To prevent undue backpressure, we try to cap the buffer size at something will safely fit
        // in the "reserved" memory, which in practice is ~180MB.
        const val MAX_BATCH_SIZE_BYTES = 70000000
    }

    /**
     * The CH writer wants an output stream and the client an input stream.
     * This is a naive wrapper class to avoid having to copy the buffer contents around.
     */
    private class InputOutputBuffer : ByteArrayOutputStream() {
        /**
         * Get an input stream based on the contents of this output stream.
         * Do not use the output stream after calling this method.
         * @return an {@link InputStream}
         */
        fun toInputStream(): InputStream {
            return ByteArrayInputStream(this.buf, 0, this.count);
        }
    }
}
