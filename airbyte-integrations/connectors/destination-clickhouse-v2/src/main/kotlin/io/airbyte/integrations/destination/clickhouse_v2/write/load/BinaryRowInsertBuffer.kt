/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.load

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.RowBinaryFormatWriter
import com.clickhouse.client.api.metadata.TableSchema
import com.clickhouse.data.ClickHouseFormat
import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.clickhouse_v2.config.toClickHouseCompatibleName
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
    justification = "suspend and fb's non-null analysis don't play well",
)
class BinaryRowInsertBuffer(
    val tableName: TableName,
    private val clickhouseClient: Client,
    airbyteSchema: AirbyteType
) {
    // Initialize the inner buffer
    private val schema: TableSchema =
        clickhouseClient.getTableSchema(tableName.name, tableName.namespace)
    @VisibleForTesting internal var inner = InputOutputBuffer()
    @VisibleForTesting
    internal var writer = RowBinaryFormatWriter(inner, schema, ClickHouseFormat.RowBinary)

    @VisibleForTesting
    internal var formattedSchema: Map<String, FieldType> =
        airbyteSchema.asColumns().mapKeys { (k, _) -> k.toClickHouseCompatibleName() }

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        recordFields.forEach {
            val airbyteType: AirbyteType =
                if (COLUMN_NAMES.contains(it.key)) {
                    when (it.key) {
                        Meta.COLUMN_NAME_AB_RAW_ID -> StringType
                        Meta.COLUMN_NAME_AB_META -> StringType
                        Meta.COLUMN_NAME_AB_EXTRACTED_AT -> DateType
                        Meta.COLUMN_NAME_AB_GENERATION_ID -> IntegerType
                        else -> // Unreachable
                        StringType
                    }
                } else {
                    formattedSchema[it.key]!!.type
                }
            writeAirbyteValue(it.key, it.value, airbyteType)
        }

        writer.commitRow()
    }

    suspend fun flush() {
        log.info { "Beginning insert into ${tableName.name}" }

        val insertResult =
            clickhouseClient
                .insert(
                    "`${tableName.namespace}`.`${tableName.name}`",
                    inner.toInputStream(),
                    ClickHouseFormat.RowBinary,
                )
                .await()

        log.info { "Finished insert of ${insertResult.writtenRows} rows into ${tableName.name}" }
    }

    internal fun writeAirbyteValue(
        columnName: String,
        abValue: AirbyteValue,
        dataType: AirbyteType,
    ) {
        when (abValue) {
            // TODO: let's consider refactoring AirbyteValue so we don't have to do this
            is NullValue -> writer.setValue(columnName, null)
            is ObjectValue -> writer.setValue(columnName, abValue.values.serializeToString())
            is ArrayValue -> writer.setValue(columnName, abValue.values.serializeToString())
            is BooleanValue ->
                write(columnName, abValue.value, dataType is BooleanType || dataType is UnknownType)
            is IntegerValue ->
                write(columnName, abValue.value, dataType is IntegerType || dataType is UnknownType)
            is NumberValue ->
                write(columnName, abValue.value, dataType is NumberType || dataType is UnknownType)
            is StringValue ->
                write(columnName, abValue.value, dataType is StringType || dataType is UnknownType)
            is DateValue ->
                write(columnName, abValue.value, dataType is DateType || dataType is UnknownType)
            is TimeWithTimezoneValue ->
                write(
                    columnName,
                    abValue.value,
                    dataType is TimeTypeWithTimezone ||
                        dataType is DateType ||
                        dataType is UnknownType
                )
            is TimeWithoutTimezoneValue ->
                write(
                    columnName,
                    abValue.value,
                    dataType is TimeTypeWithoutTimezone ||
                        dataType is DateType ||
                        dataType is UnknownType
                )
            is TimestampWithTimezoneValue ->
                write(
                    columnName,
                    abValue.value,
                    dataType is TimestampTypeWithTimezone ||
                        dataType is DateType ||
                        dataType is UnknownType
                )
            is TimestampWithoutTimezoneValue ->
                write(
                    columnName,
                    abValue.value,
                    dataType is TimestampTypeWithoutTimezone ||
                        dataType is DateType ||
                        dataType is UnknownType
                )
        }
    }

    internal fun <V> write(columnName: String, value: V, matchType: Boolean) {
        if (matchType) {
            writer.setValue(columnName, value)
        } else {
            writer.setValue(columnName, value.serializeToString())
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
