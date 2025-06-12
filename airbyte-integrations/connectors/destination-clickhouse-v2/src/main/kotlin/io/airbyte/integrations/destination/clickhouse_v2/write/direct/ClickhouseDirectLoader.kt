/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.RowBinaryFormatWriter
import com.clickhouse.client.api.metadata.TableSchema
import com.clickhouse.data.ClickHouseFormat
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.protobuf.value
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta as CDKConstants
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.cdk.load.util.write
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.Constants.DELIMITER
import io.airbyte.protocol.models.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
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
    private var buffer: ByteArrayOutputStream = ByteArrayOutputStream()
    private lateinit var schema: TableSchema
    private lateinit var writer: RowBinaryFormatWriter

    private fun init() {
        schema = clickhouseClient.getTableSchema(descriptor.name, descriptor.namespace ?: "default")
        writer = RowBinaryFormatWriter(buffer, schema, ClickHouseFormat.RowBinary)
    }

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        // we have to do this lazily because it depends on the table being created in the dest
        if (!this::writer.isInitialized) {
            init()
        }

        // TODO: validate and coerce data if necessary
        val meta = Jsons.jsonNode(record.rawData.sourceMeta) as ObjectNode
        meta.put(CDKConstants.AIRBYTE_META_SYNC_ID, record.stream.syncId)
        // add internal columns
        val protocolRecord = record.asJsonRecord() as ObjectNode

        record.schema.asColumns().forEach {
            val rawValue = protocolRecord[it.key]
            when (val coerced = rawValue.toAirbyteValue()) {
                is BooleanValue -> writer.setValue(it.key, coerced.value)
                is IntegerValue -> writer.setValue(it.key, coerced.value)
                is NumberValue -> writer.setValue(it.key, coerced.value)
                is StringValue -> writer.setValue(it.key, coerced.value)
                is ObjectValue -> writer.setValue(it.key, coerced.values.toString())
                is ArrayValue -> writer.setValue(it.key, coerced.values.toString())
                is NullValue -> writer.setValue(it.key, null)
                else -> {}
            }


//            writer.setValue(it.key, rawValue)
        }

        val ts = java.time.Instant.ofEpochMilli(record.rawData.emittedAtMs)

        writer.setValue(CDKConstants.COLUMN_NAME_AB_EXTRACTED_AT, ts)
        writer.setValue(CDKConstants.COLUMN_NAME_AB_GENERATION_ID, record.stream.generationId)
        writer.setValue(CDKConstants.COLUMN_NAME_AB_RAW_ID, record.airbyteRawId.toString())
        writer.setValue(CDKConstants.COLUMN_NAME_AB_META, meta)
        writer.commitRow()

        // serialize and buffer
//        buffer.write(protocolRecord.toString())
//        buffer.write(DELIMITER)

//        recordCount++

        // determine whether we're complete
        if (writer.rowCount >= Constants.BATCH_SIZE_RECORDS) {
            // upload
            flush()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
    }

    private suspend fun flush() {

        log.info { "Copying buffer for insert into ${descriptor.name}" }
        val bytes = ByteArrayInputStream(buffer.toByteArray())
//        buffer = ByteArrayOutputStream()

        log.info { "Beginning insert into ${descriptor.name}" }

        val insertResult =
            clickhouseClient
                .insert(
                    "`${descriptor.namespace ?: "default"}`.`${descriptor.name}`",
                    bytes,
                    ClickHouseFormat.RowBinary
//                    bytes,
//                    ClickHouseFormat.JSONEachRow,
                )
                .await()

        log.info { "Finished insert of ${insertResult.writtenRows} rows into ${descriptor.name}" }
//        recordCount = 0
    }

    // only calls this on force complete
    override suspend fun finish() {
        flush()
    }

    // this is always called on complete
    override fun close() {}

    object Constants {
        const val BATCH_SIZE_RECORDS = 500000
        const val DELIMITER = "\n"
    }
}
