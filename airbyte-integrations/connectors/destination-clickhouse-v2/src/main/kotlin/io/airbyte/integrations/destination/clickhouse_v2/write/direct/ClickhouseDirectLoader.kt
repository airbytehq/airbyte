/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.RowBinaryFormatWriter
import com.clickhouse.client.api.metadata.TableSchema
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
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.write.DirectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.time.Instant
import kotlinx.coroutines.future.await

private val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class ClickhouseDirectLoader(
    private val descriptor: DestinationStream.Descriptor,
    private val clickhouseClient: Client,
) : DirectLoader {
    private val buffer: ClickHouseBinaryBuffer = ClickHouseBinaryBuffer()
    private val schema: TableSchema = clickhouseClient.getTableSchema(descriptor.name, descriptor.namespace ?: "default")
    private val writer: RowBinaryFormatWriter = RowBinaryFormatWriter(buffer, schema, ClickHouseFormat.RowBinary)

    private fun writeAirbyteValue(key: String, abValue: AirbyteValue) {
            when (abValue) {
                is NullValue -> writer.setValue(key, null)
                is ObjectValue -> writer.setValue(key, abValue.values.toString())
                is ArrayValue -> writer.setValue(key, abValue.values.toString())
                is BooleanValue -> writer.setValue(key, abValue.value)
                is IntegerValue -> writer.setValue(key, abValue.value)
                is NumberValue -> writer.setValue(key, abValue.value)
                is StringValue -> writer.setValue(key, abValue.value)
                is DateValue -> writer.setValue(key, abValue.value)
                is TimeWithTimezoneValue -> writer.setValue(key, abValue.value)
                is TimeWithoutTimezoneValue -> writer.setValue(key, abValue.value)
                is TimestampWithTimezoneValue -> writer.setValue(key, abValue.value)
                is TimestampWithoutTimezoneValue -> writer.setValue(key, abValue.value)
            }
    }


    private fun accRow(record: DestinationRecordRaw) {
        // coerces and munges record to schema, adding any changes to the meta
        val enriched = record.asEnrichedDestinationRecordAirbyteValue()
        val cols = enriched.allTypedFields
        cols.filter { it.key != Meta.COLUMN_NAME_AB_EXTRACTED_AT }.forEach {
            when (val abValue = it.value.abValue) {

            }
        val extractedAt = Instant.ofEpochMilli(cols[Meta.COLUMN_NAME_AB_EXTRACTED_AT].abValue)
        writer.setValue(Meta.COLUMN_NAME_AB_EXTRACTED_AT, )

        writer.commitRow()
    }

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        accRow(record)

        // determine whether we're complete
        if (writer.rowCount >= Constants.BATCH_SIZE_RECORDS) {
            // upload
            flush()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
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

    // only calls this on force complete
    override suspend fun finish() {
        flush()
    }

    // this is always called on complete
    override fun close() {}

    object Constants {
        const val BATCH_SIZE_RECORDS = 500000
    }

    /**
     * Naive wrapper class to having to copy the buffer contents around.
     */
    private class ClickHouseBinaryBuffer : ByteArrayOutputStream() {
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
