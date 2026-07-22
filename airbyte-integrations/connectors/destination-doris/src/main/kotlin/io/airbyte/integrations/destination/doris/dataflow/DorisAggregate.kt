/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.dataflow

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
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.doris.write.DorisStreamLoadClient
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import java.io.ByteArrayOutputStream
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

private val log = KotlinLogging.logger {}
private val DORIS_DATETIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS")

/**
 * Accumulates records as newline-delimited JSON (JSON lines) and flushes them to Doris via Stream
 * Load.
 */
class DorisAggregate(
    private val database: String,
    private val table: String,
    private val streamLoadClient: DorisStreamLoadClient,
) : Aggregate {

    private val buffer = ByteArrayOutputStream()
    private var recordCount = 0

    override fun accept(record: RecordDTO) {
        val jsonMap = linkedMapOf<String, Any?>()
        for ((fieldName, fieldValue) in record.fields) {
            jsonMap[fieldName] = toJsonValue(fieldName, fieldValue)
        }

        val jsonBytes = Jsons.writeValueAsBytes(jsonMap)
        if (recordCount > 0) {
            buffer.write('\n'.code)
        }
        buffer.write(jsonBytes)
        recordCount++
    }

    override suspend fun flush() {
        if (recordCount == 0) {
            return
        }

        log.info { "Flushing $recordCount records (${buffer.size()} bytes) to $database.$table" }
        streamLoadClient.streamLoad(database, table, buffer.toByteArray())
        buffer.reset()
        recordCount = 0
    }

    /**
     * Convert AirbyteValue to a JSON-compatible value.
     *
     * Special handling for Airbyte internal columns:
     * - _airbyte_meta: ObjectValue must be serialized to JSON string (Doris column is STRING)
     * - _airbyte_extracted_at: IntegerValue (epoch millis) is passed as-is (Doris handles it)
     * - ObjectValue/ArrayValue: serialized to JSON string for STRING columns, or kept as nested
     * structure for JSON columns
     */
    private fun toJsonValue(fieldName: String, value: AirbyteValue): Any? {
        return when (value) {
            is NullValue -> null
            is StringValue -> value.value
            is BooleanValue -> value.value
            is IntegerValue -> value.value
            is NumberValue -> value.value
            is DateValue -> value.value.toString()
            is TimestampWithTimezoneValue -> {
                // Convert to UTC and format without timezone suffix for Doris DATETIME
                val utcDateTime =
                    value.value.withOffsetSameInstant(ZoneOffset.UTC).toLocalDateTime()
                utcDateTime.format(DORIS_DATETIME_FORMATTER)
            }
            is TimestampWithoutTimezoneValue -> value.value.format(DORIS_DATETIME_FORMATTER)
            is TimeWithTimezoneValue -> value.value.toString()
            is TimeWithoutTimezoneValue -> value.value.toString()
            is ObjectValue -> {
                if (fieldName == Meta.COLUMN_NAME_AB_META) {
                    // _airbyte_meta is stored as STRING in Doris, serialize to JSON string
                    value.values.serializeToString()
                } else {
                    // For JSON columns, keep as nested map
                    value.values.mapValues { (_, v) -> toJsonValue("", v) }
                }
            }
            is ArrayValue -> {
                // For JSON columns, keep as list
                value.values.map { toJsonValue("", it) }
            }
        }
    }
}

@Factory
class DorisAggregateFactory(
    private val streamLoadClient: DorisStreamLoadClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        return DorisAggregate(
            database = tableName.namespace,
            table = tableName.name,
            streamLoadClient = streamLoadClient,
        )
    }
}
