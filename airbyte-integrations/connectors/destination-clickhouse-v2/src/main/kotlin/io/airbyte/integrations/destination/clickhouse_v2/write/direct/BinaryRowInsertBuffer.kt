/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.RowBinaryFormatWriter
import com.clickhouse.data.ClickHouseFormat
import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
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
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import kotlinx.coroutines.future.await

private val log = KotlinLogging.logger {}

/*
 * Encapsulates ClickHouse specific buffering and writing logic separate from the loader
 * state machine.
 */
@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class BinaryRowInsertBuffer(
    val tableName: TableName,
    private val clickhouseClient: Client,
) {
    // Initialize the inner buffer
    private val schema = clickhouseClient.getTableSchema(tableName.name, tableName.namespace)
    @VisibleForTesting internal var inner = InputOutputBuffer()
    @VisibleForTesting
    internal var writer = RowBinaryFormatWriter(inner, schema, ClickHouseFormat.RowBinary)

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        recordFields.forEach { writeAirbyteValue(it.key, it.value) }

        writer.commitRow()
    }

    suspend fun flush() {
        log.info { "Beginning insert into ${tableName.name}" }

        val insertResult =
            clickhouseClient
                .insert(
                    "`${tableName.namespace}`.`${tableName.name}`",
                    inner.toInputStream(),
                    ClickHouseFormat.RowBinary
                )
                .await()

        log.info { "Finished insert of ${insertResult.writtenRows} rows into ${tableName.name}" }
    }

    private fun writeAirbyteValue(columnName: String, abValue: AirbyteValue) {
        when (abValue) {
            // TODO: let's consider refactoring AirbyteValue so we don't have to do this
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

    /**
     * The CH writer wants an output stream and the client an input stream. This is a naive wrapper
     * class to avoid having to copy the buffer contents around.
     */
    internal class InputOutputBuffer : ByteArrayOutputStream() {
        /**
         * Get an input stream based on the contents of this output stream. Do not use the output
         * stream after calling this method.
         * @return an {@link InputStream}
         */
        fun toInputStream(): ByteArrayInputStream {
            return ByteArrayInputStream(this.buf, 0, this.count)
        }
    }
}
